"""Gestor de anúncios da Meta (Marketing API) — Meu Cão Obedece.
Comandos:
  checar     → quais permissões a chave tem, contas de anúncio, páginas, Instagram e pixels (grava dados/meta_anuncios_status.json)
Usa o segredo META_ADS_TOKEN; se não existir, tenta o IG_TOKEN. Nunca imprime a chave."""
import json, os, sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
os.environ['IG_TOKEN'] = (os.environ.get('META_ADS_TOKEN') or os.environ.get('IG_TOKEN') or '').strip()
import postar  # noqa: E402  (usa postar.chamar com a chave acima)

RAIZ = Path(__file__).resolve().parents[1]
STATUS = RAIZ / 'dados' / 'meta_anuncios_status.json'


def _try(f, padrao=None):
    try:
        return f()
    except Exception as e:  # noqa: BLE001
        print('  aviso:', str(e)[:200])
        return padrao


def checar():
    chamar = postar.chamar
    perms = _try(lambda: chamar('GET', 'me/permissions', {}), {}) or {}
    concedidas = sorted(p['permission'] for p in perms.get('data', []) if p.get('status') == 'granted')
    print('Permissões concedidas:', ', '.join(concedidas) or '(nenhuma lida)')
    falta = [p for p in ('ads_management', 'ads_read') if p not in concedidas]
    print('Faltam para anúncios:', ', '.join(falta) or 'nada — dá para gerenciar anúncios')
    contas = _try(lambda: chamar('GET', 'me/adaccounts', {'fields': 'id,name,currency,account_status,amount_spent', 'limit': 50}), {}) or {}
    contas = [{'id': c['id'], 'nome': c.get('name'), 'moeda': c.get('currency'), 'status': c.get('account_status'), 'gasto': c.get('amount_spent')} for c in contas.get('data', [])]
    for c in contas:
        print('Conta de anúncio:', c)
    pags = _try(lambda: chamar('GET', 'me/accounts', {'fields': 'id,name,instagram_business_account{id,username}'}), {}) or {}
    paginas = [{'id': p['id'], 'nome': p.get('name'), 'ig': (p.get('instagram_business_account') or {}).get('id'),
                'ig_user': (p.get('instagram_business_account') or {}).get('username')} for p in pags.get('data', [])]
    for p in paginas:
        print('Página:', p)
    pixels = []
    for c in contas:
        r = _try(lambda: chamar('GET', f"{c['id']}/adspixels", {'fields': 'id,name,last_fired_time'}), {}) or {}
        for px in r.get('data', []):
            pixels.append({'conta': c['id'], 'id': px['id'], 'nome': px.get('name'), 'ultimo_evento': px.get('last_fired_time')})
            print('Pixel:', pixels[-1])
    STATUS.parent.mkdir(exist_ok=True)
    STATUS.write_text(json.dumps({'permissoes': concedidas, 'faltam': falta, 'contas_anuncio': contas, 'paginas': paginas, 'pixels': pixels},
                                 ensure_ascii=False, indent=1), encoding='utf-8')
    print('Gravado em', STATUS.relative_to(RAIZ))


if __name__ == '__main__':
    cmd = sys.argv[1] if len(sys.argv) > 1 else 'checar'
    {'checar': checar}[cmd]()
