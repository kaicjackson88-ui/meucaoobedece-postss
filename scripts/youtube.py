"""YouTube Shorts automático (API oficial YouTube Data v3).

Aproveita as histórias já renderizadas de madrugada para o TikTok (dados/tiktok_prontos.json) e sobe no canal
com título, descrição, hashtags e tags. Enquanto o projeto do Google não passar pela verificação da API,
o YouTube deixa os vídeos como "privado" — o Kaic só muda para Público no YouTube Studio.

python scripts/youtube.py autorizar <codigo>   # uma vez (docs/yt-conectar.html)
python scripts/youtube.py precisa              # "sim" se tem horário de envio vencido
python scripts/youtube.py enviar [n]           # sobe o que falta agora
python scripts/youtube.py metricas             # views/likes dos Shorts (dados/youtube_metricas.json)

Segredos: YT_CLIENT_ID, YT_CLIENT_SECRET. Token criptografado em dados/youtube_token.enc.
"""
import json, os, re, subprocess, sys, tempfile, urllib.error, urllib.parse, urllib.request
from datetime import datetime
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(RAIZ / 'scripts'))
import reels  # noqa: E402

CID = os.environ.get('YT_CLIENT_ID', '').strip()
CS = os.environ.get('YT_CLIENT_SECRET', '').strip()
REDIRECT = 'https://kaicjackson88-ui.github.io/meucaoobedece-postss/yt-callback.html'
TOKEN = RAIZ / 'dados' / 'youtube_token.enc'
ENVIADOS = RAIZ / 'dados' / 'youtube_enviados.json'
PRONTOS = RAIZ / 'dados' / 'tiktok_prontos.json'
BANCO = RAIZ / 'tiktok' / 'banco'
CFG = reels.CFG
HORARIOS = CFG.get('yt_horarios', ['07:10', '12:40', '18:40'])
PRIVACIDADE = CFG.get('yt_privacidade', 'private')  # vira 'public' depois da verificação do Google
LINK = CFG.get('link_teste', 'https://meucaoobedece.vercel.app/') + '?utm_source=youtube&utm_medium=shorts'


def http(metodo, url, dados=None, headers=None, json_body=None, raw=None, devolver_headers=False):
    h = dict(headers or {})
    if json_body is not None:
        dados = json.dumps(json_body).encode(); h['Content-Type'] = 'application/json; charset=UTF-8'
    elif dados is not None:
        dados = urllib.parse.urlencode(dados).encode(); h['Content-Type'] = 'application/x-www-form-urlencoded'
    elif raw is not None:
        dados = raw
    req = urllib.request.Request(url, data=dados, headers=h, method=metodo)
    try:
        with urllib.request.urlopen(req, timeout=600) as r:
            corpo = r.read().decode() or '{}'
            j = json.loads(corpo) if corpo.strip().startswith('{') else {}
            return (j, dict(r.headers)) if devolver_headers else j
    except urllib.error.HTTPError as e:
        raise RuntimeError(f'Google respondeu {e.code}: {e.read().decode(errors="replace")[:500]}')


def salvar_token(tok):
    p = subprocess.run(['openssl', 'enc', '-aes-256-cbc', '-pbkdf2', '-salt', '-a', '-pass', 'env:YT_CLIENT_SECRET'],
                       input=json.dumps(tok).encode(), capture_output=True, check=True)
    TOKEN.write_bytes(p.stdout)


def ler_token():
    p = subprocess.run(['openssl', 'enc', '-d', '-aes-256-cbc', '-pbkdf2', '-a', '-pass', 'env:YT_CLIENT_SECRET'],
                       input=TOKEN.read_bytes(), capture_output=True, check=True)
    return json.loads(p.stdout)


def autorizar(codigo):
    r = http('POST', 'https://oauth2.googleapis.com/token', {'code': urllib.parse.unquote(codigo.strip()), 'client_id': CID,
                                                             'client_secret': CS, 'redirect_uri': REDIRECT, 'grant_type': 'authorization_code'})
    if 'refresh_token' not in r:
        raise RuntimeError(f'Não consegui autorizar: {r}')
    salvar_token({'refresh_token': r['refresh_token'], 'escopos': r.get('scope')})
    at = r['access_token']
    canal = http('GET', 'https://www.googleapis.com/youtube/v3/channels?part=snippet,statistics&mine=true', headers={'Authorization': f'Bearer {at}'})
    itens = canal.get('items', [])
    print('YouTube conectado!', ('Canal: ' + itens[0]['snippet']['title']) if itens else '⚠️ essa conta ainda não tem canal — crie um no app do YouTube.')


def access_token():
    tok = ler_token()
    r = http('POST', 'https://oauth2.googleapis.com/token', {'client_id': CID, 'client_secret': CS, 'refresh_token': tok['refresh_token'], 'grant_type': 'refresh_token'})
    if 'access_token' not in r:
        raise RuntimeError(f'Não consegui renovar o acesso (reconecte em docs/yt-conectar.html): {r}')
    return r['access_token']


def hoje():
    return datetime.now(reels.BRT).strftime('%Y-%m-%d')


def faltam_agora():
    agora = datetime.now(reels.BRT).strftime('%H:%M')
    devidos = sum(1 for h in HORARIOS if agora >= h)
    feitos = sum(1 for e in reels.ler_json(ENVIADOS, []) if e.get('data') == hoje() and e.get('video_id'))
    return max(0, devidos - feitos)


def metadados(rid):
    p = BANCO / f'{rid}.json'
    r = json.loads(p.read_text(encoding='utf-8')) if p.exists() else {}
    g = next((c for c in r.get('cenas', []) if c.get('tipo') == 'gancho'), {})
    capa = ' '.join(g.get('linhas', [])).strip().capitalize() or r.get('legenda', 'História de cachorro')[:60]
    leg = r.get('legenda', '').split('(História ilustrativa')[0].strip()
    titulo = re.sub(r'\s+', ' ', f'{leg[:70] or capa} #shorts').strip()[:100]
    tags_txt = r.get('hashtags', '#cachorro #adestramento')
    desc = (r.get('legenda', '') + f'\n\n🐾 Teste grátis — descubra o perfil do seu cão: {LINK}\n\n' + tags_txt + ' #shorts').strip()[:4900]
    tags = [t.lstrip('#') for t in tags_txt.split() if t.startswith('#')][:15] + ['cachorro', 'adestramento', 'historia de cachorro', 'shorts']
    return titulo, desc, list(dict.fromkeys(tags))


def subir(at, arq, rid):
    titulo, desc, tags = metadados(rid)
    meta = {'snippet': {'title': titulo, 'description': desc, 'tags': tags, 'categoryId': '15', 'defaultLanguage': 'pt-BR', 'defaultAudioLanguage': 'pt-BR'},
            'status': {'privacyStatus': PRIVACIDADE, 'selfDeclaredMadeForKids': False, 'embeddable': True}}
    tam = arq.stat().st_size
    _, hd = http('POST', 'https://www.googleapis.com/upload/youtube/v3/videos?uploadType=resumable&part=snippet,status',
                 headers={'Authorization': f'Bearer {at}', 'X-Upload-Content-Type': 'video/mp4', 'X-Upload-Content-Length': str(tam)},
                 json_body=meta, devolver_headers=True)
    url = hd.get('Location') or hd.get('location')
    r = http('PUT', url, headers={'Authorization': f'Bearer {at}', 'Content-Type': 'video/mp4', 'Content-Length': str(tam)}, raw=arq.read_bytes())
    return r.get('id'), r.get('status', {}).get('privacyStatus'), titulo


def enviar(n=None):
    n = n or faltam_agora()
    if n <= 0:
        print('Nenhum horário do YouTube vencido agora.'); return
    env = reels.ler_json(ENVIADOS, [])
    ja = {e['id'] for e in env if e.get('video_id')}
    cand = [p for p in reversed(reels.ler_json(PRONTOS, [])) if p.get('url') and p['id'] not in ja]
    if not cand:
        print('⚠️ Nenhuma história renderizada disponível agora (as do dia saem de madrugada).'); return
    at = access_token()
    for p in cand[:n]:
        try:
            arq = Path(tempfile.mkdtemp(prefix='yt-')) / 'v.mp4'
            urllib.request.urlretrieve(p['url'], arq)
            vid, priv, titulo = subir(at, arq, p['id'])
        except Exception as e:
            print('falhou', p['id'], e)
            if 'quota' in str(e).lower(): break
            continue
        env.append({'data': hoje(), 'id': p['id'], 'video_id': vid, 'privacidade': priv, 'titulo': titulo,
                    'link': f'https://youtube.com/shorts/{vid}', 'quando': datetime.now(reels.BRT).isoformat()})
        reels.gravar_json(ENVIADOS, env)
        print(f'✅ YouTube: {titulo} → https://youtube.com/shorts/{vid} ({priv})')


def metricas():
    env = [e for e in reels.ler_json(ENVIADOS, []) if e.get('video_id')]
    if not env: return
    at = access_token(); out = []
    for i in range(0, len(env), 50):
        ids = ','.join(e['video_id'] for e in env[i:i + 50])
        r = http('GET', f'https://www.googleapis.com/youtube/v3/videos?part=statistics,status&id={ids}', headers={'Authorization': f'Bearer {at}'})
        st = {it['id']: it for it in r.get('items', [])}
        for e in env[i:i + 50]:
            it = st.get(e['video_id'], {})
            s = it.get('statistics', {})
            out.append({'roteiro': e['id'], 'video_id': e['video_id'], 'privacidade': it.get('status', {}).get('privacyStatus'),
                        'views': int(s.get('viewCount', 0)), 'curtidas': int(s.get('likeCount', 0)), 'comentarios': int(s.get('commentCount', 0)), 'link': e['link']})
    canal = http('GET', 'https://www.googleapis.com/youtube/v3/channels?part=statistics&mine=true', headers={'Authorization': f'Bearer {at}'})
    stats = (canal.get('items') or [{}])[0].get('statistics', {})
    reels.gravar_json(RAIZ / 'dados' / 'youtube_metricas.json', {'canal': stats, 'atualizado': datetime.now(reels.BRT).isoformat(), 'videos': out})
    print('YouTube:', stats.get('subscriberCount'), 'inscritos ·', sum(v['views'] for v in out), 'views nos Shorts')


def main():
    a = sys.argv[1:]
    if not a: sys.exit(__doc__)
    if a[0] == 'precisa':
        print('sim' if TOKEN.exists() and faltam_agora() > 0 else 'nao'); return
    if not CID or not CS:
        sys.exit('Faltam os segredos YT_CLIENT_ID e YT_CLIENT_SECRET no GitHub.')
    if a[0] == 'autorizar': autorizar(a[1])
    elif a[0] == 'enviar': enviar(int(a[1]) if len(a) > 1 and a[1].isdigit() else None)
    elif a[0] == 'metricas': metricas()


if __name__ == '__main__':
    try: main()
    except RuntimeError as e: sys.exit(str(e))
