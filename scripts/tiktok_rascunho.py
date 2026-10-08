"""Histórias do TikTok: renderiza de madrugada e manda em lotes (manhã/tarde/noite) para os RASCUNHOS.

python scripts/tiktok_rascunho.py autorizar <codigo>   # uma vez, depois de conectar em docs/conectar.html
python scripts/tiktok_rascunho.py precisa              # "sim" se hoje ainda faltam vídeos
python scripts/tiktok_rascunho.py enviar [quantidade]  # gera e envia o que falta de hoje

Precisa dos segredos TIKTOK_CLIENT_KEY e TIKTOK_CLIENT_SECRET.
O token fica criptografado em dados/tiktok_token.enc (chave = client secret).
"""
import json, os, subprocess, sys, tempfile, time, urllib.error, urllib.parse, urllib.request
from datetime import datetime
from html import escape
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(RAIZ / 'scripts'))
import reels  # noqa: E402

CK = os.environ.get('TIKTOK_CLIENT_KEY', '').strip()
CS = os.environ.get('TIKTOK_CLIENT_SECRET', '').strip()
REDIRECT = 'https://kaicjackson88-ui.github.io/meucaoobedece-postss/tiktok-callback.html'
TOKEN_ARQ = RAIZ / 'dados' / 'tiktok_token.enc'
ENVIADOS = RAIZ / 'dados' / 'tiktok_rascunhos.json'
USADOS = RAIZ / 'dados' / 'tiktok_usados.json'
BANCO = RAIZ / 'tiktok' / 'banco'
FILA = RAIZ / 'dados' / 'tiktok_fila.json'  # espelhos do Instagram que ainda não entraram (limite de rascunhos pendentes)
POR_DIA = int(reels.CFG.get('tiktok_por_dia', 0))
PRONTOS = RAIZ / 'dados' / 'tiktok_prontos.json'   # histórias já renderizadas de madrugada, esperando o horário do lote
LOTES = reels.CFG.get('tiktok_lotes', ['05:20', '11:50', '17:20'])
POR_LOTE = int(reels.CFG.get('tiktok_por_lote', 3))
NOITE = reels.CFG.get('tiktok_render_hora', '01:00')
INICIO = reels.CFG.get('tiktok_hora_inicio', '08:00')


def http(metodo, url, dados=None, headers=None, json_body=None, raw=None):
    h = dict(headers or {})
    if json_body is not None:
        dados = json.dumps(json_body).encode(); h['Content-Type'] = 'application/json; charset=UTF-8'
    elif dados is not None:
        dados = urllib.parse.urlencode(dados).encode(); h['Content-Type'] = 'application/x-www-form-urlencoded'
    elif raw is not None:
        dados = raw
    req = urllib.request.Request(url, data=dados, headers=h, method=metodo)
    try:
        with urllib.request.urlopen(req, timeout=120) as r:
            corpo = r.read().decode() or '{}'
            return json.loads(corpo) if corpo.strip().startswith('{') else {}
    except urllib.error.HTTPError as e:
        raise RuntimeError(f'TikTok respondeu {e.code}: {e.read().decode(errors="replace")[:400]}')


def salvar_token(tok):
    TOKEN_ARQ.parent.mkdir(exist_ok=True)
    p = subprocess.run(['openssl', 'enc', '-aes-256-cbc', '-pbkdf2', '-salt', '-a', '-pass', 'env:TIKTOK_CLIENT_SECRET'],
                       input=json.dumps(tok).encode(), capture_output=True, check=True)
    TOKEN_ARQ.write_bytes(p.stdout)


def ler_token():
    p = subprocess.run(['openssl', 'enc', '-d', '-aes-256-cbc', '-pbkdf2', '-a', '-pass', 'env:TIKTOK_CLIENT_SECRET'],
                       input=TOKEN_ARQ.read_bytes(), capture_output=True, check=True)
    return json.loads(p.stdout)


def autorizar(codigo):
    r = http('POST', 'https://open.tiktokapis.com/v2/oauth/token/', {
        'client_key': CK, 'client_secret': CS, 'code': urllib.parse.unquote(codigo.strip()),
        'grant_type': 'authorization_code', 'redirect_uri': REDIRECT})
    if 'refresh_token' not in r:
        raise RuntimeError(f'Não consegui autorizar: {r}')
    salvar_token({'refresh_token': r['refresh_token'], 'open_id': r.get('open_id'), 'escopos': r.get('scope')})
    print('TikTok conectado! Escopos:', r.get('scope'))


def access_token():
    tok = ler_token()
    r = http('POST', 'https://open.tiktokapis.com/v2/oauth/token/', {
        'client_key': CK, 'client_secret': CS, 'grant_type': 'refresh_token', 'refresh_token': tok['refresh_token']})
    if 'access_token' not in r:
        raise RuntimeError(f'Não consegui renovar o acesso (reconecte em docs/conectar.html): {r}')
    if r.get('refresh_token') and r['refresh_token'] != tok['refresh_token']:
        tok['refresh_token'] = r['refresh_token']; salvar_token(tok)
    return r['access_token']


def enviar_video(at, arq):
    tam = arq.stat().st_size
    r = http('POST', 'https://open.tiktokapis.com/v2/post/publish/inbox/video/init/', headers={'Authorization': f'Bearer {at}'},
             json_body={'source_info': {'source': 'FILE_UPLOAD', 'video_size': tam, 'chunk_size': tam, 'total_chunk_count': 1}})
    if r.get('error', {}).get('code') not in (None, 'ok'):
        raise RuntimeError(f"Erro ao iniciar envio: {r['error']}")
    up = r['data']['upload_url']; pid = r['data']['publish_id']
    http('PUT', up, headers={'Content-Type': 'video/mp4', 'Content-Length': str(tam), 'Content-Range': f'bytes 0-{tam - 1}/{tam}'}, raw=arq.read_bytes())
    status = '?'
    for _ in range(12):
        time.sleep(10)
        try:
            s = http('POST', 'https://open.tiktokapis.com/v2/post/publish/status/fetch/', headers={'Authorization': f'Bearer {at}'}, json_body={'publish_id': pid})
            status = s.get('data', {}).get('status', '?')
            if status in ('SEND_TO_USER_INBOX', 'PUBLISH_COMPLETE', 'FAILED'): break
        except RuntimeError as e:
            status = str(e)[:80]; break
    return pid, status


def hoje():
    return datetime.now(reels.BRT).strftime('%Y-%m-%d')


def faltam_hoje():
    env = reels.ler_json(ENVIADOS, [])
    return max(0, POR_DIA - sum(1 for e in env if e['data'] == hoje() and e.get('status') != 'FAILED' and e.get('tipo') != 'espelho'))


def espelhar(arq, rid, legenda, url=None):
    """Manda pro TikTok o mesmo vídeo que acabou de sair no Instagram. Se não der (ex.: limite de 5 rascunhos
    pendentes), guarda na fila e tenta de novo nas próximas horas."""
    if not CK or not CS or not TOKEN_ARQ.exists():
        return
    try:
        pid, st = enviar_video(access_token(), Path(arq))
        if st == 'FAILED':
            raise RuntimeError('status FAILED')
    except Exception as e:
        fila = reels.ler_json(FILA, []); fila.append({'id': rid, 'url': url, 'legenda': legenda, 'erro': str(e)[:200], 'quando': datetime.now(reels.BRT).isoformat()})
        reels.gravar_json(FILA, fila); print('TikTok: ficou na fila —', e); return
    env = reels.ler_json(ENVIADOS, [])
    env.append({'data': hoje(), 'id': rid, 'tipo': 'espelho', 'legenda': legenda, 'publish_id': pid, 'status': st, 'quando': datetime.now(reels.BRT).isoformat()})
    reels.gravar_json(ENVIADOS, env); atualizar_pagina_legendas()
    print('TikTok: espelho nos rascunhos:', st)


def processar_fila():
    fila = reels.ler_json(FILA, [])
    if not fila or not TOKEN_ARQ.exists():
        return
    at = access_token(); resto = []
    for i, item in enumerate(fila):
        try:
            arq = Path(tempfile.mkdtemp(prefix='ttf-')) / 'v.mp4'
            urllib.request.urlretrieve(item['url'], arq)
        except Exception as e:
            print('TikTok fila: vídeo não está mais disponível, descartei', item['id'], e); continue
        try:
            pid, st = enviar_video(at, arq)
            if st == 'FAILED': raise RuntimeError('status FAILED')
        except Exception as e:
            print('TikTok fila: ainda não deu, tento depois —', e); resto = fila[i:]; break
        env = reels.ler_json(ENVIADOS, [])
        env.append({'data': hoje(), 'id': item['id'], 'tipo': 'espelho', 'legenda': item.get('legenda', ''), 'publish_id': pid, 'status': st, 'quando': datetime.now(reels.BRT).isoformat()})
        reels.gravar_json(ENVIADOS, env)
    reels.gravar_json(FILA, resto); atualizar_pagina_legendas()


def atualizar_pagina_legendas():
    env = reels.ler_json(ENVIADOS, [])[-21:][::-1]
    banco = {json.loads(p.read_text(encoding='utf-8'))['id']: json.loads(p.read_text(encoding='utf-8')) for p in BANCO.glob('*.json')}
    blocos = []
    for i, e in enumerate(env):
        r = banco.get(e['id'], {})
        leg = e.get('legenda') or (r.get('legenda', '') + '\n\n' + r.get('hashtags', '')).strip()
        blocos.append(f'<div class="caixa"><b>{escape(e["data"])} · {escape(e["id"])}</b><pre id="l{i}">{escape(leg)}</pre>'
                      f'<p><button onclick="navigator.clipboard.writeText(document.getElementById(\'l{i}\').textContent);this.textContent=\'Copiado ✓\'">Copiar legenda</button></p></div>')
    html = ('<!doctype html><html lang="pt-BR"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">'
            '<title>Legendas TikTok</title><link rel="stylesheet" href="estilo.css"></head><body><main><div class="marca">🐾 Meu Cão Obedece</div>'
            '<h1>Legendas dos rascunhos do TikTok</h1><p>Os vídeos estão nos seus rascunhos do TikTok (Caixa de entrada › notificação). Abra, cole a legenda, ponha um som se quiser e publique.</p>'
            + ''.join(blocos) + '</main></body></html>')
    (RAIZ / 'docs' / 'legendas.html').write_text(html, encoding='utf-8')


def enviar(qtd=None):
    try:
        processar_fila()
    except Exception as e:
        print('TikTok fila falhou:', e)
    qtd = qtd or faltam_hoje()
    if qtd <= 0:
        print('Hoje já foi tudo pros rascunhos.'); return
    usados = reels.ler_json(USADOS, [])
    ja = {u['id'] for u in usados}
    livres = [p for p in sorted(BANCO.glob('*.json')) if json.loads(p.read_text(encoding='utf-8'))['id'] not in ja]
    if not livres:
        print('⚠️ Banco de roteiros do TikTok vazio — aguardando o roteirista.'); return
    at = access_token()
    env = reels.ler_json(ENVIADOS, [])
    for p in livres[:qtd]:
        rot = json.loads(p.read_text(encoding='utf-8'))
        print('Produzindo', rot['id'], flush=True)
        pasta = Path(tempfile.mkdtemp(prefix='tt-'))
        reels.produzir(rot, pasta)
        pid, st = enviar_video(at, pasta / 'reel.mp4')
        print(f'  enviado para os rascunhos: {st}')
        env.append({'data': hoje(), 'id': rot['id'], 'publish_id': pid, 'status': st, 'quando': datetime.now(reels.BRT).isoformat()})
        usados.append({'id': rot['id'], 'quando': datetime.now(reels.BRT).isoformat()})
        reels.gravar_json(ENVIADOS, env); reels.gravar_json(USADOS, usados)
        atualizar_pagina_legendas()
        reels.salvar_git('TikTok: vídeo nos rascunhos')


# ---------------- produção noturna + lotes (manhã, tarde, noite) ----------------
def _hhmm():
    return datetime.now(reels.BRT).strftime('%H:%M')


def meta_dia():
    return POR_LOTE * len(LOTES)


def noite_pendente():
    pr = reels.ler_json(PRONTOS, [])
    # renderiza de madrugada; se a madrugada falhar, recupera até as 15h (nunca à noite)
    return NOITE <= _hhmm() < '15:00' and sum(1 for x in pr if x['data'] == hoje()) < meta_dia()


def a_enviar():
    pr = reels.ler_json(PRONTOS, [])
    devidos = POR_LOTE * sum(1 for h in LOTES if _hhmm() >= h)
    feitos = sum(1 for x in pr if (x.get('enviado') or '').startswith(hoje()))
    return min(max(0, devidos - feitos), sum(1 for x in pr if not x.get('enviado')))


def historias_livres():
    usados = {u['id'] for u in reels.ler_json(USADOS, [])} | {x['id'] for x in reels.ler_json(PRONTOS, [])}
    out = []
    for p in sorted(BANCO.glob('h*.json')):
        r = json.loads(p.read_text(encoding='utf-8'))
        if r.get('formato') == 'tiktok-historia' and r['id'] not in usados:
            out.append(r)
    return out


def noite(qtd=None):
    """Renderiza as histórias do dia e deixa prontas (vídeo publicado numa branch de mídia)."""
    pr = reels.ler_json(PRONTOS, [])
    qtd = qtd if qtd is not None else meta_dia() - sum(1 for x in pr if x['data'] == hoje())
    livres = historias_livres()
    if qtd > len(livres):
        print(f'⚠️ Só há {len(livres)} histórias novas no banco (queria {qtd}) — o roteirista repõe à noite.')
    for rot in livres[:max(0, qtd)]:
        print('Produzindo', rot['id'], flush=True)
        pasta = Path(tempfile.mkdtemp(prefix='tt-'))
        try:
            reels.produzir(rot, pasta)
            url = reels.subir_midia(pasta / 'reel.mp4', f'{datetime.now(reels.BRT).strftime("%Y%m%d-%H%M")}-tt-{rot["id"]}.mp4')
        except Exception as e:
            print('  falhou:', e); continue
        leg = (rot.get('legenda', '') + '\n\n' + rot.get('hashtags', '')).strip()
        pr = reels.ler_json(PRONTOS, [])
        pr.append({'id': rot['id'], 'data': hoje(), 'url': url, 'legenda': leg, 'enviado': None})
        reels.gravar_json(PRONTOS, pr[-60:])
        us = reels.ler_json(USADOS, []); us.append({'id': rot['id'], 'quando': datetime.now(reels.BRT).isoformat()}); reels.gravar_json(USADOS, us)
        reels.salvar_git('TikTok: história pronta')


def enviar_lote(n):
    pr = reels.ler_json(PRONTOS, [])
    pend = [x for x in pr if not x.get('enviado')][:n]
    if not pend:
        return
    at = access_token()
    for x in pend:
        try:
            arq = Path(tempfile.mkdtemp(prefix='ttl-')) / 'v.mp4'
            urllib.request.urlretrieve(x['url'], arq)
        except Exception as e:
            print('Vídeo pronto sumiu, descartei', x['id'], e); x['enviado'] = 'descartado'; continue
        try:
            pid, st = enviar_video(at, arq)
            if st == 'FAILED': raise RuntimeError('status FAILED')
        except Exception as e:
            print('TikTok não aceitou agora (provável limite de 5 rascunhos pendentes) — tento na próxima hora:', e); break
        x['enviado'] = datetime.now(reels.BRT).isoformat(); x['status'] = st
        env = reels.ler_json(ENVIADOS, [])
        env.append({'data': hoje(), 'id': x['id'], 'tipo': 'lote', 'legenda': x['legenda'], 'publish_id': pid, 'status': st, 'quando': x['enviado']})
        reels.gravar_json(ENVIADOS, env); reels.gravar_json(PRONTOS, pr)
        print('  nos rascunhos:', x['id'], st)
    reels.gravar_json(PRONTOS, pr); atualizar_pagina_legendas()


def ciclo(qtd=None):
    try:
        processar_fila()
    except Exception as e:
        print('TikTok fila falhou:', e)
    if qtd:  # envio manual agora
        falta = qtd - sum(1 for x in reels.ler_json(PRONTOS, []) if not x.get('enviado'))
        if falta > 0: noite(falta)
        enviar_lote(qtd); return
    if noite_pendente():
        noite()
    n = a_enviar()
    if n: enviar_lote(n)
    else: print('Nenhum lote vencido agora.')


def main():
    a = sys.argv[1:]
    if not a: sys.exit(__doc__)
    if a[0] == 'precisa':
        hh, mm = map(int, INICIO.split(':'))
        agora = datetime.now(reels.BRT)
        ok = TOKEN_ARQ.exists() and (noite_pendente() or a_enviar() > 0 or bool(reels.ler_json(FILA, [])))
        print('sim' if ok else 'nao'); return
    if not CK or not CS:
        sys.exit('Faltam os segredos TIKTOK_CLIENT_KEY e TIKTOK_CLIENT_SECRET no GitHub.')
    if a[0] == 'autorizar':
        autorizar(a[1])
    elif a[0] == 'enviar':
        ciclo(int(a[1]) if len(a) > 1 and a[1].isdigit() else None)


if __name__ == '__main__':
    try: main()
    except RuntimeError as e: sys.exit(str(e))
