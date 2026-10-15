"""Cães reais no lugar do mascote desenhado, sem perder a cara da marca.
Cada humor do mascote (bravo, feliz, normal, dorminhoco, lendario) vira um "cartão de foto" da marca:
moldura creme, contorno tinta e sombra dura (o mesmo estilo dos balões e botões), com um cão de verdade dentro.
- Reels: trechos de vídeo do Pixabay viram quadros (12 por segundo) e o motor troca o quadro a cada frame.
- Carrosséis: uma foto por humor (o "bravo" usa um quadro do vídeo de latido).
Os IDs vêm de reels/midia_real.json (todos conferidos a olho). Qualquer erro devolve {} e o post sai com o mascote.
Precisa do segredo PIXABAY_API_KEY."""
import base64, io, json, random, subprocess, sys, tempfile, urllib.parse, urllib.request
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

RAIZ = Path(__file__).resolve().parents[1]
POOL = RAIZ / 'reels' / 'midia_real.json'
CW, CH = 440, 564          # mesma proporção do mascote (220:282)
TINTA, CREME = (42, 38, 34, 255), (253, 247, 238, 255)
HUMORES = ['bravo', 'feliz', 'normal', 'dorminhoco', 'lendario']


def config():
    try:
        return json.loads(POOL.read_text(encoding='utf-8'))
    except Exception:  # noqa: BLE001
        return {'ativo': False}


def pular():
    return config().get('pular_tipos', ['historia', 'chat'])


def _get(url):
    with urllib.request.urlopen(urllib.request.Request(url, headers={'User-Agent': 'meu-cao-obedece/1.0'}), timeout=40) as r:
        return r.read()


def _hit(endpoint, pid):
    import garimpo_pixabay as gp
    q = urllib.parse.urlencode({'key': gp.CHAVE, 'id': pid})
    hits = json.loads(_get(f'https://pixabay.com/api/{endpoint}?{q}').decode('utf-8')).get('hits', [])
    return hits[0] if hits else None


def cartao(im):
    """Foto (PIL) → cartão RGBA da marca, desenhado em 2x e reduzido para bordas lisas."""
    from PIL import Image, ImageDraw, ImageOps
    k = 2
    W, H = CW * k, CH * k
    card = Image.new('RGBA', (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(card)
    x0, y0, w, h = 6 * k, 6 * k, (CW - 22) * k, (CH - 46) * k
    d.rounded_rectangle([x0 + 12 * k, y0 + 12 * k, x0 + w + 12 * k, y0 + h + 12 * k], 38 * k, fill=TINTA)   # sombra dura
    d.rounded_rectangle([x0, y0, x0 + w, y0 + h], 38 * k, fill=CREME, outline=TINTA, width=7 * k)
    m = 20 * k
    pw, ph = w - 2 * m, h - 2 * m
    foto = ImageOps.fit(im.convert('RGB'), (pw, ph), Image.LANCZOS, centering=(0.5, 0.42))
    mask = Image.new('L', (pw, ph), 0)
    ImageDraw.Draw(mask).rounded_rectangle([0, 0, pw - 1, ph - 1], 26 * k, fill=255)
    card.paste(foto, (x0 + m, y0 + m), mask)
    return card.resize((CW, CH), Image.LANCZOS)


def _quadros_video(vid, segundos, fps, pasta, inicio=1.0):
    """Baixa o vídeo (≈540p) e devolve a lista de quadros PIL."""
    from PIL import Image
    import garimpo_pixabay as gp
    h = _hit('videos/', vid)
    url = gp.arquivo(h, 540) if h else None
    if not url:
        return []
    mp4 = Path(pasta) / f'v{vid}.mp4'
    mp4.write_bytes(_get(url))
    saida = Path(pasta) / f'q{vid}'
    saida.mkdir(exist_ok=True)
    subprocess.run(['ffmpeg', '-y', '-v', 'error', '-ss', str(inicio), '-i', str(mp4), '-t', str(segundos),
                    '-vf', f'fps={fps},scale=-2:600', str(saida / '%03d.jpg')], check=True)
    mp4.unlink(missing_ok=True)
    return [Image.open(p).copy() for p in sorted(saida.glob('*.jpg'))]


def _foto(pid):
    from PIL import Image
    h = _hit('', pid)
    if not h:
        return None
    return Image.open(io.BytesIO(_get(h.get('largeImageURL') or h['webformatURL'])))


def preparar_reel(roteiro, seed, pasta):
    """Grava pasta/{humor}_{000}.png para cada humor e devolve {humor: nº de quadros}. {} se desligado ou erro."""
    cfg = config()
    if not cfg.get('ativo'):
        return {}
    tipos = {c.get('tipo') for c in roteiro.get('cenas', [])}
    if tipos and tipos <= set(cfg.get('pular_tipos', [])):
        return {}
    pasta = Path(pasta); pasta.mkdir(parents=True, exist_ok=True)
    rnd = random.Random(seed)
    tmp = Path(tempfile.mkdtemp(prefix='real-'))
    out = {}
    if tipos & {'historia', 'chat'} and cfg.get('historia'):
        return _reel_historia(cfg, rnd, tmp, pasta)
    for humor in HUMORES:
        try:
            quadros = []
            vids = cfg.get('videos', {}).get(humor) or []
            if vids:
                quadros = _quadros_video(rnd.choice(vids), cfg.get('segundos', 4), cfg.get('fps', 12), tmp, inicio=rnd.choice([0.5, 1.0, 2.0]))
            if not quadros:
                fotos = cfg.get('fotos', {}).get(humor) or []
                f = _foto(rnd.choice(fotos)) if fotos else None
                quadros = [f] if f else []
            for i, q in enumerate(quadros):
                cartao(q).save(pasta / f'{humor}_{i:03d}.png')
            if quadros:
                out[humor] = len(quadros)
                print(f'  cão real "{humor}": {len(quadros)} quadro(s)', flush=True)
        except Exception as e:  # noqa: BLE001
            print(f'  cão real "{humor}" falhou ({str(e)[:80]}); fica o mascote', flush=True)
    return out


def _reel_historia(cfg, rnd, tmp, pasta):
    """História: o mesmo cão (só cão, sem pessoas) em todos os humores, pra não trocar de raça no meio."""
    h = cfg['historia']
    itens = [('v', i) for i in h.get('videos', [])] + [('f', i) for i in h.get('fotos', [])]
    rnd.shuffle(itens)
    for tipo, pid in itens:
        try:
            if tipo == 'v':
                quadros = _quadros_video(pid, cfg.get('segundos', 4), cfg.get('fps', 12), tmp, inicio=1.0)
            else:
                f = _foto(pid); quadros = [f] if f else []
            if not quadros:
                continue
            for i, q in enumerate(quadros):
                cartao(q).save(Path(pasta) / f'normal_{i:03d}.png')
            for humor in HUMORES:
                if humor != 'normal':
                    for i in range(len(quadros)):
                        (Path(pasta) / f'{humor}_{i:03d}.png').write_bytes((Path(pasta) / f'normal_{i:03d}.png').read_bytes())
            print(f'  história: o mesmo cão real ({tipo}{pid}) em todas as cenas, {len(quadros)} quadro(s)', flush=True)
            return {humor: len(quadros) for humor in HUMORES}
        except Exception as e:  # noqa: BLE001
            print(f'  história: {tipo}{pid} falhou ({str(e)[:80]})', flush=True)
    return {}


def preparar_carrossel(seed):
    """{humor: dataURL PNG do cartão} para a fábrica de carrosséis. {} se desligado ou erro."""
    cfg = config()
    if not cfg.get('ativo'):
        return {}
    rnd = random.Random(seed)
    tmp = Path(tempfile.mkdtemp(prefix='realc-'))
    out = {}
    for humor in HUMORES:
        try:
            fotos = cfg.get('fotos', {}).get(humor) or []
            im = _foto(rnd.choice(fotos)) if fotos else None
            if im is None and cfg.get('videos', {}).get(humor):
                q = _quadros_video(rnd.choice(cfg['videos'][humor]), 0.2, 5, tmp, inicio=1.5)
                im = q[0] if q else None
            if im is None:
                continue
            buf = io.BytesIO(); cartao(im).save(buf, 'PNG')
            out[humor] = 'data:image/png;base64,' + base64.b64encode(buf.getvalue()).decode('ascii')
            print(f'  cão real "{humor}" pronto', flush=True)
        except Exception as e:  # noqa: BLE001
            print(f'  cão real "{humor}" falhou ({str(e)[:80]}); fica o mascote', flush=True)
    return out


if __name__ == '__main__':  # teste: python scripts/midia_real.py <pasta>
    p = Path(sys.argv[1] if len(sys.argv) > 1 else 'teste_real')
    print(preparar_reel({'cenas': [{'tipo': 'gancho'}]}, 7, p))
    print({k: len(v) for k, v in preparar_carrossel(7).items()})
