"""Gera a biblioteca de personagens e fundos no estilo 3D tipo Pixar (referência: arte/ref/estilo.jpg).
Usa o modelo de imagem do Gemini (GEMINI_API_KEY). Personagens saem em fundo branco e são recortados (rembg).
python arte/gerar_arte.py            -> gera o que falta
python arte/gerar_arte.py ana_base    -> gera só esses ids (refaz)"""
import base64, io, json, os, sys, time, urllib.request, urllib.error
from pathlib import Path

AQUI = Path(__file__).resolve().parent
BRUTO, PERS, FUNDOS = AQUI / 'bruto', AQUI / 'personagens', AQUI / 'fundos'
for p in (BRUTO, PERS, FUNDOS): p.mkdir(exist_ok=True)
CHAVE = os.environ.get('GEMINI_API_KEY', '').strip()
API = 'https://generativelanguage.googleapis.com/v1beta'

ESTILO = ('3D animated feature film style like Pixar/Disney: soft global illumination, warm cozy colors, subsurface skin, '
          'big expressive eyes, smooth stylized shapes, high detail, cinematic, 9:16 vertical. Same art style as the reference image.')
ANA = ('Ana: young Brazilian woman, late 20s, warm light-brown skin, long wavy dark-brown hair, friendly face, '
       'teal t-shirt with a small white paw print, blue jeans, white sneakers')
THOR = 'Thor: golden retriever puppy, fluffy golden fur, big shiny brown eyes, floppy ears, red collar'
BRANCO = 'Full body, centered, plain pure white background, no shadow on the floor, no text.'
ITENS = {
    'ana_base':      ('p', f'{ANA}. Standing relaxed, gentle smile, looking at the camera. {BRANCO}'),
    'ana_acena':     ('p', f'{ANA}. Waving hello with one hand, big happy smile. {BRANCO}'),
    'ana_surpresa':  ('p', f'{ANA}. Surprised, hands on her cheeks, mouth open, eyebrows up. {BRANCO}'),
    'ana_brava':     ('p', f'{ANA}. Frustrated, hands on hips, frowning (cartoon, not aggressive). {BRANCO}'),
    'ana_petisco':   ('p', f'{ANA}. Crouching slightly, holding a small dog treat forward, kind smile. {BRANCO}'),
    'thor_sentado':  ('p', f'{THOR}. Sitting obediently, looking up, attentive. {BRANCO}'),
    'thor_feliz':    ('p', f'{THOR}. Happy, tongue out, tail wagging, playful pose. {BRANCO}'),
    'thor_culpado':  ('p', f'{THOR}. Guilty look, ears down, eyes up, lying on the floor. {BRANCO}'),
    'fundo_sala':    ('f', 'Empty cozy living room, striped wallpaper, sofa, rug, plant, window with daylight. No people, no animals, no text. Eye-level camera, 9:16 vertical.'),
    'fundo_corredor': ('f', 'Empty apartment hallway with wooden floor, front door, coat hanger, warm light. No people, no animals, no text. Eye-level camera, 9:16 vertical.'),
}


def pedir(url, corpo=None, tent=4):
    for i in range(tent):
        try:
            req = urllib.request.Request(url, data=json.dumps(corpo).encode() if corpo else None, headers={'Content-Type': 'application/json'})
            with urllib.request.urlopen(req, timeout=180) as r:
                return json.load(r)
        except urllib.error.HTTPError as e:
            msg = e.read().decode('utf-8', 'replace')[:400]
            if e.code == 429 and ('limit: 0' in msg or 'quota' in msg.lower()):
                raise RuntimeError(f'SEM COTA (429): {msg}')
            if e.code in (429, 500, 503) and i < tent - 1:
                print(f'  aguardando ({e.code})…', flush=True); time.sleep(20 * (i + 1)); continue
            raise RuntimeError(f'HTTP {e.code}: {msg}')


def modelos_imagem():
    ms = pedir(f'{API}/models?pageSize=200&key={CHAVE}').get('models', [])
    nomes = [m['name'].split('/')[-1] for m in ms if 'image' in m['name'] and 'generateContent' in m.get('supportedGenerationMethods', [])]
    nomes.sort(key=lambda n: (0 if 'flash' in n else 1, 'preview' in n))
    print('Modelos de imagem:', nomes, flush=True)
    return nomes


def parte_img(caminho):
    return {'inline_data': {'mime_type': 'image/png' if caminho.suffix == '.png' else 'image/jpeg', 'data': base64.b64encode(caminho.read_bytes()).decode()}}


def gerar(modelo, texto, refs):
    partes = [parte_img(r) for r in refs] + [{'text': texto}]
    corpo = {'contents': [{'parts': partes}], 'generationConfig': {'responseModalities': ['IMAGE', 'TEXT'], 'imageConfig': {'aspectRatio': '9:16'}}}
    url = f'{API}/models/{modelo}:generateContent?key={CHAVE}'
    try:
        r = pedir(url, corpo)
    except RuntimeError as e:
        if 'HTTP 400' not in str(e): raise
        corpo['generationConfig'].pop('imageConfig'); r = pedir(url, corpo)
    for c in r.get('candidates', []):
        for p in c.get('content', {}).get('parts', []):
            d = p.get('inlineData') or p.get('inline_data')
            if d: return base64.b64decode(d['data'])
    raise RuntimeError('sem imagem na resposta: ' + json.dumps(r)[:300])


def recortar(png_bytes, destino):
    from rembg import remove
    from PIL import Image
    img = Image.open(io.BytesIO(remove(png_bytes))).convert('RGBA')
    bb = img.getbbox(); img = img.crop(bb) if bb else img
    img.save(destino)


def previa():
    from PIL import Image
    arqs = sorted(PERS.glob('*.png')) + sorted(FUNDOS.glob('*.png'))
    if not arqs: return
    W, H = 360, 640; cols = 5; linhas = (len(arqs) + cols - 1) // cols
    folha = Image.new('RGB', (W * cols, H * linhas), (235, 235, 235))
    for i, a in enumerate(arqs):
        im = Image.open(a).convert('RGBA'); im.thumbnail((W - 20, H - 20))
        x = (i % cols) * W + (W - im.width) // 2; y = (i // cols) * H + (H - im.height) // 2
        folha.paste(im, (x, y), im)
    folha.save(AQUI / 'previa.jpg', quality=85); print('Prévia:', AQUI / 'previa.jpg')


def main():
    if not CHAVE: sys.exit('sem GEMINI_API_KEY')
    pedidos = sys.argv[1:] or [k for k, (t, _) in ITENS.items() if not ((PERS if t == 'p' else FUNDOS) / f'{k}.png').exists()]
    # imagens feitas à mão (app Gemini/ChatGPT) colocadas em arte/bruto/<id>.png|jpg: só recorta
    for k in list(pedidos):
        feito = next((x for x in BRUTO.glob(f'{k}.*')), None)
        if feito:
            tipo = ITENS[k][0]; dados = feito.read_bytes()
            if tipo == 'p': recortar(dados, PERS / f'{k}.png')
            else:
                from PIL import Image
                Image.open(io.BytesIO(dados)).convert('RGB').save(FUNDOS / f'{k}.png')
            print(f'{k}: recortado da imagem enviada', flush=True); pedidos.remove(k)
    modelos = modelos_imagem() if pedidos else []
    if pedidos and not modelos: sys.exit('Nenhum modelo de imagem disponível para esta chave.')
    ref = AQUI / 'ref' / 'estilo.jpg'
    falhas, mortos, t0 = [], set(), time.time()
    for k in pedidos:
        if time.time() - t0 > 20 * 60: falhas.append(k); continue
        tipo, desc = ITENS[k]
        # referência de estilo + uma imagem já pronta do mesmo personagem (mantém o rosto igual)
        refs = [ref] + [x for x in [PERS / ('ana_base.png' if k.startswith('ana') else 'thor_sentado.png')] if x.exists() and x.stem != k][:1]
        texto = f'{ESTILO} {desc} Keep the character identical to the reference images.' if tipo == 'p' else f'{ESTILO} {desc}'
        for m in [x for x in modelos if x not in mortos]:
            try:
                print(f'{k}: gerando com {m}…', flush=True)
                dados = gerar(m, texto, refs)
                (BRUTO / f'{k}.png').write_bytes(dados)
                if tipo == 'p': recortar(dados, PERS / f'{k}.png')
                else:
                    from PIL import Image
                    Image.open(io.BytesIO(dados)).convert('RGB').save(FUNDOS / f'{k}.png')
                print(f'{k}: ok', flush=True); break
            except Exception as e:  # noqa: BLE001
                print(f'{k}: falhou em {m}: {e}', flush=True)
                if 'SEM COTA' in str(e) or 'HTTP 404' in str(e) or 'HTTP 403' in str(e): mortos.add(m)
        else:
            falhas.append(k)
        time.sleep(6)
    previa()
    print('FALHAS:', falhas or 'nenhuma')


if __name__ == '__main__':
    main()
