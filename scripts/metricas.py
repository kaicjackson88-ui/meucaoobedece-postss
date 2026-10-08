"""Coleta métricas dos Reels e carrosséis publicados e calcula os pesos que guiam a escolha dos próximos roteiros.

Saídas: dados/metricas.json, dados/pesos.json, dados/relatorio.md
"""
import json, math, statistics, sys
from datetime import datetime, timedelta, timezone
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(RAIZ / 'scripts'))
from postar import chamar  # noqa: E402

DADOS = RAIZ / 'dados'
METRICAS_REELS = ['views', 'reach', 'likes', 'comments', 'shares', 'saved', 'total_interactions', 'ig_reels_avg_watch_time', 'ig_reels_video_view_total_time']
METRICAS_BASICAS = ['reach', 'likes', 'comments', 'shares', 'saved']


def ler(p, padrao):
    return json.loads(p.read_text(encoding='utf-8')) if p.exists() else padrao


def insights(media_id, lista):
    for tentativa in [lista, METRICAS_BASICAS, ['reach', 'likes', 'comments']]:
        try:
            r = chamar('GET', f'{media_id}/insights', {'metric': ','.join(tentativa)})
            out = {}
            for m in r.get('data', []):
                v = m.get('values', [{}])[0].get('value') if m.get('values') else m.get('total_value', {}).get('value')
                out[m['name']] = v or 0
            return out
        except RuntimeError as e:
            erro = str(e)
    print('  sem métricas para', media_id, '-', erro)
    return None


def pontuar(m, dur):
    reach = max(1, m.get('reach', 0))
    eng = (m.get('shares', 0) * 4 + m.get('saved', 0) * 3 + m.get('comments', 0) * 2 + m.get('likes', 0)) / reach * 100
    ret = 0
    if m.get('ig_reels_avg_watch_time') and dur:
        ret = min(1, m['ig_reels_avg_watch_time'] / 1000 / dur) * 10
    return round(eng + ret, 3)


def main():
    agora = datetime.now(timezone.utc)
    reels = ler(DADOS / 'reels_publicados.json', [])
    met = ler(DADOS / 'metricas.json', {})
    itens = []
    for r in reels:
        if not r.get('media_id'): continue
        if agora - datetime.fromisoformat(r['publicado_em']) < timedelta(hours=20): continue
        itens.append(('reel', r['media_id'], r))
    for pj in sorted((RAIZ / 'posts').glob('*/publicado.json')):
        p = json.loads(pj.read_text(encoding='utf-8')); info = json.loads((pj.parent / 'post.json').read_text(encoding='utf-8'))
        if agora - datetime.fromisoformat(p['publicado_em']) < timedelta(hours=20): continue
        itens.append(('carrossel', p['media_id'], {'formato': 'carrossel', 'tema': pj.parent.name.split('-')[-1], 'gancho_tipo': '', 'roteiro': pj.parent.name, 'link': p.get('link')}))
    for tipo, mid, r in itens:
        antigo = met.get(mid, {})
        if antigo.get('coletado_em') and agora - datetime.fromisoformat(antigo['coletado_em']) < timedelta(hours=20):
            continue
        m = insights(mid, METRICAS_REELS if tipo == 'reel' else METRICAS_BASICAS)
        if m is None: continue
        m.update({'tipo': tipo, 'roteiro': r.get('roteiro'), 'formato': r.get('formato'), 'gancho_tipo': r.get('gancho_tipo', ''), 'tema': r.get('tema', ''), 'estilo': r.get('estilo', ''),
                  'duracao': r.get('duracao'), 'link': r.get('link'), 'coletado_em': agora.isoformat()})
        m['pontuacao'] = pontuar(m, r.get('duracao'))
        met[mid] = m
        print(f"  {r.get('roteiro')}: alcance {m.get('reach')} · pontos {m['pontuacao']}")
    (DADOS).mkdir(exist_ok=True)
    (DADOS / 'metricas.json').write_text(json.dumps(met, ensure_ascii=False, indent=1), encoding='utf-8')
    # pesos: quanto cada formato/gancho/tema fica acima da média (encolhido quando há poucos dados)
    so_reels = [m for m in met.values() if m.get('tipo') == 'reel']
    pesos = {'atualizado': agora.isoformat(), 'n_reels': len(so_reels)}
    if len(so_reels) >= 3:
        notas = [m['pontuacao'] for m in so_reels]; mu = statistics.mean(notas); sd = statistics.pstdev(notas) or 1
        for campo in ['formato', 'gancho_tipo', 'tema', 'estilo']:
            grupos = {}
            for m in so_reels: grupos.setdefault(m.get(campo) or '?', []).append(m['pontuacao'])
            pesos[campo] = {k: round((statistics.mean(v) - mu) / sd * len(v) / (len(v) + 3), 3) for k, v in grupos.items()}
    (DADOS / 'pesos.json').write_text(json.dumps(pesos, ensure_ascii=False, indent=1), encoding='utf-8')
    # relatório legível
    linhas = ['# Relatório de desempenho', f'Atualizado em {agora.astimezone(timezone(timedelta(hours=-3))).strftime("%d/%m/%Y %H:%M")} (Brasília)', '']
    ordem = sorted(met.values(), key=lambda m: -m['pontuacao'])
    linhas += ['| Post | Tipo | Formato | Alcance | Views | Curtidas | Coment. | Compart. | Salvos | Pontos |', '|---|---|---|---|---|---|---|---|---|---|']
    for m in ordem:
        linhas.append(f"| [{m.get('roteiro')}]({m.get('link')}) | {m.get('tipo')} | {m.get('formato')} | {m.get('reach', 0)} | {m.get('views', '-')} | {m.get('likes', 0)} | {m.get('comments', 0)} | {m.get('shares', 0)} | {m.get('saved', 0)} | {m['pontuacao']} |")
    if pesos.get('formato'):
        linhas += ['', '## Pesos atuais (positivo = o robô vai usar mais)', '```', json.dumps({k: pesos[k] for k in ['formato', 'gancho_tipo', 'tema']}, ensure_ascii=False, indent=1), '```']
    (DADOS / 'relatorio.md').write_text('\n'.join(linhas) + '\n', encoding='utf-8')
    print('ok:', len(met), 'posts com métricas')


if __name__ == '__main__':
    try:
        main()
    except RuntimeError as e:
        sys.exit(str(e))
