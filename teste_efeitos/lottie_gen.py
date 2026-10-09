"""Gera duas animações Lottie próprias (estilo After Effects, sem material de terceiros):
explosao.json (estrelas + bolinhas na cor da marca) e susto.json (raios de susto)."""
import json, math, random
from pathlib import Path

AQUI = Path(__file__).parent
COR = {'amb': [0.91, 0.57, 0.24, 1], 'teal': [0.12, 0.48, 0.42, 1], 'red': [0.76, 0.25, 0.05, 1], 'cream': [0.99, 0.97, 0.93, 1], 'gold': [0.95, 0.75, 0.2, 1]}
E = {'i': {'x': 0.2, 'y': 1}, 'o': {'x': 0.3, 'y': 0}}


def kf(pares):
    out = []
    for k, (t, v) in enumerate(pares):
        d = {'t': t, 's': v if isinstance(v, list) else [v]}
        if k < len(pares) - 1: d.update(E)
        out.append(d)
    return {'a': 1, 'k': out}


def grupo(forma, cor, p0, p1, esc, rot, op_fim):
    return {'ty': 'gr', 'it': [forma, {'ty': 'fl', 'c': {'a': 0, 'k': cor}, 'o': {'a': 0, 'k': 100}},
            {'ty': 'tr', 'p': kf([(0, p0), (22, p1)]), 'a': {'a': 0, 'k': [0, 0]},
             's': kf([(0, [0, 0]), (7, [esc * 1.3, esc * 1.3]), (op_fim, [esc * .5, esc * .5])]),
             'r': kf([(0, 0), (op_fim, rot)]), 'o': kf([(0, 100), (op_fim - 10, 100), (op_fim, 0)]),
             'sk': {'a': 0, 'k': 0}, 'sa': {'a': 0, 'k': 0}}]}


def estrela(r): return {'ty': 'sr', 'sy': 1, 'd': 1, 'pt': {'a': 0, 'k': 5}, 'p': {'a': 0, 'k': [0, 0]}, 'r': {'a': 0, 'k': 0},
                        'ir': {'a': 0, 'k': r * .45}, 'is': {'a': 0, 'k': 0}, 'or': {'a': 0, 'k': r}, 'os': {'a': 0, 'k': 0}}
def bola(r): return {'ty': 'el', 'p': {'a': 0, 'k': [0, 0]}, 's': {'a': 0, 'k': [r * 2, r * 2]}}
def barra(w, h): return {'ty': 'rc', 'p': {'a': 0, 'k': [0, 0]}, 's': {'a': 0, 'k': [w, h]}, 'r': {'a': 0, 'k': h / 2}}


def anim(nome, grupos, op=40):
    camada = {'ddd': 0, 'ind': 1, 'ty': 4, 'nm': nome, 'sr': 1, 'ao': 0, 'ip': 0, 'op': op, 'st': 0, 'bm': 0,
              'ks': {'o': {'a': 0, 'k': 100}, 'r': {'a': 0, 'k': 0}, 'p': {'a': 0, 'k': [0, 0, 0]}, 'a': {'a': 0, 'k': [0, 0, 0]}, 's': {'a': 0, 'k': [100, 100, 100]}},
              'shapes': grupos}
    return {'v': '5.7.4', 'fr': 30, 'ip': 0, 'op': op, 'w': 700, 'h': 700, 'nm': nome, 'ddd': 0, 'assets': [], 'layers': [camada]}


def explosao():
    rnd = random.Random(3); g = []
    for i in range(22):
        a = i / 22 * 2 * math.pi + rnd.uniform(-.15, .15); d = rnd.uniform(170, 310)
        cor = [COR['amb'], COR['teal'], COR['gold'], COR['red'], COR['cream']][i % 5]
        forma = estrela(rnd.uniform(16, 28)) if i % 2 else bola(rnd.uniform(8, 15))
        g.append(grupo(forma, cor, [350, 350], [350 + math.cos(a) * d, 350 + math.sin(a) * d], 100, rnd.uniform(-200, 200), rnd.randint(30, 38)))
    return anim('explosao', g)


def susto():
    g = []
    for i in range(10):
        a = i / 10 * 2 * math.pi - math.pi / 2
        r0, r1 = 120, 250
        gg = grupo(barra(70, 16), COR['red'] if i % 2 else COR['amb'], [350 + math.cos(a) * r0, 350 + math.sin(a) * r0],
                   [350 + math.cos(a) * r1, 350 + math.sin(a) * r1], 100, 0, 26)
        gg['it'][2]['r'] = {'a': 0, 'k': math.degrees(a)}
        g.append(gg)
    return anim('susto', g, op=30)


if __name__ == '__main__':
    (AQUI / 'explosao.json').write_text(json.dumps(explosao()))
    (AQUI / 'susto.json').write_text(json.dumps(susto()))
    print('lottie ok')
