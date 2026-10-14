"""Tira print, em alta resolução e com fundo transparente, de cada bloco real da página de vendas
(dores, painel, módulos, skins, oferta, garantia, mascote) para virar "quadros flutuantes" nos criativos.
O pixel da Meta fica bloqueado. Saída: quiz/site_*.png"""
import asyncio, os
from playwright.async_api import async_playwright

SITE = 'https://meucaoobedece.vercel.app/?utm_source=gravacao_robo'
OUT = 'quiz'
ALVOS = {  # nome: (seletor, índice)
    'dor1': ('.dor', 0), 'dor2': ('.dor', 1), 'dor3': ('.dor', 2), 'dor4': ('.dor', 3), 'dor5': ('.dor', 4),
    'painel': ('.painel', 0), 'mods': ('.mods', 0),
    'mod1': ('.mod', 0), 'mod2': ('.mod', 1), 'mod3': ('.mod', 2), 'mod4': ('.mod', 3), 'mod5': ('.mod', 4), 'mod6': ('.mod', 5), 'mod7': ('.mod', 6),
    'skin1': ('#sk1', 0), 'skin2': ('#sk2', 0), 'skin3': ('#sk3', 0), 'skins': ('.skins', 0),
    'stack': ('.stack', 0), 'oferta': ('.oferta', 0), 'garantia': ('.gar', 0), 'mascote': ('#heroDog', 0),
    'mecok': ('.mecOk', 0), 'carrossel': ('.carr', 0),
}
CSS = """.rv,.rvE,.rvD,.rvZ,.par{opacity:1!important;transform:none!important;animation:none!important;transition:none!important}
#quiz,.barraFixa,#barra,.bFix{display:none!important}"""


async def main():
    os.makedirs(OUT, exist_ok=True)
    async with async_playwright() as p:
        b = await p.chromium.launch()
        ctx = await b.new_context(**{**p.devices['iPhone 13'], 'device_scale_factor': 3})
        await ctx.route('**/*facebook*/**', lambda r: r.abort())
        pg = await ctx.new_page()
        await pg.goto(SITE, wait_until='networkidle')
        await pg.wait_for_timeout(1500)
        await pg.evaluate("() => { const b = document.getElementById('qPula2') || document.getElementById('qPula'); if (b) b.click(); }")
        await pg.wait_for_timeout(1200)
        await pg.add_style_tag(content=CSS)
        # rola a página toda para disparar contadores e carrosséis
        for f in range(0, 101, 5):
            await pg.evaluate(f'window.scrollTo(0, document.documentElement.scrollHeight*{f / 100})')
            await pg.wait_for_timeout(250)
        await pg.wait_for_timeout(1500)
        for nome, (sel, i) in ALVOS.items():
            try:
                el = pg.locator(sel).nth(i)
                await el.scroll_into_view_if_needed(timeout=4000)
                await pg.wait_for_timeout(400)
                await el.screenshot(path=f'{OUT}/site_{nome}.png', omit_background=True, timeout=8000)
                print('ok', nome)
            except Exception as e:  # noqa: BLE001
                print('falhou', nome, str(e)[:80])
        await b.close()


asyncio.run(main())
