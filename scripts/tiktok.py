"""Lote de vídeos para o TikTok.

python scripts/tiktok.py lote <quantidade> [--ids t001,t002]
  Renderiza roteiros de tiktok/banco/ ainda não usados e cria um Release no GitHub
  com os MP4s e um arquivo de legendas, pronto para agendar no TikTok Studio.
"""
import json, shutil, subprocess, sys, tempfile
from datetime import datetime
from pathlib import Path
RAIZ = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(RAIZ / 'scripts'))
import reels  # noqa: E402

BANCO = RAIZ / 'tiktok' / 'banco'
USADOS = RAIZ / 'dados' / 'tiktok_usados.json'


def main():
    a = sys.argv[1:]
    n = int(a[1]) if len(a) > 1 and a[1].isdigit() else 21
    usados = reels.ler_json(USADOS, [])
    banco = {json.loads(p.read_text(encoding='utf-8'))['id']: json.loads(p.read_text(encoding='utf-8')) for p in sorted(BANCO.glob('*.json'))}
    if '--ids' in a:
        ids = [x.strip() for x in a[a.index('--ids') + 1].split(',') if x.strip()]
    else:
        ids = [i for i in banco if i not in {u['id'] for u in usados}][:n]
    if not ids:
        print('⚠️ Nenhum roteiro de TikTok disponível.'); return
    saida = Path(tempfile.mkdtemp(prefix='tiktok-'))
    legendas = []
    for k, rid in enumerate(ids, 1):
        rot = banco.get(rid) or json.loads((RAIZ / rid).read_text(encoding='utf-8'))  # aceita caminho .json (ex.: anúncios)
        print(f'[{k}/{len(ids)}] {rid}', flush=True)
        pasta = saida / rid
        try:
            reels.produzir(rot, pasta)
        except Exception as e:
            print('  falhou:', e); continue
        nome = f'{k:02d}-{rid}.mp4'
        shutil.move(pasta / 'reel.mp4', saida / nome)
        legendas.append(f"=== {nome} ===\n{rot['legenda']}\n\n{rot.get('hashtags', '')}\n")
        if rid in banco: usados.append({'id': rid, 'quando': datetime.now(reels.BRT).isoformat()})
    (saida / 'legendas.txt').write_text('\n'.join(legendas), encoding='utf-8')
    tag = 'tiktok-' + datetime.now(reels.BRT).strftime('%Y%m%d-%H%M')
    notas = ('Vídeos prontos para o TikTok. Baixe pelo celular ou agende no TikTok Studio (computador) '
             'até 10 dias à frente. As legendas de cada vídeo estão em legendas.txt.\n\n' + '\n'.join(legendas))
    (saida / 'notas.md').write_text(notas, encoding='utf-8')
    arquivos = sorted(str(p) for p in saida.glob('*.mp4')) + [str(saida / 'legendas.txt')]
    subprocess.run(['gh', 'release', 'create', tag, *arquivos, '--title', f'TikTok — lote de {datetime.now(reels.BRT).strftime("%d/%m")}',
                    '--notes-file', str(saida / 'notas.md'), '--latest=false'], cwd=RAIZ, check=True)
    reels.gravar_json(USADOS, usados)
    print('Release criado:', tag)


if __name__ == '__main__':
    main()
