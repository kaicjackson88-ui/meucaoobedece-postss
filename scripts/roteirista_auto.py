"""Roteirista autônomo (sem Claude): escreve histórias NOVAS com a IA gratuita do GitHub,
usando o guia de escrita, uma história modelo, os pesos do nosso perfil (o que dá view) e a pesquisa de tendências.
Cada história é validada (campos permitidos, final com quiz/seguir, narração montável); se falhar, tenta de novo.

python scripts/roteirista_auto.py 9
"""
import json, random, re, sys
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(RAIZ / 'scripts'))
import reels  # noqa: E402
import ia_gratis  # noqa: E402

BANCO = RAIZ / 'tiktok' / 'banco'
D = RAIZ / 'dados'
QUEM = {'ana', 'carla', 'bia', 'joao', 'pedro', 'vizinho', 'sindica', 'narrador', 'cao'}
POSES = {'parado', 'aponta', 'maos_cabeca', 'bracos_cruzados', 'maos_cintura', 'petisco', 'acena', 'celular', 'comemora', 'maos_rosto', 'carinho', 'guia', 'bilhete', 'explica'}
HUMOR = {'normal', 'feliz', 'radiante', 'triste', 'bravo', 'surpreso', 'preocupado', 'vergonha', 'cansado'}
CENARIO = {'sala', 'noite', 'quarto', 'cozinha', 'corredor', 'rua'}
ACAO = {'late', 'pula', 'corre', 'senta', 'dorme', 'feliz', None}
MASC = {'normal', 'bravo', 'feliz', 'dorminhoco', 'lendario'}
OBJ = {'poca', 'almofada', 'sapato', 'petisco', 'coracoes'}
ICONES = {'sino', 'osso', 'moeda', 'casa', 'relogio', 'coracao', 'lampada', 'bola', 'guia', 'calendario', 'megafone', 'pata', 'alvo', 'cerebro', 'focinho', 'porta', 'escudo', 'x', 'check', 'sofa'}
TIPOS = {'gancho', 'historia', 'chat', 'virada', 'curiosidade', 'cta_quiz'}
FIM = 'Segue o perfil pra não perder a próxima história. E faz o teste grátis no link do perfil.'


def validar(r):
    erros = []
    c = r.get('cenas') or []
    if not (8 <= len(c) <= 12): erros.append('precisa de 8 a 12 cenas')
    if not c or c[0].get('tipo') != 'gancho': erros.append('primeira cena deve ser gancho')
    if not c or c[-1].get('tipo') != 'cta_quiz' or not c[-1].get('seguir'): erros.append('última cena deve ser cta_quiz com "seguir": true')
    if not any(x.get('tipo') == 'virada' for x in c): erros.append('falta cena virada')
    for i, x in enumerate(c):
        t = x.get('tipo')
        if t not in TIPOS: erros.append(f'cena {i}: tipo inválido {t}')
        if t == 'gancho' and (len(x.get('linhas', [])) != 3): erros.append('gancho precisa de 3 linhas curtas')
        if t == 'gancho' and x.get('icone') not in ICONES: x['icone'] = 'coracao'
        if t == 'virada':
            for k in ('topo', 'de', 'para', 'para_palavra'):
                if not x.get(k): erros.append(f'virada sem {k}')
        if t == 'curiosidade':
            x.setdefault('tag', 'VOCÊ SABIA?'); x.setdefault('rotulo', ['', ''])
            if x.get('icone') not in ICONES: x['icone'] = 'lampada'
        if t == 'cta_quiz':
            if len(x.get('opcoes', [])) != 3 or not x.get('pergunta') or not x.get('resultado'): erros.append('cta_quiz precisa de pergunta, 3 opcoes e resultado')
            if FIM not in x.get('fala', ''): x['fala'] = (x.get('fala', '').strip() + ' ' + FIM).strip()
            x.setdefault('escolha', 0)
        if t == 'historia':
            if x.get('cenario', 'sala') not in CENARIO: erros.append(f'cena {i}: cenario inválido')
            el = x.get('elenco') or []
            if not (1 <= len(el) <= 2): erros.append(f'cena {i}: elenco precisa de 1 ou 2 pessoas')
            for e in el:
                if e.get('quem') not in QUEM - {'narrador', 'cao'}: erros.append(f'cena {i}: quem inválido {e.get("quem")}')
                if e.get('pose', 'parado') not in POSES: e['pose'] = 'parado'
                if e.get('humor', 'normal') not in HUMOR: e['humor'] = 'normal'
            cao = x.get('cao')
            if isinstance(cao, dict):
                if cao.get('mascote', 'normal') not in MASC: cao['mascote'] = 'normal'
                if cao.get('acao') not in ACAO: cao['acao'] = None
            for o in x.get('objetos', []) or []:
                if o.get('nome') not in OBJ: erros.append(f'cena {i}: objeto inválido {o.get("nome")}')
        for d in x.get('dialogo', []) or []:
            if d.get('quem') not in QUEM: erros.append(f'cena {i}: dialogo quem inválido {d.get("quem")}')
            if d.get('pose') and d['pose'] not in POSES: d.pop('pose')
            if d.get('humor') and d['humor'] not in HUMOR: d.pop('humor')
        if not (x.get('fala') or x.get('dialogo')): erros.append(f'cena {i}: sem fala nem dialogo')
    if 'História ilustrativa' not in r.get('legenda', ''): erros.append('legenda precisa ter "(História ilustrativa, inspirada no que muitos tutores vivem.)"')
    try:
        rr = json.loads(json.dumps(r)); reels.preparar_falas(rr)
        if sum(len(reels.tokens(cc['fala'])) for cc in rr['cenas']) < 120: erros.append('história curta demais (precisa passar de 1 minuto)')
    except Exception as e:
        erros.append(f'falas inválidas: {e}')
    return erros


def contexto():
    guia = (RAIZ / 'reels' / 'COMO_ESCREVER.md').read_text(encoding='utf-8')
    guia = guia[guia.find('## Histórias animadas'):] if '## Histórias animadas' in guia else guia
    modelos = sorted(BANCO.glob('h[0-9]*.json'))
    modelo = json.loads(random.choice(modelos[1:6] or modelos).read_text(encoding='utf-8'))
    ganchos = []
    for p in BANCO.glob('h*.json'):
        try: ganchos.append(json.loads(p.read_text(encoding='utf-8'))['legenda'].split('(')[0].strip()[:90])
        except Exception: pass
    tend = ''
    for n in ('tendencias.md', 'tendencias_auto.md'):
        if (D / n).exists(): tend += (D / n).read_text(encoding='utf-8')[:1800] + '\n'
    pesos = json.dumps(reels.ler_json(D / 'tiktok_pesos.json', {}), ensure_ascii=False)[:1200]
    return guia, modelo, ganchos, tend, pesos


def escrever(n):
    if not ia_gratis.disponivel():
        print('IA gratuita indisponível (sem GITHUB_TOKEN)'); return []
    guia, modelo, ganchos, tend, pesos = contexto()
    nums = [int(m.group(1)) for p in BANCO.glob('h*.json') if (m := re.match(r'h(\d{3})-', p.stem))]
    prox = max(nums, default=0) + 1
    sistema = ('Você é o roteirista de um perfil de TikTok de histórias animadas 2D sobre tutores e cães (Brasil, português falado). '
               'Escreva UMA história nova por vez, no formato JSON exato do modelo, seguindo o guia. Frases curtas e faladas, emoção, diálogo de verdade. '
               'Nunca prometa prazo ou resultado garantido. Não copie histórias existentes nem de terceiros. Responda só com o JSON.')
    feitos = []
    for k in range(n):
        pedido = (f'GUIA:\n{guia}\n\nMODELO (copie a estrutura, NÃO a história):\n{json.dumps(modelo, ensure_ascii=False, separators=(",", ":"))}\n\n'
                  f'O QUE DÁ MAIS VIEW NO NOSSO PERFIL (pesos, positivo = bom):\n{pesos}\n\nTENDÊNCIAS:\n{tend}\n\n'
                  'GANCHOS QUE JÁ EXISTEM (não repita a premissa):\n- ' + '\n- '.join(ganchos[-60:]) +
                  f'\n\nEscreva a história nova nº {k + 1}: escolha uma premissa nova (use o que tem peso positivo e as ideias das tendências; '
                  'de vez em quando teste algo diferente). Campos obrigatórios: id, formato "tiktok-historia", gancho_tipo "historia", tema, estilo "sol", '
                  'legenda (gancho único + "(História ilustrativa, inspirada no que muitos tutores vivem.)" + chamada pro teste do link do perfil), hashtags (5 a 7), cenas.')
        ok = None
        for tentativa in range(3):
            try:
                r = ia_gratis.json_de(ia_gratis.perguntar(sistema, pedido, max_tokens=3800, temperatura=0.9, json_saida=True))
            except Exception as e:
                print('  IA falhou:', e); break
            erros = validar(r)
            if not erros:
                ok = r; break
            print(f'  rascunho {k + 1} com problemas ({tentativa + 1}/3):', '; '.join(erros[:5]))
            pedido += '\n\nSua última resposta tinha estes problemas, corrija: ' + '; '.join(erros[:8])
        if not ok:
            continue
        slug = re.sub(r'[^a-z0-9]+', '-', reels.norm(ok.get('tema', 'historia')) or 'historia')[:20].strip('-') or 'historia'
        ok['id'] = f'h{prox:03d}-ia-{slug}'
        ok['formato'] = 'tiktok-historia'; ok['autor'] = 'ia-gratis'
        (BANCO / f"{ok['id']}.json").write_text(json.dumps(ok, ensure_ascii=False, indent=1), encoding='utf-8')
        feitos.append(ok['id']); ganchos.append(ok['legenda'][:90]); prox += 1
        print('  ✍️ nova história:', ok['id'], '—', ok['legenda'][:70])
    return feitos


if __name__ == '__main__':
    escrever(int(sys.argv[1]) if len(sys.argv) > 1 else 3)
