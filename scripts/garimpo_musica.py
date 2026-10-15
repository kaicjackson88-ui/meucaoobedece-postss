"""Garimpa áudio do Mixkit com licença gratuita (uso comercial e em anúncios online, sem crédito)
e deixa cifrado em musicas/ — músicas (TIPO=musica, padrão) ou efeitos sonoros (TIPO=efeitos).
O repositório é público e a licença não deixa distribuir o arquivo cru, por isso cifra igual aos vídeos.
Nome e licença de cada faixa vêm do JSON-LD da listagem (cada item traz name, url e copyrightNotice).
Uso: TIPO=efeitos LIMITE=60 python scripts/garimpo_musica.py"""
import json, os, re, sys, time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import garimpo_videos as gv  # noqa: E402
from baixar_escolhidos import cifrar  # noqa: E402

RAIZ = Path(__file__).resolve().parents[1]
OUT = RAIZ / 'musicas'
TIPO = os.environ.get('TIPO', 'musica')
if TIPO == 'efeitos':
    PAGINAS = [f'https://mixkit.co/free-sound-effects/{s}/' for s in
               ('whoosh', 'swoosh', 'transition', 'pop', 'click', 'notification', 'bubble', 'coin', 'achievement')]
    POR_PAGINA = 10
else:
    PAGINAS = ['https://mixkit.co/free-stock-music/tag/ukulele/', 'https://mixkit.co/free-stock-music/mood/playful/',
               'https://mixkit.co/free-stock-music/mood/happy/', 'https://mixkit.co/free-stock-music/tag/happy/']
    POR_PAGINA = 99
LIMITE = int(os.environ.get('LIMITE') or ('60' if TIPO == 'efeitos' else '24'))
AUDIO = re.compile(r'https://assets\.mixkit\.co/[^"\'\s]+?\.(?:mp3|wav)')


def itens_ld(html):
    """Itens com áudio do JSON-LD da página: (nome, url, licença, gênero/tags)."""
    achados = []
    def andar(o):
        if isinstance(o, dict):
            u = o.get('url') or o.get('contentUrl') or ''
            if isinstance(u, str) and AUDIO.fullmatch(u):
                achados.append((o.get('name', ''), u, o.get('copyrightNotice', ''), o.get('genre', '')))
            for v in o.values():
                andar(v)
        elif isinstance(o, list):
            for v in o:
                andar(v)
    for bloco in re.findall(r'<script type="application/ld\+json">(.*?)</script>', html, re.S):
        try:
            andar(json.loads(bloco))
        except ValueError:
            pass
    return achados


def coletar():
    vistos = {}
    for url in PAGINAS:
        html = gv.get(url).decode('utf-8', 'ignore')
        origem = url.rstrip('/').split('/')[-1]
        itens = itens_ld(html)
        if not itens:  # sem JSON-LD: cai para os links soltos de áudio
            itens = [('', u, '', '') for u in dict.fromkeys(AUDIO.findall(html))]
        n = 0
        for nome, u, lic, genero in itens:
            mm = re.search(r'/(\d+)/[^/]*$', u) or re.search(r'(\d+)(?:-[a-z]+)?\.(?:mp3|wav)$', u)
            if not mm or mm.group(1) in vistos or n >= POR_PAGINA:
                continue
            if 'restricted' in lic.lower():
                print('  pulei (licença restrita):', nome); continue
            vistos[mm.group(1)] = {'id': mm.group(1), 'nome': nome, 'titulo': nome or mm.group(1), 'pagina': url,
                                   'origem': origem, 'genero': genero, 'licenca': lic or 'Mixkit License (listagem)', 'url': u}
            n += 1
        print(origem, len(itens), 'itens na página,', n, 'novos', '| ex.:', itens[0][1] if itens else '-')
        time.sleep(1)
    print('encontrados:', len(vistos))
    return list(vistos.values())


def parece_audio(dados):
    return len(dados) > 2000 and (dados[:3] == b'ID3' or dados[0] == 0xFF or dados[:4] == b'RIFF')


def main():
    OUT.mkdir(exist_ok=True)
    feitos = []
    for m in coletar():
        if len(feitos) >= LIMITE:
            break
        ext = m['url'].rsplit('.', 1)[-1]
        nome = f"mx{m['id']}.{ext}"
        arq = gv.TMP / nome
        dados = gv.get(m['url'])
        if not parece_audio(dados):
            print('  não baixou', m['titulo']); continue
        arq.write_bytes(dados)
        dur = gv.medir(arq)['dur']
        feitos.append(m | {'dur': dur, 'arquivo': nome})
        cifrar(arq, OUT / nome)
        print('  ok', nome, m['origem'], '|', m['titulo'], dur, '|', m['licenca'])
        time.sleep(0.5)
    (OUT / 'lista.json').write_text(json.dumps(feitos, ensure_ascii=False, indent=1), encoding='utf-8')
    print('baixados:', len(feitos))
    if not feitos:
        sys.exit(1)


if __name__ == '__main__':
    main()
