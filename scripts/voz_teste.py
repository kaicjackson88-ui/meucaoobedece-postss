"""Diagnóstico da voz: testa o edge-tts como está, com versões mais novas do Edge, e a voz offline (Piper).
Escreve o resultado em dados/voz_teste.txt. python scripts/voz_teste.py"""
import asyncio, sys, time
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RAIZ / 'scripts'))
out = []


def log(s):
    print(s, flush=True); out.append(s)
    (RAIZ / 'dados' / 'voz_teste.txt').write_text('\n'.join(out) + '\n')


async def tenta(saida):
    import edge_tts
    await edge_tts.Communicate('Teste de voz do Meu Cão Obedece.', 'pt-BR-FranciscaNeural').save(str(saida))


def main():
    import voz_edge
    log('padrão: ' + voz_edge.versao_atual())
    try:
        asyncio.run(tenta('/tmp/v0.mp3')); log('OK com a versão padrão')
    except Exception as e:  # noqa: BLE001
        log('falhou padrão: ' + str(e)[:90])
        log('versão que funciona: ' + str(voz_edge.descobrir_versao(log)))
    t = time.time()
    try:
        import voz_offline
        voz_offline.falar('Seu cachorro não é teimoso. Ele só nunca entendeu o que você pede.', '/tmp/p.wav')
        log(f'Piper OK ({time.time() - t:.1f}s)')
    except Exception as e:  # noqa: BLE001
        log('Piper falhou: ' + str(e)[:200])
    (RAIZ / 'dados' / 'voz_teste.txt').write_text('\n'.join(out) + '\n')


if __name__ == '__main__':
    main()
