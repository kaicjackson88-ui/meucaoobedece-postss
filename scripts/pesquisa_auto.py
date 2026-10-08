"""Pesquisador autônomo (sem Claude): descobre o que está funcionando no nicho e grava dados/tendencias_auto.md.

Fontes oficiais e públicas:
  1. Instagram Business Discovery (API oficial da Meta): posts públicos dos perfis de referência em
     reels/config.json -> "referencias_ig" — curtidas, comentários, legenda, hashtags, tipo e data.
     Acha os posts "fora da curva" de cada perfil (2x a mediana dele) = o que viralizou.
  2. Google Notícias (RSS): temas e datas do momento no nicho pet.
  3. YouTube (opcional, segredo YT_API_KEY): Shorts do nicho mais vistos nos últimos 30 dias.
Depois a IA gratuita do GitHub cruza tudo com os pesos do nosso perfil e escreve ideias acionáveis.
"""
import json, os, re, sys, urllib.parse, urllib.request
import xml.etree.ElementTree as ET
from collections import Counter
from datetime import datetime, timedelta, timezone
from pathlib import Path
from statistics import median

RAIZ = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(RAIZ / 'scripts'))
import reels  # noqa: E402
import ia_gratis  # noqa: E402

D = RAIZ / 'dados'
CFG = reels.CFG
BUSCAS = CFG.get('busca_noticias', ['cachorro comportamento', 'adestramento cães', 'pet tendência Brasil', 'cachorro fogos', 'cachorro calor'])


def instagram():
    refs = [u.strip().lstrip('@') for u in CFG.get('referencias_ig', []) if u.strip()]
    if not refs or not os.environ.get('IG_TOKEN'):
        return [], 'sem perfis de referência ou sem IG_TOKEN'
    try:
        from postar import chamar, conta_instagram
        ig = conta_instagram()
    except Exception as e:
        return [], f'Instagram indisponível: {e}'
    posts = []
    for u in refs[:25]:
        campos = (f'business_discovery.username({u}){{username,followers_count,media.limit(30)'
                  '{caption,like_count,comments_count,media_type,media_product_type,timestamp,permalink}}')
        try:
            r = chamar('GET', ig, {'fields': campos}).get('business_discovery', {})
        except Exception as e:
            print('  referência falhou', u, str(e)[:120]); continue
        media = r.get('media', {}).get('data', [])
        if not media: continue
        eng = [m.get('like_count', 0) + 2 * m.get('comments_count', 0) for m in media]
        med = median(eng) or 1
        for m, e in zip(media, eng):
            posts.append({'perfil': u, 'seguidores': r.get('followers_count'), 'engaj': e, 'vezes_mediana': round(e / med, 2),
                          'tipo': m.get('media_product_type') or m.get('media_type'), 'data': (m.get('timestamp') or '')[:10],
                          'legenda': (m.get('caption') or '')[:600], 'link': m.get('permalink')})
    return posts, f'{len(refs)} perfis consultados'


def noticias():
    out = []
    for q in BUSCAS:
        url = 'https://news.google.com/rss/search?' + urllib.parse.urlencode({'q': q + ' when:30d', 'hl': 'pt-BR', 'gl': 'BR', 'ceid': 'BR:pt-419'})
        try:
            with urllib.request.urlopen(urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'}), timeout=30) as r:
                raiz = ET.fromstring(r.read())
            for it in raiz.iter('item'):
                out.append({'busca': q, 'titulo': it.findtext('title'), 'link': it.findtext('link'), 'data': it.findtext('pubDate')})
                if sum(1 for x in out if x['busca'] == q) >= 8: break
        except Exception as e:
            print('  notícias falharam', q, e)
    return out


def youtube():
    chave = os.environ.get('YT_API_KEY', '').strip()
    if not chave: return []
    depois = (datetime.now(timezone.utc) - timedelta(days=30)).strftime('%Y-%m-%dT%H:%M:%SZ')
    out = []
    for q in ['adestramento cachorro', 'cachorro latindo', 'xixi cachorro lugar certo', 'história cachorro animação']:
        p = {'part': 'snippet', 'q': q, 'type': 'video', 'videoDuration': 'short', 'order': 'viewCount', 'regionCode': 'BR',
             'relevanceLanguage': 'pt', 'publishedAfter': depois, 'maxResults': 10, 'key': chave}
        try:
            with urllib.request.urlopen('https://www.googleapis.com/youtube/v3/search?' + urllib.parse.urlencode(p), timeout=30) as r:
                for it in json.loads(r.read().decode()).get('items', []):
                    out.append({'busca': q, 'titulo': it['snippet']['title'], 'canal': it['snippet']['channelTitle'],
                                'link': 'https://youtu.be/' + it['id'].get('videoId', '')})
        except Exception as e:
            print('  youtube falhou', q, e)
    return out


def main():
    posts, st_ig = instagram()
    news = noticias()
    yt = youtube()
    top = sorted([p for p in posts if p['vezes_mediana'] >= 2], key=lambda p: -p['vezes_mediana'])[:25]
    tags_top = Counter(t.lower() for p in top for t in re.findall(r'#\w+', p['legenda']))
    tags_todos = Counter(t.lower() for p in posts for t in re.findall(r'#\w+', p['legenda']))
    bruto = {'quando': datetime.now(reels.BRT).isoformat(), 'instagram': st_ig, 'top_posts': top,
             'hashtags_top': tags_top.most_common(30), 'hashtags_geral': tags_todos.most_common(30), 'noticias': news[:40], 'youtube': yt[:30]}
    reels.gravar_json(D / 'pesquisa_bruta.json', bruto)
    # sem IA: mede quais dores estão em alta nas manchetes e posts virais (o gerador reserva dá prioridade a elas)
    CHAVES = {'campainha': ['latido', 'late', 'campainha', 'entregador', 'barulho'], 'xixi': ['xixi', 'urina', 'fezes', 'banheiro'],
              'visita': ['pula', 'pular', 'visita'], 'guia': ['guia', 'passeio', 'puxa'], 'sozinho': ['sozinho', 'ansiedade', 'separação', 'rói', 'destr'],
              'chamado': ['chamado', 'fugiu', 'foge', 'obedece', 'comando'], 'mesa': ['comida', 'mesa', 'rouba', 'come ']}
    textos = ' '.join([(n['titulo'] or '') for n in news] + [p['legenda'] for p in top] + [y['titulo'] for y in yt]).lower()
    cont = {d: sum(textos.count(k) for k in ks) for d, ks in CHAVES.items()}
    tot = sum(cont.values()) or 1
    reels.gravar_json(D / 'tendencia_dores.json', {d: round(v / tot, 3) for d, v in cont.items()})
    print('dores em alta:', cont)
    pesos = reels.ler_json(D / 'tiktok_pesos.json', {})
    rel = (D / 'tiktok_relatorio.md').read_text(encoding='utf-8')[:2500] if (D / 'tiktok_relatorio.md').exists() else ''
    resumo = {'posts_que_viralizaram_nos_perfis_de_referencia': [{k: p[k] for k in ('perfil', 'vezes_mediana', 'tipo', 'legenda')} for p in top[:15]],
              'hashtags_nos_virais': tags_top.most_common(20), 'manchetes_pet_30_dias': [n['titulo'] for n in news[:25]],
              'youtube_shorts_mais_vistos': [y['titulo'] for y in yt[:15]]}
    sistema = ('Você é um estrategista de conteúdo para TikTok e Instagram no nicho de adestramento de cães no Brasil. '
               'O perfil faz histórias animadas 2D (tutor + cão, diálogo, problema → vergonha → virada "ninguém ensinou" → solução de 15 min/dia → quiz). '
               'Extraia PADRÕES (nunca copie texto de ninguém). Não invente números. Responda só JSON.')
    pedido = ('Dados coletados hoje:\n' + json.dumps(resumo, ensure_ascii=False)[:9000] +
              '\n\nO que já funciona no NOSSO perfil (pesos: positivo = bom):\n' + json.dumps(pesos, ensure_ascii=False)[:1500] + '\n' + rel[:1200] +
              '\n\nDevolva JSON com as chaves: "ideias" (lista de 5 objetos {"titulo","dor","gancho_exemplo","formato","por_que"} — premissas NOVAS de histórias), '
              '"hashtags" (objeto tema -> lista de 6 hashtags; temas: latido, xixi, pulo, guia, ansiedade, chamado, comida), '
              '"estilo_legenda" (lista de 3 regras curtas + 2 exemplos no tom do perfil), "datas_temas" (lista curta), "evitar" (lista curta), '
              '"resumo" (2 frases sobre o que os dados indicam).')
    try:
        an = ia_gratis.json_de(ia_gratis.perguntar(sistema, pedido, max_tokens=2500, temperatura=0.6, json_saida=True))
    except Exception as e:
        print('análise da IA falhou:', e); an = {}
    reels.gravar_json(D / 'tendencias_auto.json', an)
    L = [f"# Pesquisa automática ({datetime.now(reels.BRT).strftime('%d/%m %H:%M')})", '', f"Fontes: Instagram ({st_ig}), {len(news)} manchetes, {len(yt)} Shorts.", '',
         '## Resumo', an.get('resumo', '(sem análise da IA hoje)'), '', '## O que testar esta semana']
    for i in an.get('ideias', []):
        L.append(f"- **{i.get('titulo')}** ({i.get('dor')}, {i.get('formato')}): \"{i.get('gancho_exemplo')}\" — {i.get('por_que')}")
    L += ['', '## Hashtags recomendadas por tema'] + [f"- {k}: {' '.join(v)}" for k, v in (an.get('hashtags') or {}).items()]
    L += ['', '## Estilo de legenda que está funcionando'] + [f'- {x}' for x in an.get('estilo_legenda', [])]
    L += ['', '## Datas e temas do momento'] + [f'- {x}' for x in an.get('datas_temas', [])]
    L += ['', '## Evitar'] + [f'- {x}' for x in an.get('evitar', [])]
    virais = [f"- @{p['perfil']} · {p['vezes_mediana']}x a mediana · {p['tipo']} · {p['link']}" for p in top[:10]]
    L += ['', '## Posts que viralizaram nos perfis de referência'] + (virais or ['- (adicione perfis em referencias_ig no reels/config.json)'])
    L += ['', '## Fontes'] + [f"- {n['titulo']} — {n['link']}" for n in news[:10]]
    (D / 'tendencias_auto.md').write_text('\n'.join(L) + '\n', encoding='utf-8')
    print('\n'.join(L[:30]))


if __name__ == '__main__':
    main()
