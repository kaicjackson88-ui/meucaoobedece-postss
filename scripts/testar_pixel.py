"""Abre o site num navegador de verdade (como um iPhone e como um PC), faz o caminho do cliente
(entra, pula o quiz, rola a página, clica em comprar) e registra cada evento que o pixel da Meta enviou."""
import asyncio
from urllib.parse import urlparse, parse_qs
from playwright.async_api import async_playwright

SITE = 'https://meucaoobedece.vercel.app/?utm_source=teste_robo'


async def rodar(p, nome, opcoes):
    b = await p.chromium.launch()
    ctx = await b.new_context(**opcoes)
    pg = await ctx.new_page()
    eventos, falhas = [], []

    def req(r):
        if 'facebook.com/tr' in r.url:
            q = parse_qs(urlparse(r.url).query)
            eventos.append((q.get('ev', ['?'])[0], q.get('id', ['?'])[0], q.get('cd[content_name]', [''])[0], r))

    pg.on('request', req)
    pg.on('requestfailed', lambda r: 'facebook' in r.url and falhas.append(r.url[:90] + ' ' + str(r.failure)))
    await pg.goto(SITE, wait_until='networkidle')
    await pg.wait_for_timeout(3000)
    try:
        await pg.click('#qPula2', timeout=5000)
    except Exception as e:  # noqa: BLE001
        print(nome, 'sem botão de pular quiz:', str(e)[:80])
    await pg.wait_for_timeout(1500)
    for f in (0.3, 0.55, 0.8):
        await pg.evaluate(f'window.scrollTo(0, document.documentElement.scrollHeight*{f})')
        await pg.wait_for_timeout(1200)
    await pg.route('**/pay.kiwify.com.br/**', lambda r: r.abort())
    try:
        await pg.locator('.btn[data-cta]').first.click(timeout=5000)
    except Exception as e:  # noqa: BLE001
        print(nome, 'clique no comprar falhou:', str(e)[:80])
    await pg.wait_for_timeout(2500)
    linhas = [f'== {nome} ==']
    for ev, pid, cn, r in eventos:
        resp = await r.response()
        linhas.append(f'  {ev:18} pixel {pid}  HTTP {resp.status if resp else "sem resposta"}  {cn[:60]}')
    if not eventos:
        linhas.append('  NENHUM evento enviado')
    linhas += ['  falha: ' + x for x in falhas]
    await b.close()
    return linhas


async def main():
    async with async_playwright() as p:
        out = await rodar(p, 'iPhone', dict(p.devices['iPhone 13']))
        out += await rodar(p, 'PC', dict(viewport={'width': 1366, 'height': 800}))
    texto = '\n'.join(out)
    print(texto)
    open('dados/pixel_teste.txt', 'w', encoding='utf-8').write(texto + '\n')


asyncio.run(main())
