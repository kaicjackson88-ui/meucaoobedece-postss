"""Garimpo no Pexels pela API oficial (licença Pexels: uso comercial, inclusive anúncio, sem crédito obrigatório).
Busca cães fazendo exatamente as dores do nosso produto, prefere vídeo em pé (9:16) e monta as mesmas
pranchas/compilado/lista do garimpo do Mixkit em garimpo/.
Precisa do segredo PEXELS_API_KEY (variável de ambiente). Uso: python scripts/garimpo_pexels.py"""
import json, os, subprocess, sys, time, urllib.parse, urllib.request
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import garimpo_videos as gv  # noqa: E402

CHAVE = os.environ.get('PEXELS_API_KEY', '').strip()
BUSCAS = [  # (categoria, termos) — na ordem de importância para o anúncio
    ('xixi', ['dog pee', 'puppy pee pad', 'dog urine floor', 'cleaning dog pee', 'puppy accident']),
    ('roendo', ['dog chewing shoe', 'dog destroyed pillow', 'dog chewing furniture', 'puppy chewing slipper']),
    ('latindo', ['dog barking at door', 'dog barking window', 'small dog barking']),
    ('puxando a guia', ['dog pulling leash', 'dog walking on leash street']),
    ('pulando', ['dog jumping on person', 'excited dog jumping']),
    ('nao obedece', ['dog ignoring owner', 'dog running away', 'dog stubborn']),
    ('calmo e treino', ['dog sit command treat', 'dog training at home', 'dog lying calm living room', 'dog walking calmly leash']),
    ('tutor no celular', ['woman using phone with dog', 'man phone sofa dog']),
]
POR_CATEGORIA = {'xixi': 8, 'roendo': 7, 'latindo': 6, 'puxando a guia': 6, 'pulando': 5, 'nao obedece': 5, 'calmo e treino': 7, 'tutor no celular': 4}


def api(termo, orientacao):
    q = urllib.parse.urlencode({'query': termo, 'per_page': 15, 'orientation': orientacao, 'size': 'medium'})
    req = urllib.request.Request(f'https://api.pexels.com/videos/search?{q}', headers={'Authorization': CHAVE, 'User-Agent': 'meu-cao-obedece/1.0'})
    for t in range(3):
        try:
            with urllib.request.urlopen(req, timeout=30) as r:
                return json.loads(r.read().decode('utf-8')).get('videos', [])
        except Exception as e:  # noqa: BLE001
            print('  busca falhou', termo, str(e)[:60]); time.sleep(5 * (t + 1))
    return []


def arquivo(v, alvo):
    """Escolhe o arquivo mais próximo da altura-alvo (menor lado)."""
    fs = [f for f in v.get('video_files', []) if f.get('link') and f.get('width') and f.get('height') and 'mp4' in (f.get('file_type') or 'video/mp4')]
    if not fs:
        return None
    fs.sort(key=lambda f: abs(min(f['width'], f['height']) - alvo))
    return fs[0]['link']


def main():
    if not CHAVE:
        sys.exit('Falta o segredo PEXELS_API_KEY.')
    vistos, cand = set(), []
    for cat, termos in BUSCAS:
        achados = []
        for termo in termos:
            for ori in ('portrait', 'landscape'):
                for v in api(termo, ori):
                    if v['id'] in vistos or not (4 <= v.get('duration', 0) <= 45):
                        continue
                    vistos.add(v['id'])
                    achados.append((0 if ori == 'portrait' else 1, v, termo))
                time.sleep(1.2)
        achados.sort(key=lambda x: x[0])
        for _, v, termo in achados[:POR_CATEGORIA.get(cat, 5)]:
            cand.append({'id': str(v['id']), 'titulo': termo + ' — ' + v['url'].rstrip('/').split('/')[-1].replace('-', ' ')[:60],
                         'pagina': v['url'], 'cat': cat, 'autor': (v.get('user') or {}).get('name', ''),
                         'previa': arquivo(v, 360), 'hd': arquivo(v, 1080), 'licenca': 'Pexels (uso comercial ok)'})
        print(cat, len(achados), 'achados')
    ok = []
    for v in cand:
        if not v['previa']:
            continue
        arq = gv.TMP / f"px{v['id']}.mp4"
        dados = gv.get(v['previa'])
        if len(dados) < 20000:
            continue
        arq.write_bytes(dados)
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
    gv.montar(ok, 'Pexels', 'Licença Pexels: uso comercial, inclusive em anúncio, sem crédito obrigatório. Não usar como se fosse cliente real nem sugerir que as pessoas do vídeo recomendam o produto.')
    print('prontos:', len(ok))


if __name__ == '__main__':
    main()
