"""Aprende com o TikTok: lê views/curtidas/comentários/compartilhamentos de cada vídeo do perfil,
liga cada vídeo à história que o gerou (pela legenda), calcula o que funciona e escreve:

  dados/tiktok_metricas.json   — números de cada vídeo
  dados/tiktok_pesos.json      — peso de cada característica (tema, curiosidade, chat, cenário, elenco…)
  dados/tiktok_relatorio.md    — resumo legível + candidatos a anúncio (lido pelo roteirista toda noite)

Precisa dos escopos video.list e user.info.stats (reconectar em docs/conectar.html depois de liberar no app).
"""
import json, math, re, sys, unicodedata
from datetime import datetime, timezone
from pathlib import Path
from statistics import median

RAIZ = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(RAIZ / 'scripts'))
import reels  # noqa: E402
import tiktok_rascunho as tt  # noqa: E402

DADOS = RAIZ / 'dados'
CAMPOS = 'id,title,video_description,create_time,duration,view_count,like_count,comment_count,share_count,share_url'


def norm(s):
    s = unicodedata.normalize('NFD', s or '')
    return re.sub(r'[^a-z0-9]', '', ''.join(c for c in s if unicodedata.category(c) != 'Mn').lower())


def listar_videos(at):
    vids, cursor = [], None
    for _ in range(15):
        body = {'max_count': 20}
        if cursor: body['cursor'] = cursor
        r = tt.http('POST', f'https://open.tiktokapis.com/v2/video/list/?fields={CAMPOS}', headers={'Authorization': f'Bearer {at}'}, json_body=body)
        d = r.get('data', {})
        vids += d.get('videos', [])
        if not d.get('has_more'): break
        cursor = d.get('cursor')
    return vids


def perfil(at):
    try:
        r = tt.http('GET', 'https://open.tiktokapis.com/v2/user/info/?fields=display_name,follower_count,likes_count,video_count', headers={'Authorization': f'Bearer {at}'})
        return r.get('data', {}).get('user', {})
    except RuntimeError as e:
        print('perfil indisponível:', e); return {}


def caracteristicas(rot):
    cenas = rot.get('cenas', [])
    f = {'tema': rot.get('tema', '?'),
         'curiosidade': 'sim' if any(c['tipo'] == 'curiosidade' for c in cenas) else 'nao',
         'chat': 'sim' if any(c['tipo'] == 'chat' for c in cenas) else 'nao',
         'tamanho': 'curta' if len(cenas) <= 8 else ('media' if len(cenas) <= 10 else 'longa')}
    for c in cenas:
        if c['tipo'] == 'historia':
            f.setdefault('cenarios', set()).add(c.get('cenario', 'sala'))
            for e in c.get('elenco', []): f.setdefault('elenco', set()).add(e.get('quem'))
    return f


def main():
    if not tt.TOKEN_ARQ.exists():
        sys.exit('TikTok ainda não conectado.')
    at = tt.access_token()
    try:
        vids = listar_videos(at)
    except RuntimeError as e:
        sys.exit(f'Sem permissão de leitura ainda (libere video.list no app e reconecte): {e}')
    user = perfil(at)
    banco = {}
    for p in (RAIZ / 'tiktok' / 'banco').glob('*.json'):
        r = json.loads(p.read_text(encoding='utf-8')); banco[r['id']] = r
    chaves = {rid: norm(r.get('legenda', '').split('\n')[0])[:40] for rid, r in banco.items()}
    linhas = []
    for v in vids:
        desc = norm((v.get('video_description') or '') + (v.get('title') or ''))
        rid = next((rid for rid, k in chaves.items() if k and k[:30] in desc), None)
        views = v.get('view_count', 0) or 0
        eng = (v.get('like_count', 0) + 2 * v.get('comment_count', 0) + 3 * v.get('share_count', 0)) / max(views, 1)
        linhas.append({'video': v.get('id'), 'roteiro': rid, 'views': views, 'curtidas': v.get('like_count', 0), 'comentarios': v.get('comment_count', 0),
                       'compart': v.get('share_count', 0), 'engaj': round(eng, 4), 'duracao': v.get('duration'), 'link': v.get('share_url'),
                       'criado': datetime.fromtimestamp(v.get('create_time', 0), timezone.utc).isoformat()})
    reels.gravar_json(DADOS / 'tiktok_metricas.json', {'perfil': user, 'atualizado': datetime.now(reels.BRT).isoformat(), 'videos': linhas})
    # só aprende com vídeos que já tiveram tempo de rodar (24h+)
    agora = datetime.now(timezone.utc)
    maduros = [l for l in linhas if l['roteiro'] and (agora - datetime.fromisoformat(l['criado'])).total_seconds() > 86400]
    pesos = {}
    if maduros:
        nota = lambda l: math.log10(l['views'] + 10) + 4 * l['engaj']  # views pesam mais; engajamento desempata
        media = sum(nota(l) for l in maduros) / len(maduros)
        grupos = {}
        for l in maduros:
            for k, val in caracteristicas(banco[l['roteiro']]).items():
                for x in (val if isinstance(val, set) else [val]):
                    grupos.setdefault(k, {}).setdefault(x, []).append(nota(l))
        for k, g in grupos.items():
            # média encolhida (poucos vídeos = peso perto de zero)
            pesos[k] = {x: round((sum(n) / len(n) - media) * len(n) / (len(n) + 3), 3) for x, n in g.items()}
    reels.gravar_json(DADOS / 'tiktok_pesos.json', pesos)
    ordem = sorted([l for l in linhas if l['views']], key=lambda l: -l['views'])
    med_v = median([l['views'] for l in ordem]) if ordem else 0
    med_e = median([l['engaj'] for l in ordem]) if ordem else 0
    anuncio = [l for l in ordem if l['views'] >= max(500, 2 * med_v) and l['engaj'] >= med_e]
    rel = [f"# TikTok — o que está funcionando ({datetime.now(reels.BRT).strftime('%d/%m %H:%M')})", '',
           f"Seguidores: {user.get('follower_count', '?')} · curtidas no perfil: {user.get('likes_count', '?')} · vídeos: {user.get('video_count', len(linhas))}",
           f"Mediana de views: {int(med_v)} · mediana de engajamento: {med_e:.3f}", '', '## Top 5']
    rel += [f"- {l['views']} views · eng {l['engaj']:.3f} · {l['roteiro'] or '(vídeo manual)'} · {l['link']}" for l in ordem[:5]]
    rel += ['', '## Piores 5'] + [f"- {l['views']} views · {l['roteiro'] or '(vídeo manual)'}" for l in ordem[-5:]]
    rel += ['', '## Pesos (positivo = repetir mais, negativo = evitar)']
    for k, g in pesos.items():
        rel.append(f"- {k}: " + ', '.join(f"{x} {v:+.2f}" for x, v in sorted(g.items(), key=lambda i: -i[1])))
    rel += ['', '## Candidatos a anúncio (2x a mediana de views e engajamento acima da mediana)']
    rel += [f"- {l['roteiro'] or l['video']} · {l['views']} views · {l['link']}" for l in anuncio] or ['- ainda nenhum']
    (DADOS / 'tiktok_relatorio.md').write_text('\n'.join(rel) + '\n', encoding='utf-8')
    print('\n'.join(rel))


if __name__ == '__main__':
    try: main()
    except RuntimeError as e: sys.exit(str(e))
