"""Anúncios em motion (Meta/TikTok) com os depoimentos reais da página de vendas.
3 variações de gancho, mesmo corpo. Voz edge-tts + Whisper (tempo das palavras) + GSAP + Lottie + ffmpeg.
python criativos/anuncio/render.py"""
import asyncio, json, shutil, subprocess, sys, tempfile
from pathlib import Path

AQUI = Path(__file__).resolve().parent
RAIZ = AQUI.parents[1]
sys.path.insert(0, str(RAIZ / 'scripts'))
sys.path.insert(0, str(RAIZ / 'teste_efeitos'))
import numpy as np  # noqa: E402
from scipy.io import wavfile  # noqa: E402
from scipy.signal import resample_poly  # noqa: E402
from reels_audio import gerar_sfx, gerar_musica, SR  # noqa: E402
import lottie_gen  # noqa: E402

VOZ = {'voz': 'pt-BR-FranciscaNeural', 'rate': '+10%', 'pitch': '+0Hz'}
CORPO = ['O Meu Cão Obedece é um passo a passo no celular. Quinze minutos por dia, durante vinte e um dias.',
         'O Adriano contou: ele parou de fazer xixi na sala. A Rafaella: agora ela anda do meu lado. E a Adriana: falo uma vez e ele já obedece.',
         'Um adestrador cobra até oitocentos reais. Aqui são trinta e sete reais, pagamento único, com sete dias de garantia.',
         'Faz o teste grátis e descobre o perfil do seu cão.']
VARIANTES = {
    'a-xixi': (['SEU CACHORRO', 'FAZ XIXI', 'NA CASA TODA?'], 'Seu cachorro faz xixi na casa toda e não te obedece?'),
    'b-grito': (['PARA DE', 'GRITAR COM', 'SEU CACHORRO'], 'Para de gritar com o seu cachorro. Ele não é teimoso, ele só não te entende.'),
    'c-800': (['ADESTRADOR', 'COBRANDO', 'R$ 800?'], 'Ia pagar oitocentos reais num adestrador? Olha isso antes.'),
}
DEPS = [{'nome': 'Adriano', 'cao': 'tutor do Rex', 'frase': 'Parou de fazer xixi na sala', 'img': 'deps/dep0.jpg'},
        {'nome': 'Rafaella', 'cao': 'tutora da Xena', 'frase': 'Anda do meu lado sem puxar', 'img': 'deps/dep1.jpg'},
        {'nome': 'Adriana', 'cao': 'tutora do Theu', 'frase': 'Falo uma vez e ele obedece', 'img': 'deps/dep2.jpg'}]
FPS = 30


async def tts(texto, saida):
    import edge_tts
    await edge_tts.Communicate(texto, VOZ['voz'], rate=VOZ['rate'], pitch=VOZ['pitch']).save(str(saida))


def wav(mp3, w):
    subprocess.run(['ffmpeg', '-y', '-v', 'error', '-i', str(mp3), '-ac', '1', '-ar', str(SR), str(w)], check=True)
    return wavfile.read(w)[1].astype(np.float32) / 32768


def palavras_whisper(modelo, voz, seg, falas):
    segs, _ = modelo.transcribe(resample_poly(voz, 160, 441).astype(np.float32), language='pt', word_timestamps=True)
    ws = [w for s in segs for w in s.words]
    out = []
    for g, texto in zip(seg, falas):  # texto do roteiro + tempo do Whisper (nomes e números sempre certos)
        dentro = [w for w in ws if g['ini'] - .2 <= (w.start + w.end) / 2 <= g['fim'] + .2]
        roteiro = texto.split()
        if len(dentro) == len(roteiro):
            out += [{'w': r, 'ini': round(w.start, 3), 'fim': round(w.end, 3)} for r, w in zip(roteiro, dentro)]
        else:
            out += [{'w': w.word.strip(), 'ini': round(w.start, 3), 'fim': round(w.end, 3)} for w in dentro]
    return out


def main():
    (AQUI / 'explosao.json').write_text(json.dumps(lottie_gen.explosao())); (AQUI / 'susto.json').write_text(json.dumps(lottie_gen.susto()))
    from faster_whisper import WhisperModel
    modelo = WhisperModel('small', device='cpu', compute_type='int8')
    saida = AQUI / 'videos'; saida.mkdir(exist_ok=True)
    for nome, (gancho, fala_gancho) in VARIANTES.items():
        pasta = Path(tempfile.mkdtemp(prefix='ad-'))
        falas = [fala_gancho] + CORPO
        partes, seg, t = [np.zeros(int(SR * .3))], [], .3
        for i, texto in enumerate(falas):
            mp3 = pasta / f'f{i}.mp3'; asyncio.run(tts(texto, mp3)); x = wav(mp3, pasta / f'f{i}.wav')
            nz = np.where(np.abs(x) > .01)[0]; x = x[max(0, nz[0] - 600): nz[-1] + 1400]
            pausa = .5 if i == 0 else .35
            seg.append({'ini': round(t, 3), 'fim': round(t + len(x) / SR, 3)})
            partes += [x, np.zeros(int(SR * pausa))]; t += len(x) / SR + pausa
        voz = np.concatenate(partes); wavfile.write(pasta / 'voz.wav', SR, (voz * 32767).astype(np.int16))
        pal = palavras_whisper(modelo, voz, seg, falas)
        dur = round(seg[-1]['fim'] + 2.0, 2)
        work = pasta / 'pg'; work.mkdir()
        for f in ['svgs.js', 'base.js']: shutil.copy(RAIZ / 'motor' / f, work / f)
        shutil.copytree(RAIZ / 'motor' / 'fontes', work / 'fontes'); shutil.copytree(AQUI / 'deps', work / 'deps')
        shutil.copy(RAIZ / 'node_modules' / 'gsap' / 'dist' / 'gsap.min.js', work)
        shutil.copy(RAIZ / 'node_modules' / 'lottie-web' / 'build' / 'player' / 'lottie.min.js', work)
        shutil.copy(AQUI / 'anuncio.html', work)
        (work / 'dados.js').write_text('const PALAVRAS=%s;const SEG=%s;const DUR=%s;const GANCHO=%s;const DEPS=%s;const LOTTIE_EXPLOSAO=%s;const LOTTIE_SUSTO=%s;' % (
            json.dumps(pal, ensure_ascii=False), json.dumps(seg), dur, json.dumps(gancho, ensure_ascii=False), json.dumps(DEPS, ensure_ascii=False),
            (AQUI / 'explosao.json').read_text(), (AQUI / 'susto.json').read_text()), encoding='utf-8')
        sfx = asyncio.run(gravar(work, pasta / 'mudo.mp4', dur, pasta / 'capa.jpg'))
        wavfile.write(pasta / 'sfx.wav', SR, (np.clip(gerar_sfx(sfx, dur, 9), -1, 1) * 32767).astype(np.int16))
        wavfile.write(pasta / 'mus.wav', SR, (np.clip(gerar_musica(dur, 1, []), -1, 1) * 32767).astype(np.int16))
        final = saida / f'anuncio-{nome}.mp4'
        subprocess.run(['ffmpeg', '-y', '-v', 'error', '-i', str(pasta / 'mudo.mp4'), '-i', str(pasta / 'voz.wav'), '-i', str(pasta / 'mus.wav'), '-i', str(pasta / 'sfx.wav'),
                        '-filter_complex',
                        '[1:a]apad,highpass=f=80,acompressor=threshold=-18dB:ratio=3:attack=5:release=80,volume=1.7,asplit=2[v][vs];'
                        '[2:a]volume=0.4[m];[m][vs]sidechaincompress=threshold=0.03:ratio=8:attack=20:release=300[md];[3:a]volume=0.45[s];'
                        '[v][md][s]amix=inputs=3:normalize=0:duration=longest,alimiter=limit=0.95[a]',
                        '-map', '0:v', '-map', '[a]', '-c:v', 'libx264', '-crf', '19', '-preset', 'medium', '-pix_fmt', 'yuv420p', '-r', str(FPS),
                        '-c:a', 'aac', '-b:a', '160k', '-t', str(dur), '-movflags', '+faststart', str(final)], check=True)
        shutil.copy(pasta / 'capa.jpg', saida / f'capa-{nome}.jpg')
        print('Pronto:', final, dur, 's', flush=True)


async def gravar(work, saida, dur, capa):
    from playwright.async_api import async_playwright
    async with async_playwright() as p:
        b = await p.chromium.launch(); pg = await b.new_page(viewport={'width': 1080, 'height': 1920})
        erros = []; pg.on('pageerror', lambda e: erros.append(str(e)))
        await pg.goto((work / 'anuncio.html').as_uri())
        await pg.evaluate("Promise.all(['600 50px FR','700 50px FR','800 50px NU','900 50px NU'].map(x=>document.fonts.load(x))).then(()=>load())")
        if erros: raise RuntimeError('Erro na página: ' + erros[0])
        sfx = await pg.evaluate('SFX')
        await pg.evaluate('render(1.2)'); await pg.screenshot(path=str(capa), type='jpeg', quality=90)
        ff = subprocess.Popen(['ffmpeg', '-y', '-v', 'error', '-f', 'image2pipe', '-framerate', str(FPS), '-c:v', 'mjpeg', '-i', '-',
                               '-c:v', 'libx264', '-pix_fmt', 'yuv420p', '-crf', '17', '-preset', 'medium', str(saida)], stdin=subprocess.PIPE)
        for i in range(int(FPS * dur)):
            await pg.evaluate(f'render({i / FPS})')
            ff.stdin.write(await pg.screenshot(type='jpeg', quality=92))
        ff.stdin.close(); ff.wait(); await b.close()
        if erros: raise RuntimeError('Erro na página: ' + erros[0])
        return sfx


if __name__ == '__main__':
    main()
