"""Gestor de anúncios da Meta (Marketing API) — Meu Cão Obedece.
Comandos (python scripts/anuncios_meta.py <comando> [arquivo de campanha]):
  checar     → permissões da chave, contas de anúncio, páginas, Instagram e pixels (dados/meta_anuncios_status.json)
  montar     → sobe as mídias e cria campanha + conjunto + anúncios, tudo PAUSADO (dados/meta_campanha_<id>.json)
  ativar     → liga campanha, conjunto e anúncios (só quando o dono autorizar o gasto)
  pausar     → pausa a campanha inteira
  relatorio  → números por anúncio, aplica as regras de corte (pausa automática) e avisa no celular
Regras de autonomia: o robô só PAUSA (perdedores e limite de gasto). Nunca aumenta orçamento nem cria gasto novo sozinho.
Usa o segredo META_ADS_TOKEN (usuário do sistema com ads_management/ads_read); se não existir, tenta o IG_TOKEN. Nunca imprime a chave."""
import base64, json, os, sys, time, urllib.error, urllib.parse, urllib.request
from datetime import datetime, timezone, timedelta
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[1]
DADOS = RAIZ / 'dados'
API = 'https://graph.facebook.com/v26.0'
TOKEN = (os.environ.get('META_ADS_TOKEN') or os.environ.get('IG_TOKEN') or '').strip()
BRT = timezone(timedelta(hours=-3))
STATUS = DADOS / 'meta_anuncios_status.json'
# economia do produto (skill gestor-trafego): líquido ≈ R$31,18; com impostos da Meta o empate fica ≈ R$27,80
ALVO_CPA, TETO_CPA = 28.0, 42.0


# ---------------- chamada à API ----------------
def api(metodo, caminho, params=None):
    p = {k: (json.dumps(v, ensure_ascii=False) if isinstance(v, (dict, list)) else v) for k, v in (params or {}).items()}
    p.setdefault('access_token', TOKEN)
    corpo = urllib.parse.urlencode(p).encode()
    url = caminho if caminho.startswith('http') else f'{API}/{caminho}'
    req = urllib.request.Request(f'{url}?{corpo.decode()}') if metodo == 'GET' else urllib.request.Request(url, data=corpo, method=metodo)
    for t in range(3):
        try:
            with urllib.request.urlopen(req, timeout=120) as r:
                return json.loads(r.read().decode())
        except urllib.error.HTTPError as e:
            txt = e.read().decode(errors='replace')
            try:
                err = json.loads(txt).get('error', {})
            except ValueError:
                err = {'message': txt[:300]}
            if err.get('code') in (1, 2, 17, 613) and t < 2:   # limite/instabilidade: espera e tenta de novo
                time.sleep(20 * (t + 1)); continue
            raise RuntimeError(f"Meta recusou {caminho.split('?')[0]}: {err.get('message')} "
                               f"(código {err.get('code')}/{err.get('error_subcode')}) {err.get('error_user_msg') or ''}") from None
    raise RuntimeError(f'Meta não respondeu em {caminho}')


def _try(f, padrao=None):
    try:
        return f()
    except Exception as e:  # noqa: BLE001
        print('  aviso:', str(e)[:250]); return padrao


def ler(p, padrao=None):
    return json.loads(Path(p).read_text(encoding='utf-8')) if Path(p).exists() else padrao


def gravar(p, obj):
    Path(p).parent.mkdir(exist_ok=True)
    Path(p).write_text(json.dumps(obj, ensure_ascii=False, indent=1), encoding='utf-8')


def avisar(titulo, texto):
    topico = os.environ.get('NTFY_TOPIC', '').strip()
    if not topico:
        return
    corpo = json.dumps({'topic': topico, 'title': titulo, 'message': texto[:3500], 'tags': ['moneybag']}).encode()
    _try(lambda: urllib.request.urlopen(urllib.request.Request('https://ntfy.sh/', data=corpo, headers={'Content-Type': 'application/json'}, method='POST'), timeout=30))


# ---------------- checar ----------------
def checar(_=None):
    perms = _try(lambda: api('GET', 'me/permissions'), {}) or {}
    concedidas = sorted(p['permission'] for p in perms.get('data', []) if p.get('status') == 'granted')
    print('Permissões concedidas:', ', '.join(concedidas) or '(nenhuma lida)')
    falta = [p for p in ('ads_management', 'ads_read') if p not in concedidas]
    print('Faltam para anúncios:', ', '.join(falta) or 'nada — dá para gerenciar anúncios')
    r = _try(lambda: api('GET', 'me/adaccounts', {'fields': 'id,name,currency,account_status,amount_spent,funding_source_details', 'limit': 50}), {}) or {}
    contas = [{'id': c['id'], 'nome': c.get('name'), 'moeda': c.get('currency'), 'status': c.get('account_status'), 'gasto': c.get('amount_spent'),
               'pagamento': (c.get('funding_source_details') or {}).get('display_string')} for c in r.get('data', [])]
    for c in contas:
        print('Conta de anúncio:', c)
    r = _try(lambda: api('GET', 'me/accounts', {'fields': 'id,name,access_token,instagram_business_account{id,username}'}), {}) or {}
    paginas = [{'id': p['id'], 'nome': p.get('name'), 'ig': (p.get('instagram_business_account') or {}).get('id'),
                'ig_user': (p.get('instagram_business_account') or {}).get('username')} for p in r.get('data', [])]
    tok_pag = {p['id']: p.get('access_token') for p in r.get('data', [])}
    for p in paginas:
        print('Página:', p)
    pixels = []
    for c in contas:
        r = _try(lambda: api('GET', f"{c['id']}/adspixels", {'fields': 'id,name,last_fired_time'}), {}) or {}
        for px in r.get('data', []):
            pixels.append({'conta': c['id'], 'id': px['id'], 'nome': px.get('name'), 'ultimo_evento': px.get('last_fired_time')})
            print('Pixel:', pixels[-1])
    # pixel do site (o que dispara no meucaoobedece) — pode não estar listado na conta
    pixel_site = os.environ.get('PIXEL_SITE', '1702277674672285')
    r = _try(lambda: api('GET', pixel_site, {'fields': 'id,name,last_fired_time,owner_business{id,name}'}), None)
    print('Pixel do site:', r if r else f'{pixel_site} NÃO visível para o robô')
    if r:
        ev = _try(lambda: api('GET', f'{pixel_site}/stats', {'aggregation': 'event'}), None)
        nomes = sorted({d.get('value') for b in (ev or {}).get('data', []) for d in b.get('data', [])} - {None})
        print('  eventos recentes do pixel do site:', ', '.join(nomes) or '(nenhum lido)')
    # Instagram para anúncio (outras rotas, já que instagram_business_account pede instagram_basic)
    igs = []
    for p in paginas:
        for rota in (f"{p['id']}/instagram_accounts", f"{p['id']}/page_backed_instagram_accounts"):
            d = _try(lambda: api('GET', rota, {'fields': 'id,username', 'access_token': tok_pag.get(p['id']) or TOKEN}), {}) or {}
            for x in d.get('data', []):
                igs.append({'pagina': p['id'], 'rota': rota.split('/')[1], 'id': x['id'], 'user': x.get('username')})
    for c in contas:
        d = _try(lambda: api('GET', f"{c['id']}/instagram_accounts", {'fields': 'id,username'}), {}) or {}
        igs += [{'conta': c['id'], 'rota': 'conta', 'id': x['id'], 'user': x.get('username')} for x in d.get('data', [])]
        f = _try(lambda: api('GET', c['id'], {'fields': 'funding_source,funding_source_details,disable_reason,business{id,name}'}), {}) or {}
        print('Pagamento da conta:', {k: f.get(k) for k in ('funding_source', 'funding_source_details', 'disable_reason', 'business')})
    for x in igs:
        print('Instagram p/ anúncio:', x)
    gravar(STATUS, {'permissoes': concedidas, 'faltam': falta, 'contas_anuncio': contas, 'paginas': paginas, 'pixels': pixels,
                    'pixel_site': r, 'instagrams': igs})
    print('Gravado em', STATUS.relative_to(RAIZ))
    return not falta and bool(contas)


# ---------------- montar ----------------
def _alvos(cfg):
    """Conta, página, Instagram e pixel: os do arquivo de campanha, senão os achados pelo checar."""
    st = ler(STATUS, {}) or {}
    if not st.get('contas_anuncio'):
        checar(); st = ler(STATUS, {})
    contas = [c for c in st.get('contas_anuncio', []) if c.get('status') == 1] or st.get('contas_anuncio', [])
    conta = cfg.get('conta') or (contas[0]['id'] if contas else None)
    pag = next((p for p in st.get('paginas', []) if p.get('ig') and 'obedece' in (p.get('nome') or '').lower()), None) or \
        next((p for p in st.get('paginas', []) if p.get('ig')), {})
    pixs = sorted([p for p in st.get('pixels', []) if p['conta'] == conta], key=lambda p: p.get('ultimo_evento') or '', reverse=True)
    if not pag:
        pag = next((p for p in st.get('paginas', []) if 'obedece' in (p.get('nome') or '').lower()), {})
    ig2 = next((x['id'] for x in st.get('instagrams', []) if x.get('rota') == 'instagram_accounts' and x.get('pagina') == pag.get('id')), None) or \
        next((x['id'] for x in st.get('instagrams', []) if x.get('rota') == 'conta'), None)
    out = {'conta': conta, 'pagina': cfg.get('pagina') or pag.get('id'), 'ig': cfg.get('instagram') or pag.get('ig') or ig2,
           'pixel': cfg.get('pixel') or (pixs[0]['id'] if pixs else None)}
    falta = [k for k, v in out.items() if not v and k != 'ig']
    if falta:
        sys.exit(f'Não achei: {", ".join(falta)}. Rode "checar" e confira as permissões/ativos do usuário do sistema.')
    print('Usando:', out)
    return out


def _url(cfg, nome):
    return f"https://raw.githubusercontent.com/kaicjackson88-ui/meucaoobedece-postss/{cfg['midia_branch']}/{nome}"


def _imagem(conta, cfg, nome):
    dados = urllib.request.urlopen(urllib.request.Request(_url(cfg, nome), headers={'User-Agent': 'mco'}), timeout=60).read()
    r = api('POST', f'{conta}/adimages', {'bytes': base64.b64encode(dados).decode('ascii'), 'name': nome})
    return next(iter(r['images'].values()))['hash']


def _video(conta, cfg, nome):
    vid = api('POST', f'{conta}/advideos', {'file_url': _url(cfg, nome), 'name': nome})['id']
    for _ in range(60):   # espera a Meta processar (até ~10 min)
        st = (api('GET', vid, {'fields': 'status'}).get('status') or {}).get('video_status')
        if st == 'ready':
            return vid
        if st == 'error':
            raise RuntimeError(f'A Meta não conseguiu processar o vídeo {nome}')
        time.sleep(10)
    raise RuntimeError(f'Vídeo {nome} demorou demais para processar')


def _cta(link):
    return {'type': 'LEARN_MORE', 'value': {'link': link}}


def _criativo(alvo, cfg, ad):
    conta, link = alvo['conta'], cfg['link']
    spec = {'page_id': alvo['pagina']}
    if alvo.get('ig'):
        spec['instagram_user_id'] = alvo['ig']
    if ad['tipo'] == 'video':
        vid = _video(conta, cfg, ad['arquivos'][0])
        capa = _imagem(conta, cfg, ad['arquivos'][1])
        spec['video_data'] = {'video_id': vid, 'image_hash': capa, 'message': ad['texto'], 'title': ad['titulo'], 'call_to_action': _cta(link)}
    elif ad['tipo'] == 'imagem':
        h = _imagem(conta, cfg, ad['arquivos'][0])
        spec['link_data'] = {'image_hash': h, 'link': link, 'message': ad['texto'], 'name': ad['titulo'], 'call_to_action': _cta(link)}
    elif ad['tipo'] == 'carrossel':
        filhos = [{'link': link, 'image_hash': _imagem(conta, cfg, a), 'name': t, 'call_to_action': _cta(link)}
                  for a, t in zip(ad['arquivos'], ad['cartoes'])]
        spec['link_data'] = {'link': link, 'message': ad['texto'], 'child_attachments': filhos, 'multi_share_optimized': False,
                             'multi_share_end_card': False, 'call_to_action': _cta(link)}
    else:
        raise ValueError(ad['tipo'])
    corpo = {'name': f"{cfg['nome']} | {ad['nome']}", 'object_story_spec': spec, 'url_tags': cfg['url_tags']}
    try:
        return api('POST', f'{conta}/adcreatives', corpo)['id']
    except RuntimeError as e:
        if 'instagram_user_id' not in spec:
            raise
        print('  Instagram recusado, criativo sai com a identidade da Página no Instagram:', str(e)[:160])
        spec.pop('instagram_user_id')
        return api('POST', f'{conta}/adcreatives', corpo)['id']


def montar(arq):
    cfg = ler(arq)
    saida = DADOS / f"meta_campanha_{cfg['id']}.json"
    est = ler(saida, {}) or {}
    alvo = _alvos(cfg)
    conta = alvo['conta']
    est.update({k: alvo[k] for k in alvo})
    if not est.get('campanha'):
        est['campanha'] = api('POST', f'{conta}/campaigns', {'name': cfg['nome'], 'objective': 'OUTCOME_SALES', 'status': 'PAUSED',
                                                             'special_ad_categories': [], 'is_adset_budget_sharing_enabled': 'false'})['id']
        print('Campanha criada (pausada):', est['campanha']); gravar(saida, est)
    if not est.get('conjunto'):
        est['conjunto'] = api('POST', f'{conta}/adsets', {
            'name': cfg['conjunto'], 'campaign_id': est['campanha'], 'status': 'PAUSED',
            'daily_budget': int(round(cfg['orcamento_dia'] * 100)), 'billing_event': 'IMPRESSIONS',
            'optimization_goal': 'OFFSITE_CONVERSIONS', 'bid_strategy': 'LOWEST_COST_WITHOUT_CAP',
            'promoted_object': {'pixel_id': alvo['pixel'], 'custom_event_type': 'PURCHASE'},
            'targeting': {'geo_locations': {'countries': ['BR']}, 'age_min': 18, 'targeting_automation': {'advantage_audience': 1}},
        })['id']
        print('Conjunto criado (pausado):', est['conjunto']); gravar(saida, est)
    est.setdefault('anuncios', {})
    for ad in cfg['anuncios']:
        if ad.get('pular'):
            print('Pulando (marcado para depois):', ad['nome']); continue
        if est['anuncios'].get(ad['nome'], {}).get('id'):
            continue
        try:
            cid = _criativo(alvo, cfg, ad)
            aid = api('POST', f'{conta}/ads', {'name': ad['nome'], 'adset_id': est['conjunto'], 'creative': {'creative_id': cid}, 'status': 'PAUSED'})['id']
            est['anuncios'][ad['nome']] = {'id': aid, 'criativo': cid}
            print('Anúncio criado (pausado):', ad['nome'], aid)
        except Exception as e:  # noqa: BLE001
            est['anuncios'][ad['nome']] = {'erro': str(e)[:400]}
            print('FALHOU', ad['nome'], '→', str(e)[:400])
        gravar(saida, est)
    est['montado_em'] = datetime.now(BRT).isoformat()
    gravar(saida, est)
    ok = [n for n, a in est['anuncios'].items() if a.get('id')]
    print(f'Pronto: {len(ok)} anúncio(s) criados, tudo PAUSADO. Para ligar: ativar.')


def _estado(arq):
    cfg = ler(arq)
    est = ler(DADOS / f"meta_campanha_{cfg['id']}.json")
    if not est or not est.get('campanha'):
        sys.exit('Campanha ainda não montada.')
    return cfg, est


def ativar(arq):
    cfg, est = _estado(arq)
    for nome, a in est['anuncios'].items():
        if a.get('id') and a.get('status') != 'PAUSADO_PELO_ROBO':
            api('POST', a['id'], {'status': 'ACTIVE'}); print('Ligado:', nome)
    api('POST', est['conjunto'], {'status': 'ACTIVE'}); api('POST', est['campanha'], {'status': 'ACTIVE'})
    est['ativado_em'] = datetime.now(BRT).isoformat(); gravar(DADOS / f"meta_campanha_{cfg['id']}.json", est)
    print('Campanha ligada.'); avisar('🚀 Anúncios no ar', f"{cfg['nome']} ligada com R${cfg['orcamento_dia']:.0f}/dia.")


def pausar(arq):
    cfg, est = _estado(arq)
    api('POST', est['campanha'], {'status': 'PAUSED'}); print('Campanha pausada.')


# ---------------- relatório + regras ----------------
def _acao(lista, *tipos):
    for t in tipos:
        for a in lista or []:
            if a.get('action_type') == t:
                return float(a.get('value') or 0)
    return 0.0


def relatorio(arq):
    cfg, est = _estado(arq)
    saida = DADOS / f"meta_campanha_{cfg['id']}.json"
    campos = 'ad_id,ad_name,spend,impressions,frequency,inline_link_clicks,inline_link_click_ctr,cpc,actions,video_thruplay_watched_actions'
    r = api('GET', f"{est['campanha']}/insights", {'level': 'ad', 'date_preset': 'maximum', 'fields': campos, 'limit': 100})
    linhas, acoes, total, vendas_tot = [], [], 0.0, 0
    ativado = datetime.fromisoformat(est['ativado_em']) if est.get('ativado_em') else None
    dias = (datetime.now(BRT) - ativado).days if ativado else 0
    for d in r.get('data', []):
        gasto = float(d.get('spend') or 0); imp = float(d.get('impressions') or 0); total += gasto
        ctr = float(d.get('inline_link_click_ctr') or 0)
        v3 = _acao(d.get('actions'), 'video_view'); hook = (v3 / imp * 100) if imp and v3 else None
        compras = int(_acao(d.get('actions'), 'offsite_conversion.fb_pixel_purchase', 'purchase', 'omni_purchase'))
        ic = int(_acao(d.get('actions'), 'offsite_conversion.fb_pixel_initiate_checkout', 'initiate_checkout', 'omni_initiated_checkout'))
        vendas_tot += compras
        cpa = gasto / compras if compras else None
        freq = float(d.get('frequency') or 0)
        nome, aid = d.get('ad_name'), d.get('ad_id')
        dec = 'manter'
        if gasto >= 15 and (ctr < 0.8 or (hook is not None and hook < 25)):
            dec = 'PAUSAR (gancho fraco)'
        elif gasto >= 45 and compras == 0:
            dec = 'PAUSAR (R$45 sem venda)'
        elif cpa is not None and cpa > TETO_CPA and dias >= 3:
            dec = 'PAUSAR (custo/venda alto)'
        elif freq > 3:
            dec = 'trocar criativo (frequência alta)'
        elif cpa is not None and cpa <= ALVO_CPA:
            dec = 'manter — vencedor'
        if dec.startswith('PAUSAR'):
            info = est['anuncios'].get(nome, {})
            if info.get('status') != 'PAUSADO_PELO_ROBO':
                _try(lambda: api('POST', aid, {'status': 'PAUSED'}))
                info['status'] = 'PAUSADO_PELO_ROBO'; info['motivo'] = dec; est['anuncios'][nome] = info
                acoes.append(f'⏸ pausei {nome}: {dec[8:-1]}')
        linhas.append(f"| {nome} | R${gasto:.2f} | {ctr:.2f}% | {f'{hook:.0f}%' if hook is not None else '—'} | {ic} | {compras} | "
                      f"{f'R${cpa:.2f}' if cpa else '—'} | {dec} |")
    limite = cfg.get('limite_total', 200)
    if total >= limite and vendas_tot == 0:
        _try(lambda: api('POST', est['campanha'], {'status': 'PAUSED'}))
        acoes.append(f'🛑 pausei a campanha: gastou R${total:.2f} (limite R${limite}) sem venda — hora de revisar oferta/página')
    agora = datetime.now(BRT).strftime('%d/%m %H:%M')
    md = [f"# {cfg['nome']} — {agora}", '', f'Gasto total: **R${total:.2f}** de R${limite} · vendas: **{vendas_tot}** · dia {dias + 1} do teste', '',
          '| anúncio | gasto | CTR link | hook 3s | checkouts | vendas | custo/venda | decisão |', '|---|---|---|---|---|---|---|---|'] + linhas
    md += ['', '**Ações do robô:** ' + ('; '.join(acoes) if acoes else 'nenhuma — dentro das regras.')]
    if dias < 3:
        md.append('_Primeiros 3 dias: só pausas de segurança; nada de mexer no resto (o aprendizado reinicia)._')
    (DADOS / 'meta_relatorio.md').write_text('\n'.join(md) + '\n', encoding='utf-8')
    est['ultimo_relatorio'] = agora; gravar(saida, est)
    print('\n'.join(md))
    avisar(f'📈 Anúncios {agora}: R${total:.0f} · {vendas_tot} venda(s)',
           '\n'.join(l.split('|')[1].strip() + ': ' + l.split('|')[2].strip() + ', ' + l.split('|')[6].strip() + ' venda(s) → ' + l.split('|')[8].strip()
                     for l in linhas) + ('\n' + '\n'.join(acoes) if acoes else ''))


if __name__ == '__main__':
    cmd = sys.argv[1] if len(sys.argv) > 1 else 'checar'
    arq = sys.argv[2] if len(sys.argv) > 2 else str(RAIZ / 'anuncios' / 'teste2.json')
    if not TOKEN:
        sys.exit('Sem chave: crie o segredo META_ADS_TOKEN.')
    {'checar': checar, 'montar': montar, 'ativar': ativar, 'pausar': pausar, 'relatorio': relatorio}[cmd](arq)
