"""Relatório diário no celular — roda no GitHub, sem depender do Claude.

Monta o resumo do dia a partir de dados/ e envia como notificação pelo app gratuito ntfy
(o tópico fica no segredo NTFY_TOPIC). Guarda um retrato por dia em dados/historico_diario.json
para mostrar a variação de seguidores e views.
"""
import json, os, sys, urllib.request
from datetime import datetime
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(RAIZ / 'scripts'))
import reels  # noqa: E402

D = RAIZ / 'dados'
ler = lambda n, pad: reels.ler_json(D / n, pad)


def montar():
    agora = datetime.now(reels.BRT); hoje = agora.strftime('%Y-%m-%d')
    cfg = reels.CFG
    pub = ler('reels_publicados.json', [])
    reels_hoje = [p for p in pub if (p.get('slot') or '').startswith(hoje)]
    feitos = {p.get('slot') for p in pub}
    faltou = [h for h in cfg.get('horarios', []) if f'{hoje} {h}' not in feitos and h <= agora.strftime('%H:%M')]
    car = ler('carrosseis_feitos.json', [])
    car_hoje = [c for c in car if (c.get('slot') or '').startswith(hoje) and not c.get('erro')]
    car_erro = [c for c in car if (c.get('slot') or '').startswith(hoje) and c.get('erro')]
    met = ler('tiktok_metricas.json', {})
    perfil = met.get('perfil', {}); vids = met.get('videos', [])
    seg = perfil.get('follower_count'); views_tot = sum(v.get('views', 0) for v in vids)
    hist = ler('historico_diario.json', {})
    antes = sorted(k for k in hist if k < hoje)
    ontem = hist[antes[-1]] if antes else None
    hist[hoje] = {'seguidores': seg, 'views_total': views_tot, 'videos': len(vids)}
    reels.gravar_json(D / 'historico_diario.json', dict(sorted(hist.items())[-60:]))
    dif = lambda a, b: '' if (a is None or b is None) else f' ({a - b:+d})'
    melhor = max(vids, key=lambda v: v.get('views', 0), default=None)
    env_hoje = [e for e in ler('tiktok_rascunhos.json', []) if e.get('data') == hoje]
    prontos = ler('tiktok_prontos.json', [])
    pend = [p for p in prontos if not p.get('enviado')]
    fila = ler('tiktok_fila.json', [])
    pesos = ler('tiktok_pesos.json', {})
    bons = sorted(((v, k, x) for k, g in pesos.items() for x, v in g.items()), reverse=True)[:2]
    relp = D / 'tiktok_relatorio.md'
    rel = relp.read_text(encoding='utf-8') if relp.exists() else ''
    anuncio = 'ainda nenhum'
    if '## Candidatos a anúncio' in rel:
        ls = [l for l in rel.split('## Candidatos a anúncio')[-1].split('\n')[1:] if l.startswith('- ')]
        if ls: anuncio = ls[0][2:].strip()
    usados = {u['id'] for u in ler('tiktok_usados.json', [])} | {p['id'] for p in prontos}
    hist_livres = [p.stem for p in (RAIZ / 'tiktok' / 'banco').glob('h*.json') if p.stem not in usados]
    reserva = [i for i in hist_livres if i.startswith('hr')]
    usados_ig = {p['roteiro'] for p in pub}
    reels_livres = [p for p in (RAIZ / 'reels' / 'banco').glob('*.json') if json.loads(p.read_text(encoding='utf-8'))['id'] not in usados_ig]
    por_dia = cfg.get('tiktok_por_lote', 3) * len(cfg.get('tiktok_lotes', [1, 2, 3]))
    alerta = []
    if faltou: alerta.append('Reels sem post: ' + ', '.join(faltou))
    if car_erro: alerta.append(f'{len(car_erro)} carrossel com erro')
    if fila: alerta.append(f'{len(fila)} vídeo(s) esperando vaga nos rascunhos — poste os pendentes')
    if len(hist_livres) < por_dia: alerta.append('poucas histórias novas (o gerador reserva vai entrar)')
    if any(e['id'].startswith('hr') for e in env_hoje): alerta.append('hoje saíram histórias do gerador reserva (roteirista parado?)')
    if not met: alerta.append('métricas do TikTok ainda não coletadas')
    linhas = [
        f"📱 TikTok: {seg if seg is not None else 'sem dado'} seguidores{dif(seg, (ontem or {}).get('seguidores'))} · {views_tot} views no total{dif(views_tot, (ontem or {}).get('views_total'))}",
        (f"🎬 Melhor vídeo: {melhor.get('views', 0)} views — {melhor.get('roteiro') or 'vídeo manual'}" if melhor else '🎬 Melhor vídeo: sem dado ainda'),
        f"📤 Rascunhos hoje: {len(env_hoje)} enviados · {len(pend)} prontos esperando o próximo lote",
        f"📸 Instagram: {len(reels_hoje)} Reels + {len(car_hoje)} carrosséis hoje",
        '🏆 Funcionando: ' + (', '.join(f'{k} {x}' for v, k, x in bons if v > 0) or 'ainda aprendendo (poucos vídeos)'),
        f'💰 Candidato a anúncio: {anuncio}',
        f"📦 Estoque: {len(hist_livres)} histórias (~{len(hist_livres) // max(por_dia, 1)} dias) e {len(reels_livres)} Reels" + (f' · {len(reserva)} da reserva' if reserva else ''),
    ]
    yt = ler('youtube_metricas.json', {})
    yt_hoje = [e for e in ler('youtube_enviados.json', []) if e.get('data') == hoje]
    if yt or yt_hoje:
        privados = sum(1 for v in yt.get('videos', []) if v.get('privacidade') == 'private')
        linhas.insert(4, f"▶️ YouTube: {yt.get('canal', {}).get('subscriberCount', '?')} inscritos · {sum(v['views'] for v in yt.get('videos', []))} views · {len(yt_hoje)} Shorts hoje" + (f' · {privados} privados p/ publicar' if privados else ''))
    if alerta: linhas.append('⚠️ ' + ' · '.join(alerta))
    linhas.append('✅ Amanhã: 1 vídeo a cada 2h (6h30 até 22h30) — poste quando chegar a notificação do TikTok, colando a legenda do cartão de cima da página, e responda os comentários.')
    return f"📊 Meu Cão Obedece — {agora.strftime('%d/%m')}", '\n'.join(linhas)


def enviar(titulo, texto):
    topico = os.environ.get('NTFY_TOPIC', '').strip()
    if not topico:
        print('(sem NTFY_TOPIC — só mostrando)'); return
    corpo = json.dumps({'topic': topico, 'title': titulo, 'message': texto, 'tags': ['dog'],
                        'click': 'https://kaicjackson88-ui.github.io/meucaoobedece-postss/legendas.html'}).encode()
    req = urllib.request.Request('https://ntfy.sh/', data=corpo, headers={'Content-Type': 'application/json'}, method='POST')
    with urllib.request.urlopen(req, timeout=30) as r:
        print('notificação enviada', r.status)


if __name__ == '__main__':
    t, m = montar()
    print(t); print(m)
    if '--teste' not in sys.argv:
        ult = D / 'relatorio_ultimo.txt'
        try:
            antes = datetime.fromisoformat(ult.read_text().strip())
        except Exception:
            antes = None
        if antes and (datetime.now(reels.BRT) - antes).total_seconds() < 12 * 3600 and '--forcar' not in sys.argv:
            print('relatório já enviado há menos de 12h — não repito')
        else:
            enviar(t, m); ult.write_text(datetime.now(reels.BRT).isoformat())
