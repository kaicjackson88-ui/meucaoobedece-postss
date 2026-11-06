"""Posta no Instagram um Reels que já chega pronto (ex.: histórias animadas feitas fora do gerador automático).

python scripts/postar_pronto.py mco1
  -> lê prontos/mco1.json {"id", "video_url", "legenda", "capa_url"(opcional)}, publica e registra em dados/reels_publicados.json
"""
import json
import sys
import time
from datetime import datetime, timezone, timedelta
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(RAIZ / 'scripts'))
BRT = timezone(timedelta(hours=-3))


def main(alvo):
    from postar import chamar, conta_instagram
    item = json.loads((RAIZ / 'prontos' / f'{alvo}.json').read_text(encoding='utf-8'))
    pub_path = RAIZ / 'dados' / 'reels_publicados.json'
    publicados = json.loads(pub_path.read_text(encoding='utf-8')) if pub_path.exists() else []
    if any(p.get('roteiro') == item['id'] for p in publicados):
        print(f"{item['id']} já foi publicado. Nada a fazer."); return
    ig = conta_instagram()
    corpo = {'media_type': 'REELS', 'video_url': item['video_url'], 'caption': item['legenda'], 'share_to_feed': 'true'}
    if item.get('capa_url'):
        corpo['cover_url'] = item['capa_url']
    cid = chamar('POST', f'{ig}/media', corpo)['id']
    for _ in range(60):
        st = chamar('GET', cid, {'fields': 'status_code,status'})
        if st.get('status_code') == 'FINISHED':
            break
        if st.get('status_code') in ('ERROR', 'EXPIRED'):
            raise RuntimeError(f"A Meta recusou o vídeo: {st.get('status')}")
        time.sleep(10)
    else:
        raise RuntimeError('O vídeo demorou demais para processar.')
    mid = chamar('POST', f'{ig}/media_publish', {'creation_id': cid})['id']
    link = chamar('GET', mid, {'fields': 'permalink'}).get('permalink', '')
    publicados.append({'slot': datetime.now(BRT).strftime('%Y-%m-%d %H:%M'), 'roteiro': item['id'], 'formato': 'historia-animada',
                       'tema': item.get('tema', ''), 'media_id': mid, 'link': link, 'publicado_em': datetime.now(timezone.utc).isoformat()})
    pub_path.write_text(json.dumps(publicados, ensure_ascii=False, indent=1), encoding='utf-8')
    print('Publicado!', link)


if __name__ == '__main__':
    if len(sys.argv) < 2:
        sys.exit(__doc__)
    main(sys.argv[1])
