"""Vídeo de TESTE (não vai pro perfil): mesmo tema/personagens do robô + GSAP (animação),
Lottie (efeitos estilo After Effects), Whisper (legenda palavra por palavra) e ffmpeg (montagem).
Roda no GitHub Actions: python teste_efeitos/render.py"""
import asyncio, json, shutil, subprocess, sys, tempfile
from pathlib import Path

AQUI = Path(__file__).resolve().parent
RAIZ = AQUI.parent
sys.path.insert(0, str(RAIZ / 'scripts'))
import numpy as np  # noqa: E402
from scipy.io import wavfile  # noqa: E402
import reels  # noqa: E402
from reels_audio import gerar_sfx, gerar_musica, SR  # noqa: E402

FALAS = [('narrador', 'Faltavam três dias pra vistoria do apartamento.'),
         ('narrador', 'E o Thor resolveu fazer xixi bem no tapete novo.'),
         ('ana', 'Thor! De novo não!'),
         ('narrador', 'Até que ela trocou a bronca por um petisco no lugar certo. Seu cão faz isso? Comenta um ou dois.')]
FPS = 30


def wav_de(mp3, wav):
    subprocess.run(['ffmpeg', '-y', '-v', 'error', '-i', str(mp3), '-ac', '1', '-ar', str(SR), str(wav)], check=True)
    sr, x = wavfile.read(wav); return x.astype(np.float32) / 32768


async def tts(texto, vz, saida):
    import edge_tts
    await edge_tts.Communicate(texto, vz['voz'], rate=vz['rate'], pitch=vz['pitch']).save(str(saida))


def main():
    pasta = Path(tempfile.mkdtemp(prefix='teste-'))
    subprocess.run([sys.executable, str(AQUI / 'lottie_gen.py')], check=True)
    # 1) vozes (edge-tts) com pausas curtas
    partes, seg, t = [np.zeros(int(SR * .45))], [], .45
    for i, (quem, texto) in enumerate(FALAS):
        mp3 = pasta / f'f{i}.mp3'; asyncio.run(tts(texto, reels.VOZES_PADRAO[quem], mp3))
        x = wav_de(mp3, pasta / f'f{i}.wav')
        nz = np.where(np.abs(x) > .01)[0]; x = x[max(0, nz[0] - 800): nz[-1] + 1600] if len(nz) else x
        seg.append({'ini': round(t, 3), 'fim': round(t + len(x) / SR, 3), 'quem': quem})
        partes += [x, np.zeros(int(SR * .28))]; t += len(x) / SR + .28
    voz = np.concatenate(partes); wavfile.write(pasta / 'voz.wav', SR, (voz * 32767).astype(np.int16))
    # 2) Whisper: tempo exato de cada palavra
    from faster_whisper import WhisperModel
    modelo = WhisperModel('small', device='cpu', compute_type='int8')
    segs, _ = modelo.transcribe(str(pasta / 'voz.wav'), language='pt', word_timestamps=True, vad_filter=False)
    palavras = []
    for s in segs:
        for w in s.words:
            meio = (w.start + w.end) / 2
            quem = next((g['quem'] for g in seg if g['ini'] - .15 <= meio <= g['fim'] + .15), 'narrador')
            palavras.append({'w': w.word.strip(), 'ini': round(w.start, 3), 'fim': round(w.end, 3), 'q': quem})
    print('Whisper:', ' '.join(p['w'] for p in palavras))
    dur = round(seg[-1]['fim'] + 2.2, 2)
    # 3) página de animação (GSAP + Lottie + personagens do robô)
    work = pasta / 'pg'; work.mkdir()
    for f in ['svgs.js', 'base.js', 'personagens.js']: shutil.copy(RAIZ / 'motor' / f, work / f)
    shutil.copytree(RAIZ / 'motor' / 'fontes', work / 'fontes')
    shutil.copy(RAIZ / 'node_modules' / 'gsap' / 'dist' / 'gsap.min.js', work / 'gsap.min.js')
    shutil.copy(RAIZ / 'node_modules' / 'lottie-web' / 'build' / 'player' / 'lottie.min.js', work / 'lottie.min.js')
    shutil.copy(AQUI / 'efeitos.html', work / 'efeitos.html')
    (work / 'dados.js').write_text('const PALAVRAS=%s;const SEG=%s;const DUR=%s;const LOTTIE_EXPLOSAO=%s;const LOTTIE_SUSTO=%s;' % (
        json.dumps(palavras, ensure_ascii=False), json.dumps(seg), dur, (AQUI / 'explosao.json').read_text(), (AQUI / 'susto.json').read_text()), encoding='utf-8')
    sfx_ev = asyncio.run(gravar(work, pasta / 'mudo.mp4', dur))
    # 4) áudio: voz + trilha + efeitos sonoros, mixados no ffmpeg
    wavfile.write(pasta / 'sfx.wav', SR, (np.clip(gerar_sfx(sfx_ev, dur, 5), -1, 1) * 32767).astype(np.int16))
    wavfile.write(pasta / 'mus.wav', SR, (np.clip(gerar_musica(dur, 3, [seg[1]['ini'], seg[3]['ini']]), -1, 1) * 32767).astype(np.int16))
    final = AQUI / 'teste-efeitos.mp4'
    subprocess.run(['ffmpeg', '-y', '-v', 'error', '-i', str(pasta / 'mudo.mp4'), '-i', str(pasta / 'voz.wav'), '-i', str(pasta / 'mus.wav'), '-i', str(pasta / 'sfx.wav'),
                    '-filter_complex',
                    '[1:a]apad,highpass=f=80,acompressor=threshold=-18dB:ratio=3:attack=5:release=80,volume=1.6,asplit=2[v][vs];'
                    '[2:a]volume=0.45[m];[m][vs]sidechaincompress=threshold=0.03:ratio=8:attack=20:release=300[md];[3:a]volume=0.5[s];'
                    '[v][md][s]amix=inputs=3:normalize=0:duration=longest,alimiter=limit=0.95[a]',
                    '-map', '0:v', '-map', '[a]', '-c:v', 'libx264', '-crf', '20', '-preset', 'medium', '-pix_fmt', 'yuv420p', '-r', str(FPS),
                    '-c:a', 'aac', '-b:a', '160k', '-t', str(dur), '-movflags', '+faststart', str(final)], check=True)
    print('Pronto:', final, dur, 's')


async def gravar(work, saida, dur):
    from playwright.async_api import async_playwright
    async with async_playwright() as p:
        b = await p.chromium.launch(); pg = await b.new_page(viewport={'width': 1080, 'height': 1920})
        erros = []; pg.on('pageerror', lambda e: erros.append(str(e))); pg.on('console', lambda m: print('pg:', m.text))
        await pg.goto((work / 'efeitos.html').as_uri())
        await pg.evaluate("Promise.all(['600 50px FR','700 50px FR','800 50px NU','900 50px NU'].map(x=>document.fonts.load(x))).then(()=>load())")
        if erros: raise RuntimeError('Erro na página: ' + erros[0])
        sfx = await pg.evaluate('SFX')
        ff = subprocess.Popen(['ffmpeg', '-y', '-v', 'error', '-f', 'image2pipe', '-framerate', str(FPS), '-c:v', 'mjpeg', '-i', '-',
                               '-c:v', 'libx264', '-pix_fmt', 'yuv420p', '-crf', '18', '-preset', 'medium', str(saida)], stdin=subprocess.PIPE)
        for i in range(int(FPS * dur)):
            await pg.evaluate(f'render({i / FPS})')
            ff.stdin.write(await pg.screenshot(type='jpeg', quality=92))
        ff.stdin.close(); ff.wait(); await b.close()
        if erros: raise RuntimeError('Erro na página: ' + erros[0])
        return sfx


if __name__ == '__main__':
    main()
