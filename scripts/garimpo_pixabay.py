"""Garimpo no Pixabay pela API oficial. Licença de conteúdo do Pixabay: uso comercial, inclusive em anúncio, sem
crédito obrigatório (não vale distribuir o vídeo cru, nem usar pessoa reconhecível como se recomendasse o produto).
Busca cães fazendo as dores do nosso produto, confere pelas tags se o vídeo mostra mesmo aquilo, prioriza vídeo
em pé (9:16) e os mais baixados, e monta as mesmas pranchas/compilado/lista do garimpo do Mixkit em garimpo/.
Precisa do segredo PIXABAY_API_KEY (variável de ambiente). Uso: python scripts/garimpo_pixabay.py"""
import json, os, re, sys, time, urllib.error, urllib.parse, urllib.request
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import garimpo_videos as gv  # noqa: E402

_BRUTA = os.environ.get('PIXABAY_API_KEY', '')
# o celular às vezes troca o hífen por travessão ou cola caractere invisível: normaliza antes de procurar a chave
_LIMPA = re.sub(r'[\s​-‍⁠﻿]', '', re.sub(r'[‐-―−﹘﹣－]', '-', _BRUTA))
_ACHOU = re.search(r'\d{4,}-[0-9a-fA-F]{16,}', _LIMPA)  # formato da chave do Pixabay; ignora "Sua chave API:" etc.
CHAVE = _ACHOU.group(0) if _ACHOU else _LIMPA


def diagnostico():
    """Descreve a chave sem revelar o valor: tamanhos e tipos de caractere."""
    s = _BRUTA
    blocos = [len(b) for b in re.split(r'[^0-9A-Za-z]+', s) if b]
    return (f'tamanho bruto {len(s)}, usado {len(CHAVE)}, formato número-hex: {"sim" if _ACHOU else "NÃO"}; '
            f'dígitos {sum(c.isdigit() for c in s)}, letras a-f {sum(c in "abcdefABCDEF" for c in s)}, '
            f'outras letras {sum(c.isalpha() and c not in "abcdefABCDEF" for c in s)}, hífens {s.count("-")}, '
            f'não-ASCII {sum(ord(c) > 127 for c in s)}, espaços {sum(c.isspace() for c in s)}, blocos {blocos}')
API = 'https://pixabay.com/api/videos/'
CAES = {'canine', 'pet', 'pets', 'pup', 'labrador', 'retriever', 'beagle', 'chihuahua', 'poodle', 'husky', 'bulldog', 'terrier',
        'shepherd', 'corgi', 'pug', 'dachshund', 'spitz', 'pomeranian', 'schnauzer', 'collie', 'rottweiler', 'doberman'}
FORA = {'cat', 'cats', 'kitten', 'kittens', 'animation', 'animated', 'cartoon', 'illustration', 'render', '3d', 'statue',
        'sculpture', 'plush', 'stuffed', 'robot'}
# (categoria, buscas, começo de palavra que precisa aparecer nas tags) — na ordem de importância para o anúncio
BUSCAS = [
    ('xixi', ['dog pee', 'puppy pee', 'dog peeing', 'dog urinating', 'puppy potty', 'dog poop'],
     ('pee', 'urin', 'potty', 'toilet', 'poop', 'puddle', 'diaper')),
    ('roendo', ['dog chewing', 'puppy chewing', 'dog shoe', 'dog destroying', 'dog slipper'],
     ('chew', 'bite', 'biting', 'shoe', 'slipper', 'destroy', 'pillow', 'mess')),
    ('latindo', ['dog barking', 'barking dog', 'dog bark', 'dog growling'], ('bark', 'howl', 'growl')),
    ('puxando a guia', ['dog leash', 'dog pulling leash', 'dog walking leash'], ('leash',)),
    ('pulando', ['dog jumping', 'excited dog', 'dog jump'], ('jump', 'excite')),
    ('nao obedece', ['dog running away', 'stubborn dog', 'naughty dog', 'dog escaping'],
     ('run', 'stubborn', 'naughty', 'escap', 'chas', 'disobe')),
    ('calmo e treino', ['dog training', 'dog sit', 'dog treat', 'dog obedience', 'calm dog'],
     ('train', 'sit', 'treat', 'obedien', 'command', 'calm', 'relax', 'lying')),
    ('tutor no celular', ['woman phone dog', 'man phone dog', 'smartphone dog'], ('phone', 'smartphone', 'mobile', 'cellphone')),
]
POR_CATEGORIA = {'xixi': 8, 'roendo': 7, 'latindo': 6, 'puxando a guia': 6, 'pulando': 5, 'nao obedece': 5, 'calmo e treino': 7, 'tutor no celular': 4}
AVISO = ('Licença de conteúdo do Pixabay: uso comercial, inclusive em anúncio, sem crédito obrigatório. Não vale: distribuir o vídeo '
         'cru, apresentar como cliente real ou "antes e depois", nem sugerir que a pessoa do vídeo recomenda o produto.')


def api(**extra):
    """Uma busca na API de vídeos do Pixabay (uma página, os mais populares primeiro). Nunca imprime a URL: ela leva a chave."""
    params = {'key': CHAVE, 'video_type': 'film', 'safesearch': 'true', 'order': 'popular', 'per_page': 50, **extra}
    req = urllib.request.Request(API + '?' + urllib.parse.urlencode(params), headers={'User-Agent': 'meu-cao-obedece/1.0'})
    rotulo = extra.get('q') or extra.get('id')
    for t in range(3):
        try:
            with urllib.request.urlopen(req, timeout=30) as r:
                return json.loads(r.read().decode('utf-8')).get('hits', [])
        except urllib.error.HTTPError as e:
            corpo = e.read().decode('utf-8', 'ignore')[:120]
            if e.code in (400, 401, 403) and 'key' in corpo.lower():
                sys.exit(f'CHAVE_INVALIDA: o Pixabay recusou a chave ({e.code}: {corpo[:60]}; {diagnostico()}). Confira o segredo PIXABAY_API_KEY.')
            print('  busca falhou', rotulo, e.code, corpo); time.sleep(30 if e.code == 429 else 5 * (t + 1))
        except Exception as e:  # noqa: BLE001
            print('  busca falhou', rotulo, str(e)[:60]); time.sleep(5 * (t + 1))
    return []


def palavras(tags):
    return [p for t in (tags or '').lower().split(',') for p in t.strip().split()]


def serve(h, chaves):
    """Tem cão nas tags, não tem gato/desenho, e tem alguma palavra da dor procurada."""
    ws = palavras(h.get('tags'))
    tem_cao = any(w.startswith(('dog', 'pupp')) or w in CAES for w in ws)
    return tem_cao and not any(w in FORA for w in ws) and any(w.startswith(chaves) for w in ws)


def versoes(h):
    return [v for v in (h.get('videos') or {}).values() if v.get('url') and v.get('width') and v.get('height')]


def em_pe(h):
    vs = versoes(h)
    return bool(vs) and vs[0]['height'] > vs[0]['width']


def nota(h):
    """Mais baixado e mais curtido sobe; vídeo em pé vale o dobro (é o formato do Reels/Stories)."""
    return (h.get('downloads', 0) + 5 * h.get('likes', 0)) * (2 if em_pe(h) else 1)


def arquivo(h, alvo, limite=95_000_000):
    """URL da versão cujo menor lado fica mais perto de `alvo` px, abaixo de `limite` bytes."""
    vs = [v for v in versoes(h) if (v.get('size') or 0) < limite]
    return min(vs, key=lambda v: abs(min(v['width'], v['height']) - alvo))['url'] if vs else None


def preparar(v):
    """Baixa a prévia e mede duração/formato. False se não deu."""
    if not v.get('previa'):
        return False
    dados = gv.get(v['previa'])
    if len(dados) < 20000:
        print('  sem prévia', v['id']); return False
    arq = gv.TMP / f"pb{v['id']}.mp4"
    arq.write_bytes(dados)
    v.update(gv.medir(arq)); v['arq'] = str(arq)
    return True


def main():
    if not CHAVE:
        sys.exit('Falta o segredo PIXABAY_API_KEY.')
    usados, cand = set(), []
    for cat, termos, chaves in BUSCAS:
        achados = {}
        for termo in termos:
            for h in api(q=termo):
                if h['id'] in usados or not (4 <= h.get('duration', 0) <= 60) or not serve(h, chaves):
                    continue
                achados[h['id']] = h
            time.sleep(1)
        melhores = sorted(achados.values(), key=nota, reverse=True)[:POR_CATEGORIA[cat]]
        for h in melhores:
            usados.add(h['id'])
            cand.append({'id': str(h['id']), 'titulo': ', '.join(t.strip() for t in (h.get('tags') or '').split(',')[:5]),
                         'pagina': h.get('pageURL', ''), 'cat': cat, 'autor': h.get('user', ''),
                         'previa': arquivo(h, 540), 'hd': arquivo(h, 1080), 'licenca': 'Pixabay (uso comercial ok)'})
        print(f'{cat}: {len(achados)} achados, {len(melhores)} na prancha')
    ok = [v for v in cand if preparar(v)]
    gv.montar(ok, 'Pixabay', AVISO)
    print('prontos:', len(ok))


if __name__ == '__main__':
    main()
