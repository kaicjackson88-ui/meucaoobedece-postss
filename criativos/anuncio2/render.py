"""Anúncio completo em motion 3D (DOM + CSS 3D + GSAP): dores → como funciona → gamificação → skins →
provas sociais em janelas 3D → certificado → oferta/garantia → chamada pro quiz.
Usa o mascote real da página de vendas (mascote.js) e os depoimentos reais autorizados.
python criativos/anuncio2/render.py"""
import asyncio, json, shutil, subprocess, sys, tempfile
from pathlib import Path

AQUI = Path(__file__).resolve().parent
RAIZ = AQUI.parents[1]
sys.path.insert(0, str(RAIZ / 'scripts'))
import numpy as np  # noqa: E402
from scipy.io import wavfile  # noqa: E402
from scipy.signal import resample_poly  # noqa: E402
from reels_audio import gerar_sfx, gerar_musica, SR  # noqa: E402

VOZ = {'voz': 'pt-BR-FranciscaNeural', 'rate': '+8%', 'pitch': '+0Hz'}
FALAS = [
    'Seu cachorro faz xixi na sala, puxa na guia e finge que não te escuta?',
    'Ele não é teimoso. Ele só nunca entendeu o que você pede.',
    'No Meu Cão Obedece, você abre o painel e o exercício do dia já está lá. Quinze minutos, marca como feito, e amanhã o próximo dia destrava.',
    'E virou jogo: você monta o mascote do seu cão, com mais de quatrocentas mil combinações. Cada dia concluído libera um apetrecho novo.',
    'Toda semana, uma skin nova: Aventureiro, Guardião e Lendário.',
    'E quem já fez, conta: parou o xixi na sala, anda do lado sem puxar, obedece de primeira.',
    'No dia vinte e um, sai o certificado com o nome dele, pra baixar e imprimir.',
    'Um adestrador cobra até oitocentos reais. Aqui são trinta e sete, pagamento único, com sete dias de garantia: não gostou, devolvemos tudo.',
    'Faz o quiz grátis agora e descobre o perfil do seu cão. Toca em saiba mais.',
]
DEPS = [{'nome': 'Adriano', 'cao': 'tutor do Rex', 'frase': 'Parou de fazer xixi na sala', 'img': 'deps/dep0.jpg'},
        {'nome': 'Rafaella', 'cao': 'tutora da Xena', 'frase': 'Anda do meu lado sem puxar', 'img': 'deps/dep1.jpg'},
        {'nome': 'Adriana', 'cao': 'tutora do Theu', 'frase': 'Falo uma vez e ele obedece', 'img': 'deps/dep2.jpg'},
        {'nome': 'Amanda', 'cao': 'tutora do Apollo', 'frase': 'Visita chega e ele fica sentado', 'img': 'deps/dep3.jpg'},
        {'nome': 'Hugo', 'cao': 'tutor da Rosquinha', 'frase': 'Resolvi tudo com R$ 37', 'img': 'deps/dep4.jpg'}]
FPS = 30


async def tts(texto, saida):
    """Voz da Microsoft; se ela recusar, Kokoro (neural offline); por último Piper."""
    import edge_tts
    if not MOTOR.get('fora'):
        for i in range(2):
            try:
                await edge_tts.Communicate(texto, VOZ['voz'], rate=VOZ['rate'], pitch=VOZ['pitch']).save(str(saida)); MOTOR['usado'] = 'edge'; return
            except Exception as e:  # noqa: BLE001
                print('  voz Microsoft falhou:', str(e)[:60], flush=True); await asyncio.sleep(5)
        MOTOR['fora'] = True
    import voz_offline
    try:
        voz_offline.falar_kokoro(texto, saida, 'pf_dora', 1.08); MOTOR['usado'] = 'kokoro'; return
    except Exception as e:  # noqa: BLE001
        print('  Kokoro falhou:', str(e)[:200], flush=True)
    voz_offline.falar(texto, saida, velocidade=1.05); MOTOR['usado'] = 'piper'


MOTOR = {}


def wav(mp3, w):
    subprocess.run(['ffmpeg', '-y', '-v', 'error', '-i', str(mp3), '-ac', '1', '-ar', str(SR), str(w)], check=True)
    return wavfile.read(w)[1].astype(np.float32) / 32768


def palavras_whisper(voz, seg):
    from faster_whisper import WhisperModel
    modelo = WhisperModel('small', device='cpu', compute_type='int8')
    segs, _ = modelo.transcribe(resample_poly(voz, 160, 441).astype(np.float32), language='pt', word_timestamps=True)
    ws = [w for s in segs for w in s.words]
    out = []
    for g, texto in zip(seg, FALAS):  # texto do roteiro + tempo do Whisper
        dentro = [w for w in ws if g['ini'] - .2 <= (w.start + w.end) / 2 <= g['fim'] + .2]
        roteiro = texto.split()
        if len(dentro) == len(roteiro):
            out += [{'w': r, 'ini': round(w.start, 3), 'fim': round(w.end, 3)} for r, w in zip(roteiro, dentro)]
        else:  # distribui as palavras do roteiro no tempo da fala, proporcional ao tamanho
            tot = sum(len(r) + 2 for r in roteiro); t = g['ini']
            for r in roteiro:
                d = (g['fim'] - g['ini']) * (len(r) + 2) / tot
                out.append({'w': r, 'ini': round(t, 3), 'fim': round(t + d * .9, 3)}); t += d
    return out


async def gravar(work, saida, dur, capa):
    from playwright.async_api import async_playwright
    async with async_playwright() as p:
        b = await p.chromium.launch()
        pg = await b.new_page(viewport={'width': 1080, 'height': 1920})
        erros = []; pg.on('pageerror', lambda e: erros.append(str(e)))
        await pg.goto((work / 'anuncio.html').as_uri())
        await pg.evaluate("Promise.all(['600 50px FR','700 50px FR','800 50px NU','900 50px NU'].map(x=>document.fonts.load(x)))")
        await pg.evaluate('load()')
        await pg.wait_for_function('[...document.images].every(i=>i.complete)')
        if erros: raise RuntimeError('Erro na página: ' + erros[0])
        sfx = await pg.evaluate('SFX')
        await pg.evaluate('render(1.3)'); await pg.screenshot(path=str(capa), type='jpeg', quality=90)
        ff = subprocess.Popen(['ffmpeg', '-y', '-v', 'error', '-f', 'image2pipe', '-framerate', str(FPS), '-c:v', 'mjpeg', '-i', '-',
                               '-c:v', 'libx264', '-pix_fmt', 'yuv420p', '-crf', '17', '-preset', 'medium', str(saida)], stdin=subprocess.PIPE)
        n = int(FPS * dur)
        for i in range(n):
            await pg.evaluate(f'render({i / FPS})')
            ff.stdin.write(await pg.screenshot(type='jpeg', quality=92))
            if i % 150 == 0: print(f'  quadro {i}/{n}', flush=True)
        ff.stdin.close(); ff.wait(); await b.close()
        if erros: raise RuntimeError('Erro na página: ' + erros[0])
        return sfx


def main():
    pasta = Path(tempfile.mkdtemp(prefix='ad2-'))
    partes, seg, t = [np.zeros(int(SR * .3))], [], .3
    for i, texto in enumerate(FALAS):
        mp3 = pasta / f'f{i}.mp3'; asyncio.run(tts(texto, mp3)); x = wav(mp3, pasta / f'f{i}.wav')
        nz = np.where(np.abs(x) > .01)[0]; x = x[max(0, nz[0] - 600): nz[-1] + 1400]
        pausa = .45 if i in (0, 1) else .32
        seg.append({'ini': round(t, 3), 'fim': round(t + len(x) / SR, 3)})
        partes += [x, np.zeros(int(SR * pausa))]; t += len(x) / SR + pausa
    voz = np.concatenate(partes); wavfile.write(pasta / 'voz.wav', SR, (voz * 32767).astype(np.int16))
    pal = palavras_whisper(voz, seg)
    dur = round(seg[-1]['fim'] + 2.2, 2)
    print('Duração:', dur, 's — voz:', MOTOR.get('usado'), flush=True)
    work = pasta / 'pg'; work.mkdir()
    shutil.copytree(RAIZ / 'motor' / 'fontes', work / 'fontes'); shutil.copytree(AQUI / 'deps', work / 'deps')
    shutil.copy(RAIZ / 'node_modules' / 'gsap' / 'dist' / 'gsap.min.js', work)
    for f in ['anuncio.html', 'mascote.js']: shutil.copy(AQUI / f, work)
    (work / 'dados.js').write_text('const PALAVRAS=%s;const SEG=%s;const DUR=%s;const DEPS=%s;const NOME_CAO="Thor";' % (
        json.dumps(pal, ensure_ascii=False), json.dumps(seg), dur, json.dumps(DEPS, ensure_ascii=False)), encoding='utf-8')
    saida = AQUI / 'videos'; saida.mkdir(exist_ok=True)
    sfx = asyncio.run(gravar(work, pasta / 'mudo.mp4', dur, saida / 'capa-completo.jpg'))
    wavfile.write(pasta / 'sfx.wav', SR, (np.clip(gerar_sfx(sfx, dur, 11), -1, 1) * 32767).astype(np.int16))
    wavfile.write(pasta / 'mus.wav', SR, (np.clip(gerar_musica(dur, 2, []), -1, 1) * 32767).astype(np.int16))
    final = saida / 'anuncio-completo.mp4'
    subprocess.run(['ffmpeg', '-y', '-v', 'error', '-i', str(pasta / 'mudo.mp4'), '-i', str(pasta / 'voz.wav'), '-i', str(pasta / 'mus.wav'), '-i', str(pasta / 'sfx.wav'),
                    '-filter_complex',
                    '[1:a]apad,highpass=f=80,acompressor=threshold=-18dB:ratio=3:attack=5:release=80,volume=1.7,asplit=2[v][vs];'
                    '[2:a]volume=0.4[m];[m][vs]sidechaincompress=threshold=0.03:ratio=8:attack=20:release=300[md];[3:a]volume=0.45[s];'
                    '[v][md][s]amix=inputs=3:normalize=0:duration=longest,alimiter=limit=0.95[a]',
                    '-map', '0:v', '-map', '[a]', '-c:v', 'libx264', '-crf', '19', '-preset', 'medium', '-pix_fmt', 'yuv420p', '-r', str(FPS),
                    '-c:a', 'aac', '-b:a', '160k', '-t', str(dur), '-movflags', '+faststart', str(final)], check=True)
    subprocess.run(['ffmpeg', '-y', '-v', 'error', '-i', str(final), '-c:v', 'libx264', '-crf', '24', '-maxrate', '6M', '-bufsize', '12M', '-preset', 'medium',
                    '-c:a', 'copy', '-movflags', '+faststart', str(saida / 'envio-completo.mp4')], check=True)
    print('Pronto:', final, dur, 's', flush=True)


if __name__ == '__main__':
    main()
