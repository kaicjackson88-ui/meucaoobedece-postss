"""Fábrica de Reels — Meu Cão Obedece.

Comandos:
  python scripts/reels.py produzir <roteiro_id|caminho.json> <pasta_saida> [--falso]
      gera narração, renderiza e mixa o vídeo (--falso = tempos simulados, sem voz; só para teste local)
  python scripts/reels.py postar [--forcar <roteiro_id>] [--teste]
      se algum horário de hoje já chegou e ainda não teve Reels, escolhe um roteiro, produz e posta
  python scripts/reels.py precisa
      imprime "sim" se há horário vencido sem Reels (para o workflow pular a instalação pesada)
"""
import asyncio, json, math, os, random, re, shutil, subprocess, sys, tempfile, time, unicodedata
from datetime import datetime, timedelta, timezone
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(RAIZ / 'scripts'))
BANCO = RAIZ / 'reels' / 'banco'
DADOS = RAIZ / 'dados'
MOTOR = RAIZ / 'motor'
CFG = json.loads((RAIZ / 'reels' / 'config.json').read_text(encoding='utf-8'))
BRT = timezone(timedelta(hours=-3))
REPO = os.environ.get('GITHUB_REPOSITORY', 'kaicjackson88-ui/meucaoobedece-postss')
FPS = 30


def ler_json(p, padrao):
    p = Path(p)
    return json.loads(p.read_text(encoding='utf-8')) if p.exists() else padrao


def gravar_json(p, obj):
    Path(p).parent.mkdir(parents=True, exist_ok=True)
    Path(p).write_text(json.dumps(obj, ensure_ascii=False, indent=1), encoding='utf-8')


def norm(s):
    s = unicodedata.normalize('NFD', s)
    return re.sub(r'[^a-z0-9]', '', ''.join(c for c in s if unicodedata.category(c) != 'Mn').lower())


def tokens(fala):
    return [w for w in re.findall(r"[\w]+", fala, flags=re.UNICODE)]


# ---------------- narração ----------------
async def _narrar(texto, mp3, voz, rate):
    import edge_tts
    com = edge_tts.Communicate(texto, voz, rate=rate, boundary='WordBoundary')
    pal = []
    with open(mp3, 'wb') as f:
        async for parte in com.stream():
            if parte['type'] == 'audio':
                f.write(parte['data'])
            elif parte['type'] == 'WordBoundary':
                pal.append({'palavra': parte['text'], 'inicio': round(parte['offset'] / 1e7, 3),
                            'fim': round((parte['offset'] + parte['duration']) / 1e7, 3)})
    return pal


def narrar(roteiro, pasta, falso=False):
    texto = ' '.join(c['fala'].strip() for c in roteiro['cenas'])
    mp3 = pasta / 'narracao.mp3'
    if falso:  # tempos simulados: 2,7 palavras/s com pausa entre frases
        pal, t = [], .1
        for c in roteiro['cenas']:
            for w in tokens(c['fala']):
                d = .12 + .05 * len(w)
                pal.append({'palavra': w, 'inicio': round(t, 3), 'fim': round(t + d, 3)}); t += d + .06
            t += .35
        subprocess.run(['ffmpeg', '-y', '-v', 'error', '-f', 'lavfi', '-i', f'anullsrc=r=44100:cl=mono', '-t', str(t + .5), str(mp3)], check=True)
        return pal
    voz = roteiro.get('voz') or CFG['voz']
    for tentativa in range(3):
        try:
            return asyncio.run(_narrar(texto, str(mp3), voz, CFG.get('velocidade', '+6%')))
        except Exception as e:  # serviço de voz instável: tenta de novo
            print('narração falhou, tentando de novo:', e); time.sleep(5)
    raise RuntimeError('Não consegui gerar a narração.')


def alinhar(roteiro, pal):
    """Descobre quais palavras narradas pertencem a cada cena."""
    esperadas = []
    for ci, c in enumerate(roteiro['cenas']):
        for w in tokens(c['fala']):
            esperadas.append((ci, norm(w)))
    cena_de = [None] * len(pal)
    j = 0
    for i, p in enumerate(pal):
        n = norm(p['palavra'])
        achou = None
        for k in range(j, min(j + 6, len(esperadas))):
            if esperadas[k][1] == n or (n and esperadas[k][1].startswith(n)) or (esperadas[k][1] and n.startswith(esperadas[k][1])):
                achou = k; break
        if achou is not None:
            cena_de[i] = esperadas[achou][0]; j = achou + 1
        else:
            cena_de[i] = esperadas[min(j, len(esperadas) - 1)][0] if esperadas else 0
    # garante monotonia
    for i in range(1, len(cena_de)):
        cena_de[i] = max(cena_de[i], cena_de[i - 1])
    out = []
    for ci in range(len(roteiro['cenas'])):
        idx = [i for i, c in enumerate(cena_de) if c == ci]
        if idx:
            out.append({'ini': pal[idx[0]]['inicio'], 'fim': pal[idx[-1]]['fim'], 'pal': idx})
        else:
            prev = out[-1]['fim'] if out else 0
            out.append({'ini': prev + .1, 'fim': prev + 1.5, 'pal': []})
    return out


# ---------------- render ----------------
async def _render(dados_js, mudo, capa):
    from playwright.async_api import async_playwright
    work = Path(tempfile.mkdtemp(prefix='motor-'))
    for f in MOTOR.iterdir():
        if f.is_dir(): shutil.copytree(f, work / f.name)
        else: shutil.copy(f, work / f.name)
    (work / 'dados.js').write_text(dados_js, encoding='utf-8')
    async with async_playwright() as p:
        kw = {}
        if Path('/opt/pw-browsers/chromium').exists(): kw['executable_path'] = '/opt/pw-browsers/chromium'
        b = await p.chromium.launch(**kw)
        pg = await b.new_page(viewport={'width': 1080, 'height': 1920})
        erros = []
        pg.on('pageerror', lambda e: erros.append(str(e)))
        await pg.goto((work / 'motor.html').as_uri())
        await pg.evaluate("Promise.all(['600 50px FR','700 50px FR','800 50px NU','900 50px NU'].map(x=>document.fonts.load(x))).then(()=>load())")
        if erros: raise RuntimeError('Erro no motor: ' + erros[0])
        info = await pg.evaluate('INFO()')
        await pg.evaluate('render(0)'); await pg.screenshot(path=str(capa), type='jpeg', quality=92)
        ff = subprocess.Popen(['ffmpeg', '-y', '-v', 'error', '-f', 'image2pipe', '-framerate', str(FPS), '-c:v', 'mjpeg', '-i', '-',
                               '-c:v', 'libx264', '-pix_fmt', 'yuv420p', '-crf', '20', '-preset', 'medium', str(mudo)], stdin=subprocess.PIPE)
        n = int(FPS * info['dur'])
        for i in range(n):
            await pg.evaluate(f'render({i / FPS})')
            ff.stdin.write(await pg.screenshot(type='jpeg', quality=90))
            if i % 300 == 0: print(f'  frame {i}/{n}', flush=True)
        ff.stdin.close(); ff.wait(); await b.close()
        if erros: raise RuntimeError('Erro no motor: ' + erros[0])
    shutil.rmtree(work, ignore_errors=True)
    return info


def produzir(roteiro, pasta, falso=False):
    import numpy as np
    from scipy.io import wavfile
    from reels_audio import gerar_sfx, gerar_musica, SR
    pasta = Path(pasta); pasta.mkdir(parents=True, exist_ok=True)
    print('Narração...', flush=True)
    pal = narrar(roteiro, pasta, falso)
    tempos = alinhar(roteiro, pal)
    seed = sum(map(ord, roteiro['id'] + roteiro.get('estilo', ''))) % 97
    rot = dict(roteiro); rot['seed'] = seed
    dados_js = 'const ROTEIRO=%s;\nconst PAL=%s;\nconst CENAS_T=%s;\n' % (json.dumps(rot, ensure_ascii=False), json.dumps(pal, ensure_ascii=False), json.dumps(tempos))
    print('Render...', flush=True)
    info = asyncio.run(_render(dados_js, pasta / 'mudo.mp4', pasta / 'capa.jpg'))
    dur = info['dur']
    print('Áudio...', flush=True)
    sfx = gerar_sfx(info['sfx'], dur, seed)
    mus = gerar_musica(dur, seed, info['cortes'])
    wavfile.write(pasta / 'sfx.wav', SR, (np.clip(sfx, -1, 1) * 32767).astype(np.int16))
    wavfile.write(pasta / 'musica.wav', SR, (np.clip(mus, -1, 1) * 32767).astype(np.int16))
    vol_voz = '0' if falso else '1.6'
    subprocess.run(['ffmpeg', '-y', '-v', 'error', '-i', str(pasta / 'mudo.mp4'), '-i', str(pasta / 'narracao.mp3'), '-i', str(pasta / 'musica.wav'), '-i', str(pasta / 'sfx.wav'),
                    '-filter_complex',
                    f'[1:a]aresample=44100,apad,highpass=f=80,acompressor=threshold=-18dB:ratio=3:attack=5:release=80,volume={vol_voz},asplit=2[v][vs];'
                    '[2:a]volume=0.5[m];[m][vs]sidechaincompress=threshold=0.03:ratio=8:attack=20:release=300[md];[3:a]volume=0.9[s];'
                    '[v][md][s]amix=inputs=3:normalize=0:duration=longest,alimiter=limit=0.95[a]',
                    '-map', '0:v', '-map', '[a]', '-c:v', 'libx264', '-crf', '21', '-preset', 'medium', '-pix_fmt', 'yuv420p', '-r', '30',
                    '-x264-params', 'keyint=60:open-gop=0', '-c:a', 'aac', '-b:a', '160k', '-ar', '44100', '-t', str(dur), '-movflags', '+faststart',
                    str(pasta / 'reel.mp4')], check=True)
    for f in ['mudo.mp4', 'sfx.wav', 'musica.wav']:
        (pasta / f).unlink(missing_ok=True)
    gravar_json(pasta / 'info.json', {'id': roteiro['id'], 'duracao': dur, 'palavras': len(pal)})
    print(f'Pronto: {pasta / "reel.mp4"} ({dur:.1f}s)')
    return dur


# ---------------- escolha do roteiro ----------------
def carregar_banco():
    return {json.loads(p.read_text(encoding='utf-8'))['id']: json.loads(p.read_text(encoding='utf-8')) for p in sorted(BANCO.glob('*.json'))}


def escolher(banco, publicados):
    usados = {p['roteiro'] for p in publicados}
    livres = [r for r in banco.values() if r['id'] not in usados]
    if not livres:
        return None
    pesos = ler_json(DADOS / 'pesos.json', {})
    ultimo = publicados[-1]['formato'] if publicados else None
    cand = [r for r in livres if r['formato'] != ultimo] or livres
    if random.random() < CFG.get('exploracao', .3):
        return random.choice(cand)
    def peso(r):
        f = pesos.get('formato', {}).get(r['formato'], 0)
        g = pesos.get('gancho_tipo', {}).get(r.get('gancho_tipo', ''), 0)
        return math.exp(f + g)
    tot = sum(peso(r) for r in cand)
    x = random.random() * tot
    for r in cand:
        x -= peso(r)
        if x <= 0: return r
    return cand[-1]


def slot_vencido(publicados, agora=None):
    agora = agora or datetime.now(BRT)
    if agora.strftime('%Y-%m-%d') < CFG.get('comecar_em', '0000'):
        return None
    feitos = {p.get('slot') for p in publicados}
    for h in CFG['horarios']:
        hh, mm = map(int, h.split(':'))
        s = agora.replace(hour=hh, minute=mm, second=0, microsecond=0)
        nome = s.strftime('%Y-%m-%d %H:%M')
        if s <= agora < s + timedelta(hours=3) and nome not in feitos:
            return nome
    return None


# ---------------- Instagram ----------------
def subir_midia(arq, nome):
    """Publica o vídeo no branch 'midia' (só os arquivos atuais) e devolve a URL pública."""
    tmp = Path(tempfile.mkdtemp(prefix='midia-'))
    subprocess.run(['git', 'worktree', 'add', '--detach', str(tmp)], cwd=RAIZ, check=True)
    try:
        run = lambda *a: subprocess.run(list(a), cwd=tmp, check=True)
        run('git', 'checkout', '--orphan', 'midia-novo')
        run('git', 'rm', '-rfq', '.')
        shutil.copy(arq, tmp / nome)
        run('git', 'add', nome)
        run('git', '-c', 'user.name=robo-meu-cao-obedece', '-c', 'user.email=robo@users.noreply.github.com', 'commit', '-qm', f'midia {nome}')
        run('git', 'push', '-qf', 'origin', 'HEAD:midia')
    finally:
        subprocess.run(['git', 'worktree', 'remove', '--force', str(tmp)], cwd=RAIZ)
        subprocess.run(['git', 'branch', '-D', 'midia-novo'], cwd=RAIZ, capture_output=True)
    return f'https://raw.githubusercontent.com/{REPO}/midia/{nome}'


def postar_reel(url, legenda):
    from postar import chamar, conta_instagram
    ig = conta_instagram()
    r = chamar('POST', f'{ig}/media', {'media_type': 'REELS', 'video_url': url, 'caption': legenda, 'share_to_feed': 'true'})
    cid = r['id']
    for _ in range(60):
        st = chamar('GET', cid, {'fields': 'status_code,status'})
        if st.get('status_code') == 'FINISHED': break
        if st.get('status_code') in ('ERROR', 'EXPIRED'):
            raise RuntimeError(f"A Meta recusou o vídeo: {st.get('status')}")
        time.sleep(10)
    else:
        raise RuntimeError('O vídeo demorou demais para processar.')
    for tentativa in range(3):
        try:
            mid = chamar('POST', f'{ig}/media_publish', {'creation_id': cid})['id']; break
        except RuntimeError as e:
            print('publicar falhou, tentando de novo:', e); time.sleep(20)
    else:
        raise RuntimeError('Não consegui publicar.')
    link = chamar('GET', mid, {'fields': 'permalink'}).get('permalink', '')
    return mid, link


def cmd_postar(args):
    pub_path = DADOS / 'reels_publicados.json'
    publicados = ler_json(pub_path, [])
    banco = carregar_banco()
    teste = '--teste' in args
    forcar = args[args.index('--forcar') + 1] if '--forcar' in args else None
    slot = slot_vencido(publicados)
    if not slot and not forcar and not teste:
        print('Nenhum horário de Reels vencido agora.'); return
    rot = banco.get(forcar) if forcar else escolher(banco, publicados)
    if not rot:
        print('⚠️ O banco de roteiros acabou — aguardando roteiros novos.'); return
    rot = dict(rot)
    if not rot.get('estilo'):
        est = CFG.get('estilos', ['sol'])
        rot['estilo'] = est[len(publicados) % len(est)]
    print(f'Roteiro: {rot["id"]} ({rot["formato"]}, estilo {rot["estilo"]}) — horário {slot or "manual"}')
    pasta = Path(tempfile.mkdtemp(prefix='reel-'))
    dur = produzir(rot, pasta)
    nome = f'{datetime.now(BRT).strftime("%Y%m%d-%H%M")}-{rot["id"]}.mp4'
    url = subir_midia(pasta / 'reel.mp4', nome)
    shutil.copy(pasta / 'capa.jpg', RAIZ / 'reels' / 'ultima-capa.jpg')
    print('Vídeo público:', url)
    if teste:
        print('Modo teste: não postei.'); return
    legenda = rot['legenda'] + ('\n\n' + rot['hashtags'] if rot.get('hashtags') else '')
    time.sleep(20)  # dá tempo do CDN do GitHub servir o arquivo
    mid, link = postar_reel(url, legenda)
    publicados.append({'slot': slot or datetime.now(BRT).strftime('%Y-%m-%d %H:%M'), 'roteiro': rot['id'], 'formato': rot['formato'],
                       'gancho_tipo': rot.get('gancho_tipo', ''), 'estilo': rot.get('estilo', ''), 'tema': rot.get('tema', ''), 'duracao': dur, 'media_id': mid, 'link': link,
                       'publicado_em': datetime.now(timezone.utc).isoformat()})
    gravar_json(pub_path, publicados)
    print('Publicado!', link)


def main():
    a = sys.argv[1:]
    if not a: sys.exit(__doc__)
    if a[0] == 'produzir':
        alvo = a[1]
        rot = json.loads(Path(alvo).read_text(encoding='utf-8')) if alvo.endswith('.json') else carregar_banco()[alvo]
        produzir(rot, a[2], '--falso' in a)
    elif a[0] == 'precisa':
        print('sim' if slot_vencido(ler_json(DADOS / 'reels_publicados.json', [])) else 'nao')
    elif a[0] == 'postar':
        cmd_postar(a[1:])
    else:
        sys.exit(__doc__)


if __name__ == '__main__':
    try:
        main()
    except RuntimeError as e:
        sys.exit(str(e))
