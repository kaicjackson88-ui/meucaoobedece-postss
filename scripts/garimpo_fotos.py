"""Garimpa FOTOS no Pixabay (licença do Pixabay: uso comercial e em anúncio, sem crédito) de cães em cada
posição dos comandos básicos e deixa cifradas em fotos/ (o repositório é público; a licença não deixa
redistribuir o arquivo cru). Usa o segredo PIXABAY_API_KEY.
Uso: python scripts/garimpo_fotos.py   (POR_BUSCA=8)"""
import json, os, sys, time, urllib.error, urllib.parse, urllib.request
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import garimpo_pixabay as gp  # noqa: E402
import garimpo_videos as gv  # noqa: E402
from baixar_escolhidos import cifrar  # noqa: E402

RAIZ = Path(__file__).resolve().parents[1]
OUT = RAIZ / 'fotos'
API = 'https://pixabay.com/api/'
POR_BUSCA = int(os.environ.get('POR_BUSCA', '8'))
BUSCAS = [  # (comando, busca, palavras que precisam aparecer nas tags além de "dog")
    ('senta', 'dog sitting', ('sit', 'sitting')),
    ('senta', 'puppy sitting', ('sit', 'sitting')),
    ('deita', 'dog lying down', ('lying', 'lie', 'down', 'resting')),
    ('deita', 'dog lying floor', ('lying', 'lie', 'floor')),
    ('rola', 'dog rolling', ('rolling', 'roll', 'belly', 'back')),
    ('rola', 'dog belly up', ('belly', 'back', 'rolling')),
    ('pata', 'dog paw hand', ('paw', 'hand', 'give')),
    ('pata', 'dog giving paw', ('paw', 'give')),
    ('fica', 'dog waiting', ('waiting', 'wait', 'patient', 'sitting')),
    ('fica', 'dog stay', ('stay', 'wait', 'sitting')),
    ('vem', 'dog running towards', ('running', 'run')),
    ('treino', 'dog training treat', ('training', 'treat', 'reward')),
    ('treino', 'dog owner training', ('training', 'trainer', 'owner')),
]


def busca(q):
    params = {'key': gp.CHAVE, 'q': q, 'image_type': 'photo', 'safesearch': 'true', 'order': 'popular', 'per_page': 40}
    req = urllib.request.Request(API + '?' + urllib.parse.urlencode(params), headers={'User-Agent': 'meu-cao-obedece/1.0'})
    for t in range(3):
        try:
            with urllib.request.urlopen(req, timeout=30) as r:
                return json.loads(r.read().decode('utf-8')).get('hits', [])
        except urllib.error.HTTPError as e:
            corpo = e.read().decode('utf-8', 'ignore')[:120]
            if e.code in (400, 401, 403) and 'key' in corpo.lower():
                sys.exit(f'CHAVE_INVALIDA ({e.code}; {gp.diagnostico()})')
            print('  busca falhou', q, e.code); time.sleep(30 if e.code == 429 else 5 * (t + 1))
        except Exception as e:  # noqa: BLE001
            print('  busca falhou', q, str(e)[:60]); time.sleep(5 * (t + 1))
    return []


def main():
    OUT.mkdir(exist_ok=True)
    feitos, vistos = [], set()
    for cmd, q, chaves in BUSCAS:
        n = 0
        for h in busca(q):
            tags = (h.get('tags') or '').lower()
            if h['id'] in vistos or ('dog' not in tags and 'puppy' not in tags):
                continue
            if any(x in tags for x in ('cat', 'cartoon', 'illustration', 'drawing', 'toy', 'statue')):
                continue
            if not any(k in tags for k in chaves):
                continue
            dados = gv.get(h.get('largeImageURL') or h.get('webformatURL'))
            if len(dados) < 20000:
                continue
            vistos.add(h['id'])
            nome = f"{cmd}_{h['id']}.jpg"
            arq = gv.TMP / nome
            arq.write_bytes(dados)
            feitos.append({'id': h['id'], 'cmd': cmd, 'busca': q, 'tags': h.get('tags'), 'likes': h.get('likes'), 'downloads': h.get('downloads'),
                           'pagina': h.get('pageURL'), 'autor': h.get('user'), 'w': h.get('imageWidth'), 'h': h.get('imageHeight'), 'arquivo': nome})
            cifrar(arq, OUT / nome)
            n += 1
            if n >= POR_BUSCA:
                break
            time.sleep(0.3)
        print(cmd, '|', q, '→', n, 'fotos')
        time.sleep(1)
    (OUT / 'lista.json').write_text(json.dumps(feitos, ensure_ascii=False, indent=1), encoding='utf-8')
    print('total:', len(feitos))
    if not feitos:
        sys.exit(1)


if __name__ == '__main__':
    main()
