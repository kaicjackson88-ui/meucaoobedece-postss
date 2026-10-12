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
