"""Sons sintetizados (sem direitos autorais) e trilha para os Reels."""
import numpy as np
from scipy.signal import butter, sosfilt

SR = 44100


def _t(d): return np.arange(int(SR * d)) / SR
def _env(n, a=.005, r=.1):
    t = np.arange(n) / SR
    return np.minimum(1, t / a) * np.exp(-t / r)
def _bp(x, lo, hi): return sosfilt(butter(2, [lo, hi], 'band', fs=SR, output='sos'), x)
def _lp(x, f): return sosfilt(butter(2, f, 'low', fs=SR, output='sos'), x)
def _hp(x, f): return sosfilt(butter(2, f, 'high', fs=SR, output='sos'), x)


def gerar_sfx(eventos, dur, seed=7):
    rng = np.random.default_rng(seed)
    def whoosh():
        d = .5; t = _t(d); n = rng.standard_normal(len(t)); out = np.zeros_like(t); seg = 512
        for i in range(0, len(t), seg):
            p = i / len(t); f = 300 + 3200 * np.sin(np.pi * p) ** 2
            out[i:i + seg] = _bp(n[i:i + seg], max(80, f * .6), min(SR / 2 - 100, f * 1.4))[:len(out[i:i + seg])]
        return _lp(out * np.sin(np.pi * np.clip(t / d, 0, 1)) ** 2, 6000) * 1.6
    def pop():
        t = _t(.12); f = 900 * np.exp(-t * 30) + 380
        return np.sin(2 * np.pi * np.cumsum(f) / SR) * _env(len(t), .002, .035) * .7
    def ding():
        t = _t(1.2)
        x = sum(a * np.sin(2 * np.pi * f * t) * np.exp(-t * k) for f, a, k in [(1318, 1, 3), (2637, .4, 5), (1975, .3, 4)])
        return x * np.minimum(1, t / .003) * .3
    def boom():
        t = _t(.7); f = 110 * np.exp(-t * 6) + 38
        s = np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-t * 5)
        return (s + _lp(rng.standard_normal(len(t)), 900) * np.exp(-t * 14) * .5) * np.minimum(1, t / .002) * .9
    def sucesso():
        out = np.zeros(int(SR * 1.0))
        for i, f in enumerate([784, 988, 1175, 1568]):
            t = _t(.5); x = (np.sin(2 * np.pi * f * t) + .3 * np.sin(4 * np.pi * f * t)) * _env(len(t), .003, .14)
            s = int(i * .07 * SR); out[s:s + len(x)] += x * .28
        return out
    def doorbell():
        out = np.zeros(int(SR * 1.3))
        for f, st in [(659, 0), (523, .38)]:
            t = _t(.9); x = sum(a * np.sin(2 * np.pi * f * h * t) * np.exp(-t * kk) for h, a, kk in [(1, 1, 3.5), (2.01, .35, 6), (3, .15, 9)])
            x *= np.minimum(1, t / .004) * .42; s = int(st * SR); out[s:s + len(x)] += x
        return out
    def tick():
        t = _t(.03); return np.sin(2 * np.pi * 2200 * t) * _env(len(t), .001, .008) * .5
    def riser():
        d = 3.2; t = _t(d); f = 200 + 1400 * (t / d) ** 2
        x = np.sin(2 * np.pi * np.cumsum(f) / SR) * .25 + _hp(rng.standard_normal(len(t)), 1500) * .25 * (t / d)
        return x * (t / d) ** 1.6 * np.minimum(1, (d - t) / .05)
    def tipo():
        t = _t(.04); return _hp(rng.standard_normal(len(t)), 2500) * _env(len(t), .001, .01) * .7
    def notif():
        out = np.zeros(int(SR * .8))
        for f, st in [(1047, 0), (1568, .12)]:
            t = _t(.5); x = np.sin(2 * np.pi * f * t) * _env(len(t), .003, .12) * .35; s = int(st * SR); out[s:s + len(x)] += x
        return out
    def sirene():
        d = 1.0; t = _t(d); f = 700 + 250 * np.sin(2 * np.pi * 3 * t)
        x = np.sign(np.sin(2 * np.pi * np.cumsum(f) / SR)) * .12
        return _lp(x, 3000) * np.minimum(1, t / .02) * np.minimum(1, (d - t) / .2)
    gen = {'whoosh': (whoosh, .7), 'pop': (pop, .45), 'ding': (ding, .6), 'boom': (boom, .8), 'sucesso': (sucesso, .55),
           'doorbell': (doorbell, .8), 'tick': (tick, .3), 'riser': (riser, .55), 'tipo': (tipo, .5), 'notif': (notif, .8), 'sirene': (sirene, .5)}
    N = int(SR * dur); out = np.zeros(N)
    for k, ts in eventos.items():
        if k not in gen: continue
        g, vol = gen[k]
        for tt in ts:
            x = g() * vol; s = int(max(0, tt) * SR); e = min(N, s + len(x))
            if s < N: out[s:e] += x[:e - s]
    return out


PROGRESSOES = [([60, 64, 67], [55, 59, 62], [57, 60, 64], [53, 57, 60]),   # I V vi IV
               ([57, 60, 64], [53, 57, 60], [60, 64, 67], [55, 59, 62]),   # vi IV I V
               ([62, 65, 69], [58, 62, 65], [60, 64, 67], [57, 60, 64]),
               ([55, 59, 62], [52, 55, 59], [60, 64, 67], [62, 66, 69])]


def gerar_musica(dur, seed=0, cortes=()):
    rng = np.random.default_rng(seed)
    bpm = [104, 108, 112, 116, 120][seed % 5]; beat = 60 / bpm; N = int(SR * dur); mus = np.zeros(N)
    prog = PROGRESSOES[seed % len(PROGRESSOES)]
    def note(m): return 440 * 2 ** ((m - 69) / 12)
    def pluck(f, d=.5, v=.25):
        t = _t(d); x = sum(np.sin(2 * np.pi * f * h * t) / h ** 1.3 for h in range(1, 6))
        return x * _env(len(t), .004, .16) * v
    def put(x, tt):
        s = int(tt * SR); e = min(N, s + len(x))
        if s < N: mus[s:e] += x[:e - s]
    arp = [0, 1, 2, 1, 0, 2, 1, 2]
    for b in range(int(dur / beat) + 2):
        bar = (b // 4) % 4; tb = b * beat; ch = prog[bar]
        if b % 2 == 0: put(pluck(note(ch[0] - 24), beat * .9, .35), tb)
        for k in range(2): put(pluck(note(ch[arp[(b * 2 + k) % 8]] + 12), .4, .13), tb + k * beat / 2)
        t = _t(.25)
        if b % 2 == 0: put(np.sin(2 * np.pi * np.cumsum(120 * np.exp(-t * 25) + 45) / SR) * np.exp(-t * 12) * .45, tb)
        if b % 2 == 1: put(_bp(rng.standard_normal(int(SR * .15)), 900, 4000) * _env(int(SR * .15), .002, .05) * .25, tb)
        for k in range(2): put(_hp(rng.standard_normal(int(SR * .05)), 6000) * _env(int(SR * .05), .001, .015) * .12, tb + k * beat / 2 + beat / 4)
    tt = np.arange(N) / SR; gate = np.ones(N)
    for a, b in cortes: gate[(tt > a) & (tt < b)] = 0
    gate = np.convolve(gate, np.ones(800) / 800, 'same')
    mus *= gate * np.minimum(1, tt / .3) * np.clip((dur - tt) / .6, 0, 1)
    return mus * .8
