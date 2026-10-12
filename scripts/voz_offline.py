"""Voz reserva grátis e offline (Piper, pt-BR) — usada só se o serviço de voz da Microsoft cair.
falar(texto, 'saida.wav', voz='narrador'|'ana')"""
import urllib.request, wave
from pathlib import Path

CACHE = Path.home() / '.cache' / 'piper'
HF = 'https://huggingface.co/rhasspy/piper-voices/resolve/main/pt/pt_BR/{n}/{q}/pt_BR-{n}-{q}.onnx'
VOZES = {'narrador': ('faber', 'medium'), 'ana': ('faber', 'medium')}
_cache = {}


def _modelo(nome, q):
    CACHE.mkdir(parents=True, exist_ok=True)
    m = CACHE / f'pt_BR-{nome}-{q}.onnx'
    for f, url in ((m, HF.format(n=nome, q=q)), (Path(str(m) + '.json'), HF.format(n=nome, q=q) + '.json')):
        if not f.exists():
            urllib.request.urlretrieve(url + '?download=true', f)
    return m


def falar(texto, saida, voz='narrador', velocidade=1.0):
    try:
        from piper import PiperVoice
    except ImportError:  # instala na hora se o robô já estava rodando sem ela
        import subprocess, sys
        subprocess.run([sys.executable, '-m', 'pip', 'install', '-q', 'piper-tts'], check=True)
        from piper import PiperVoice
    nome, q = VOZES.get(voz, VOZES['narrador'])
    if nome not in _cache: _cache[nome] = PiperVoice.load(str(_modelo(nome, q)))
    v = _cache[nome]
    with wave.open(str(saida), 'wb') as w:
        if hasattr(v, 'synthesize_wav'):  # piper-tts >= 1.3
            from piper import SynthesisConfig
            v.synthesize_wav(texto, w, syn_config=SynthesisConfig(length_scale=1 / velocidade))
        else:
            v.synthesize(texto, w, length_scale=1 / velocidade)
    return saida


_kok = {}


def falar_kokoro(texto, saida, voz='pf_dora', velocidade=1.0):
    """Voz neural grátis e offline (Kokoro-82M, pt-BR: pf_dora feminina, pm_alex masculina). Mais natural que o Piper."""
    import numpy as np
    from scipy.io import wavfile
    from kokoro import KPipeline
    if 'p' not in _kok: _kok['p'] = KPipeline(lang_code='p')
    partes = [np.asarray(a, dtype=np.float32) for _, _, a in _kok['p'](texto, voice=voz, speed=velocidade)]
    x = np.concatenate(partes) if partes else np.zeros(2400, np.float32)
    wavfile.write(str(saida), 24000, (np.clip(x, -1, 1) * 32767).astype(np.int16))
    return saida
