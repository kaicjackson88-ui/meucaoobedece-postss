"""Garimpa músicas do Mixkit com licença gratuita (uso comercial e em anúncios online, sem crédito),
nos estilos que combinam com o criativo (ukulele, alegre, brincalhão), baixa e deixa cifradas em musicas/.
O repositório é público e a licença não deixa distribuir o arquivo cru, por isso cifra igual aos vídeos.
Uso: python scripts/garimpo_musica.py   (LIMITE=quantas músicas, padrão 24)"""
import json, os, re, sys, time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import garimpo_videos as gv  # noqa: E402
from baixar_escolhidos import cifrar  # noqa: E402

RAIZ = Path(__file__).resolve().parents[1]
OUT = RAIZ / 'musicas'
PAGINAS = [
    'https://mixkit.co/free-stock-music/tag/ukulele/',
    'https://mixkit.co/free-stock-music/mood/playful/',
    'https://mixkit.co/free-stock-music/mood/happy/',
    'https://mixkit.co/free-stock-music/tag/happy/',
]
LIMITE = int(os.environ.get('LIMITE', '24'))


def coletar():
    vistos = {}
    for url in PAGINAS:
        html = gv.get(url).decode('utf-8', 'ignore')
        if not vistos:  # cópia da 1ª página para depurar a estrutura (só texto do site, sem áudio)
            (OUT / 'pagina_exemplo.html').write_text(html[:400000], encoding='utf-8')
        for m in re.finditer(r'href="(/free-stock-music/([a-z0-9-]+)-(\d+)/)"', html):
            caminho, slug, mid = m.groups()
            if mid not in vistos:
                vistos[mid] = {'id': mid, 'titulo': slug.replace('-', ' '), 'pagina': 'https://mixkit.co' + caminho, 'origem': url.split('/')[-2]}
        # a listagem de músicas não tem link por faixa: pega o áudio direto (licença gratuita é a da página)
        for u in dict.fromkeys(re.findall(r'https://assets\.mixkit\.co/[^"\'\s]+?\.mp3', html)):
            mm = re.search(r'(?:mixkit-)?([a-z0-9-]*?)-?(\d+)\.mp3$', u)
            if not mm:
                continue
            mid = mm.group(2)
            if mid not in vistos:
                vistos[mid] = {'id': mid, 'titulo': (mm.group(1) or mid).replace('-', ' '), 'pagina': url, 'origem': url.split('/')[-2], 'mp3': u}
        time.sleep(1)
    print('músicas encontradas:', len(vistos))
    return list(vistos.values())


def mp3_da_pagina(m):
    if m.get('mp3'):
        return [m['mp3'], f"https://assets.mixkit.co/music/{m['id']}/{m['id']}.mp3"], 'Gratuita (listagem do Mixkit License)'
    html = gv.get(m['pagina']).decode('utf-8', 'ignore')
    low = html.lower()
    if 'restricted license' in low and 'free license' not in low:
        return None, 'Restrita (NAO usar)'
    lic = 'Gratuita (uso comercial e anuncio ok)' if 'free license' in low else 'conferir'
    urls = re.findall(r'https://assets\.mixkit\.co/[^"\'\s]+?\.mp3', html)
    urls = [u for u in dict.fromkeys(urls) if f"/{m['id']}" in u or f"-{m['id']}." in u] or urls[:1]
    urls.append(f"https://assets.mixkit.co/music/{m['id']}/{m['id']}.mp3")
    return urls, lic


def parece_mp3(dados):
    return len(dados) > 50000 and (dados[:3] == b'ID3' or dados[0] == 0xFF)


def main():
    OUT.mkdir(exist_ok=True)
    feitos = []
    for m in coletar():
        if len(feitos) >= LIMITE:
            break
        urls, lic = mp3_da_pagina(m)
        if not urls:
            print('  pulei (licença restrita):', m['titulo']); continue
        nome = f"mx{m['id']}.mp3"
        arq = gv.TMP / nome
        for u in urls:
            dados = gv.get(u)
            if parece_mp3(dados):
                arq.write_bytes(dados); m['url'] = u; break
        else:
            print('  não baixou', m['titulo']); continue
        dur = gv.medir(arq)['dur']
        feitos.append(m | {'licenca': lic, 'dur': dur, 'arquivo': nome})
        cifrar(arq, OUT / nome)
        print('  ok', nome, m['titulo'], dur, lic)
        time.sleep(1)
    (OUT / 'lista.json').write_text(json.dumps(feitos, ensure_ascii=False, indent=1), encoding='utf-8')
    print('baixadas:', len(feitos))
    if not feitos:
        sys.exit(1)


if __name__ == '__main__':
    main()
