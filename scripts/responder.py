"""Responde quem comentou XIXI: tenta mandar o teste por direct (resposta privada); se a Meta não permitir, responde no comentário."""
import json, os, re, sys, unicodedata, urllib.error, urllib.parse, urllib.request
from datetime import datetime, timedelta, timezone
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent
CFG = json.loads((RAIZ / 'reels' / 'config.json').read_text(encoding='utf-8'))
DADOS = RAIZ / 'dados'
API = 'https://graph.facebook.com/v26.0'
TOKEN = os.environ.get('IG_TOKEN', '').strip()


def chamar(metodo, caminho, params, token=None, json_body=False):
    params = dict(params); params['access_token'] = token or TOKEN
    url = f'{API}/{caminho}'
    if metodo == 'GET':
        req = urllib.request.Request(url + '?' + urllib.parse.urlencode(params))
    else:
        req = urllib.request.Request(url, data=urllib.parse.urlencode(params).encode(), method='POST')
    try:
        with urllib.request.urlopen(req, timeout=60) as r:
            return json.loads(r.read().decode())
    except urllib.error.HTTPError as e:
        try: msg = json.loads(e.read().decode()).get('error', {}).get('message')
        except ValueError: msg = 'erro'
        raise RuntimeError(msg)


def norm(s):
    s = unicodedata.normalize('NFD', s or '')
    return re.sub(r'[^a-z]', '', ''.join(c for c in s if unicodedata.category(c) != 'Mn').lower())


def main():
    if not TOKEN: sys.exit('Falta IG_TOKEN')
    contas = chamar('GET', 'me/accounts', {'fields': 'id,access_token,instagram_business_account{id,username}'})['data']
    pagina = next(p for p in contas if p.get('instagram_business_account'))
    ig = pagina['instagram_business_account']; page_token = pagina.get('access_token')
    feitos_p = DADOS / 'respondidos.json'
    feitos = json.loads(feitos_p.read_text(encoding='utf-8')) if feitos_p.exists() else {}
    limite = datetime.now(timezone.utc) - timedelta(days=7)
    midias = chamar('GET', f"{ig['id']}/media", {'fields': 'id,timestamp,comments_count', 'limit': 30}).get('data', [])
    link = CFG.get('link_teste', '').strip()
    dm = CFG['dm_xixi'].format(link=link) if link else CFG['dm_xixi_sem_link']
    novos = 0
    for m in midias:
        if datetime.fromisoformat(m['timestamp'].replace('+0000', '+00:00')) < limite or not m.get('comments_count'): continue
        try:
            coms = chamar('GET', f"{m['id']}/comments", {'fields': 'id,text,username', 'limit': 50}).get('data', [])
        except RuntimeError as e:
            print('Não consegui ler comentários (permissão instagram_manage_comments?):', e); return
        for c in coms:
            if c['id'] in feitos or c.get('username') == ig.get('username') or 'xixi' not in norm(c.get('text')): continue
            jeito = None
            try:
                chamar('POST', f"{pagina['id']}/messages", {'recipient': json.dumps({'comment_id': c['id']}), 'message': json.dumps({'text': dm})}, token=page_token)
                jeito = 'direct'
            except RuntimeError as e:
                print('  direct não permitido ainda:', e)
                try:
                    chamar('POST', f"{c['id']}/replies", {'message': CFG['resposta_publica']}); jeito = 'comentario'
                except RuntimeError as e2:
                    print('  resposta pública falhou:', e2)
            feitos[c['id']] = {'quando': datetime.now(timezone.utc).isoformat(), 'como': jeito or 'falhou'}
            novos += 1
    DADOS.mkdir(exist_ok=True)
    feitos_p.write_text(json.dumps(feitos, ensure_ascii=False, indent=1), encoding='utf-8')
    print(f'{novos} comentário(s) XIXI respondido(s).')


if __name__ == '__main__':
    try: main()
    except RuntimeError as e: sys.exit(str(e))
