"""Grava a tela do quiz do site num iPhone (navegador de verdade), respondendo as perguntas devagar,
até o diagnóstico. Serve de cena real do produto nos anúncios. O pixel da Meta fica bloqueado durante a
gravação para não sujar os dados. Saída: quiz/quiz_iphone.mp4 + prints."""
import asyncio, glob, os, shutil, subprocess
from playwright.async_api import async_playwright

SITE = 'https://meucaoobedece.vercel.app/?utm_source=gravacao_robo'
OUT = 'quiz'


async def main():
    os.makedirs(OUT, exist_ok=True)
    async with async_playwright() as p:
        b = await p.chromium.launch()
        dev = dict(p.devices['iPhone 13'])
        ctx = await b.new_context(**dev, record_video_dir='/tmp/gravacao', record_video_size={'width': 390, 'height': 844})
        await ctx.route('**/*facebook*/**', lambda r: r.abort())
        pg = await ctx.new_page()
        await pg.goto(SITE, wait_until='networkidle')
        await pg.wait_for_timeout(2500)
        await pg.screenshot(path=f'{OUT}/q0.png')
        for passo in range(1, 14):
            ops = pg.locator('#qPalco .qOp')
            if await ops.count() == 0:
                break
            alvo = ops.nth(min(1, await ops.count() - 1))
            await alvo.scroll_into_view_if_needed()
            await pg.wait_for_timeout(700)
            await alvo.click()
            await pg.wait_for_timeout(500)
            seguir = pg.locator('#qSeguir')
            if await seguir.count() and await seguir.is_visible():
                await pg.wait_for_timeout(500)
                await seguir.click()
            await pg.wait_for_timeout(1300)
            await pg.screenshot(path=f'{OUT}/q{passo}.png')
        await pg.wait_for_timeout(6000)  # carregamento + diagnóstico
        await pg.screenshot(path=f'{OUT}/diagnostico.png')
        for _ in range(4):
            await pg.mouse.wheel(0, 350)
            await pg.wait_for_timeout(1100)
        await pg.screenshot(path=f'{OUT}/fim.png')
        await ctx.close(); await b.close()
    webm = sorted(glob.glob('/tmp/gravacao/*.webm'))[-1]
    subprocess.run(['ffmpeg', '-y', '-v', 'error', '-i', webm, '-vf', 'scale=780:-2,fps=30', '-c:v', 'libx264', '-crf', '20',
                    '-pix_fmt', 'yuv420p', f'{OUT}/quiz_iphone.mp4'], check=True)
    shutil.rmtree('/tmp/gravacao', ignore_errors=True)
    print('gravado:', os.path.getsize(f'{OUT}/quiz_iphone.mp4'), 'bytes')


asyncio.run(main())
