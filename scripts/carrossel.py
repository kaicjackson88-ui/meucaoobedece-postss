"""Gera carrosséis novos (5 slides) com a Fábrica de Carrosséis (motor/fabrica.html)."""
import asyncio, base64, json, random
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent
FABRICA = RAIZ / 'motor' / 'fabrica.html'
SEGS = ['latido', 'xixi', 'coleira', 'roer', 'pulo', 'ansiedade', 'chamado', 'mordida', 'fogos', 'obedece']


async def _gerar(seg, seed, pasta):
    from playwright.async_api import async_playwright
    async with async_playwright() as p:
        kw = {}
        if Path('/opt/pw-browsers/chromium').exists(): kw['executable_path'] = '/opt/pw-browsers/chromium'
        b = await p.chromium.launch(**kw)
        pg = await b.new_page(viewport={'width': 1200, 'height': 900})
        await pg.goto(FABRICA.as_uri())
        await pg.wait_for_function('typeof montar === "function"')
        r = await pg.evaluate('''async ([seg, seed]) => {
            await fontes();
            const c = montar(seg, seed); c.legenda = legendaDe(c);
            const out = [];
            for (let i = 0; i < 5; i++) {
                const blob = await pngDe(c, i);
                out.push(await new Promise(res => { const fr = new FileReader(); fr.onload = () => res(fr.result); fr.readAsDataURL(blob); }));
            }
            return {out, legenda: c.legenda, hook: plain(c.hook), assin: c.assin, nome: SEG[seg].nome};
        }''', [seg, seed])
        await b.close()
    pasta = Path(pasta); pasta.mkdir(parents=True, exist_ok=True)
    arquivos = []
    for i, d in enumerate(r['out'], 1):
        f = pasta / f'slide-{i}.jpg'; f.write_bytes(base64.b64decode(d.split(',', 1)[1])); arquivos.append(f)
    return arquivos, r


def gerar(seg, usados_assin, pasta, tentativas=8):
    """Gera um carrossel do tema `seg` com combinação (gancho + dicas) ainda não usada."""
    ultimo = None
    for _ in range(tentativas):
        seed = random.randint(1, 10 ** 9)
        arquivos, info = asyncio.run(_gerar(seg, seed, pasta))
        ultimo = (arquivos, info, seed)
        if info['assin'] not in usados_assin:
            break
    return ultimo


def escolher_tema(feitos):
    recentes = [f['seg'] for f in feitos[-12:] if f.get('seg')]  # ignora registros de erro
    cont = {s: recentes.count(s) for s in SEGS}
    ultimo = recentes[-1] if recentes else None
    cand = sorted([s for s in SEGS if s != ultimo], key=lambda s: (cont[s], random.random()))
    return cand[0]
