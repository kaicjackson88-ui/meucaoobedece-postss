"""Abre o checkout da Kiwify como um iPhone no Brasil e tira prints (para auditoria da página de pagamento)."""
import asyncio
from playwright.async_api import async_playwright

URL = 'https://pay.kiwify.com.br/p5DbD5v?utm_source=teste_robo'


async def main():
    async with async_playwright() as p:
        b = await p.chromium.launch()
        ctx = await b.new_context(**p.devices['iPhone 13'], locale='pt-BR', timezone_id='America/Sao_Paulo')
        pg = await ctx.new_page()
        await pg.goto(URL, wait_until='networkidle'); await pg.wait_for_timeout(4000)
        h = await pg.evaluate('document.documentElement.scrollHeight')
        for i in range(min(6, h // 844 + 1)):
            await pg.evaluate(f'scrollTo(0,{i * 844})'); await pg.wait_for_timeout(600)
            await pg.screenshot(path=f'dados/checkout_{i}.png')
        txt = await pg.evaluate('document.body.innerText')
        open('dados/checkout_texto.txt', 'w', encoding='utf-8').write(txt)
        await b.close()

asyncio.run(main())
