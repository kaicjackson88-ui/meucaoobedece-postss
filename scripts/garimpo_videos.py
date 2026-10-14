"""Garimpa vídeos de cães no Mixkit (licença gratuita com uso comercial e em anúncios),
filtra os que mostram comportamentos do nosso nicho, baixa prévias e monta:
- garimpo/prancha_N.jpg (miniaturas numeradas)
- garimpo/compilado.mp4 (3 s de cada candidato, com o número na tela)
- garimpo/lista.md (número, título, link, licença, categoria)
Uso: python scripts/garimpo_videos.py"""
import json, re, subprocess, time, urllib.request
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[1]
OUT = RAIZ / 'garimpo'; OUT.mkdir(exist_ok=True)
TMP = Path('/tmp/garimpo'); TMP.mkdir(exist_ok=True)
UA = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126 Safari/537.36'}

PAGINAS = [f'https://mixkit.co/free-stock-video/dog/?page={i}' for i in range(1, 21)]
PAGINAS += [f'https://mixkit.co/free-stock-video/{s}/' for s in
            ['dog-barking', 'dogs-barking', 'puppy', 'puppies', 'dog-walking', 'dog-training', 'pet', 'pets', 'dog-playing', 'leash']]

CATEG = [  # (categoria, palavras no título) — a primeira que bater vale
    ('latindo', ['bark', 'howl', 'growl', 'angry', 'aggress', 'enraged']),
    ('guia/passeio', ['leash', 'walking', 'walks', 'walk ']),
    ('roendo/bagunca', ['chew', 'bite', 'biting', 'destroy', 'mess', 'shoe', 'sofa', 'couch', 'pillow', 'tear']),
    ('pulando/agitado', ['jump', 'excite', 'running', 'runs', 'playing', 'plays']),
    ('filhote', ['puppy', 'puppies']),
    ('treino/comando', ['train', 'command', 'sit', 'treat', 'trick', 'paw', 'obedien', 'hand']),
    ('casa', ['home', 'house', 'room', 'floor', 'bed', 'carpet', 'rug', 'kitchen', 'door', 'window', 'apartment']),
    ('tutor e cao', ['owner', 'woman', 'man ', 'girl', 'boy', 'family', 'couple', 'petting', 'hug']),
]


def get(url, tent=3):
    for t in range(tent):
        try:
            with urllib.request.urlopen(urllib.request.Request(url, headers=UA), timeout=30) as r:
                return r.read()
        except Exception as e:  # noqa: BLE001
            print('  falhou', url, str(e)[:60]); time.sleep(3 * (t + 1))
    return b''


def coletar():
    vistos = {}
    for url in PAGINAS:
        html = get(url).decode('utf-8', 'ignore')
        for m in re.finditer(r'href="(/free-stock-video/([a-z0-9-]+)-(\d+)/)"', html):
            caminho, slug, vid = m.groups()
            if vid in vistos:
                continue
            vistos[vid] = {'id': vid, 'titulo': slug.replace('-', ' '), 'pagina': 'https://mixkit.co' + caminho}
        time.sleep(1)
    print('vídeos encontrados:', len(vistos))
    return list(vistos.values())


def categoria(t):
    t = ' ' + t.lower() + ' '
    if not any(k in t for k in ('dog', 'puppy', 'puppies', 'canine', 'pet')):
        return None
    for nome, chaves in CATEG:
        if any(k in t for k in chaves):
            return nome
    return None


def licenca(pagina):
    html = get(pagina).decode('utf-8', 'ignore').lower()
    if 'restricted license' in html and 'free license' not in html:
        return 'Restrita (NAO usar)'
    if 'free license' in html:
        return 'Gratuita (uso comercial e anuncio ok)'
    return 'conferir'


def main():
    todos = coletar()
    cand = []
    for v in todos:
        c = categoria(v['titulo'])
        if c:
            v['cat'] = c; cand.append(v)
    ordem = [c for c, _ in CATEG]
    cand.sort(key=lambda v: ordem.index(v['cat']))
    lim = {'filhote': 8, 'tutor e cao': 8, 'casa': 10, 'pulando/agitado': 10}
    cont, final = {}, []
    for v in cand:
        cont[v['cat']] = cont.get(v['cat'], 0) + 1
        if cont[v['cat']] <= lim.get(v['cat'], 99):
            final.append(v)
    final = final[:48]
    print('candidatos:', len(final))
    ok = []
    for v in final:
        arq = TMP / f"{v['id']}.mp4"
        dados = get(f"https://assets.mixkit.co/videos/{v['id']}/{v['id']}-360.mp4")
        if len(dados) < 20000:
            print('  sem prévia', v['id']); continue
        arq.write_bytes(dados)
        v['licenca'] = licenca(v['pagina'])
        dur = subprocess.run(['ffprobe', '-v', 'error', '-show_entries', 'format=duration', '-of', 'csv=p=0', str(arq)], capture_output=True, text=True).stdout.strip()
        wh = subprocess.run(['ffprobe', '-v', 'error', '-select_streams', 'v:0', '-show_entries', 'stream=width,height', '-of', 'csv=p=0', str(arq)], capture_output=True, text=True).stdout.strip()
        try:
            v['dur'] = round(float(dur), 1)
        except ValueError:
            v['dur'] = 0
        try:
            w, h = map(int, wh.split(',')[:2]); v['formato'] = 'vertical' if h > w else 'horizontal'
        except ValueError:
            v['formato'] = '?'
        v['arq'] = str(arq); ok.append(v)
    for n, v in enumerate(ok, 1):
        v['n'] = n
    thumbs = []
    for v in ok:
        th = TMP / f"t{v['n']}.jpg"
        meio = max(0.5, v['dur'] / 2)
        subprocess.run(['ffmpeg', '-y', '-v', 'error', '-ss', str(meio), '-i', v['arq'], '-frames:v', '1', '-vf',
                        "scale=480:270:force_original_aspect_ratio=decrease,pad=480:270:(ow-iw)/2:(oh-ih)/2:color=black,"
                        f"drawbox=x=0:y=0:w=74:h=46:color=black@0.75:t=fill,drawtext=text='{v['n']}':x=12:y=6:fontsize=34:fontcolor=yellow,"
                        f"drawbox=x=0:y=236:w=480:h=34:color=black@0.6:t=fill,drawtext=text='{v['cat']}':x=10:y=242:fontsize=20:fontcolor=white",
                        str(th)], check=False)
        if th.exists():
            thumbs.append(th)
    for p in range(0, len(thumbs), 12):
        grupo = thumbs[p:p + 12]
        entradas = []
        for t in grupo:
            entradas += ['-i', str(t)]
        n = len(grupo); cols = 3
        layout = '|'.join(f'{(k % cols) * 480}_{(k // cols) * 270}' for k in range(n))
        filtro = f"xstack=inputs={n}:layout={layout}:fill=black" if n > 1 else 'null'
        subprocess.run(['ffmpeg', '-y', '-v', 'error', *entradas, '-filter_complex', filtro, '-frames:v', '1', '-q:v', '3', str(OUT / f'prancha_{p // 12 + 1}.jpg')], check=False)
    partes = []
    for v in ok:
        pt = TMP / f"c{v['n']}.mp4"; ini = max(0, v['dur'] / 2 - 1.5)
        subprocess.run(['ffmpeg', '-y', '-v', 'error', '-ss', str(ini), '-t', '3', '-i', v['arq'], '-an', '-vf',
                        "scale=640:360:force_original_aspect_ratio=decrease,pad=640:360:(ow-iw)/2:(oh-ih)/2:color=black,fps=30,"
                        f"drawbox=x=0:y=0:w=110:h=60:color=black@0.75:t=fill,drawtext=text='{v['n']}':x=16:y=8:fontsize=44:fontcolor=yellow,"
                        f"drawtext=text='{v['cat']}':x=126:y=18:fontsize=24:fontcolor=white:box=1:boxcolor=black@0.6:boxborderw=6",
                        '-c:v', 'libx264', '-crf', '30', '-preset', 'veryfast', '-pix_fmt', 'yuv420p', str(pt)], check=False)
        if pt.exists():
            partes.append(pt)
    (TMP / 'lista.txt').write_text(''.join(f"file '{p}'\n" for p in partes))
    subprocess.run(['ffmpeg', '-y', '-v', 'error', '-f', 'concat', '-safe', '0', '-i', str(TMP / 'lista.txt'), '-c', 'copy', str(OUT / 'compilado.mp4')], check=False)
    linhas = ['# Garimpo de vídeos — Mixkit', '', 'Licença gratuita do Mixkit: uso comercial e em anúncios online, sem crédito obrigatório.', '',
              '| Nº | Categoria | Título (original) | Duração | Formato | Licença | Página |', '| --- | --- | --- | --- | --- | --- | --- |']
    for v in ok:
        linhas.append(f"| {v['n']} | {v['cat']} | {v['titulo']} | {v['dur']} s | {v['formato']} | {v['licenca']} | {v['pagina']} |")
    (OUT / 'lista.md').write_text('\n'.join(linhas) + '\n', encoding='utf-8')
    (OUT / 'candidatos.json').write_text(json.dumps([{k: v[k] for k in ('n', 'id', 'titulo', 'cat', 'dur', 'formato', 'licenca', 'pagina')} for v in ok], ensure_ascii=False, indent=1), encoding='utf-8')
    print('prontos:', len(ok))


if __name__ == '__main__':
    main()
