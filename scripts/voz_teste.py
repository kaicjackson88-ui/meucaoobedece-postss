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


def teste_google():
    import json, voz_google
    if not voz_google.disponivel():
        log('Google: sem GEMINI_API_KEY'); return
    texto = 'Seu cachorro não é teimoso. Ele só nunca entendeu o que você está pedindo. E isso muda tudo.'
    tempos = {}
    for nome, voz in (('narrador', 'pt-BR-AntonioNeural'), ('ana', 'pt-BR-FranciscaNeural')):
        t = time.time()
        try:
            dest = RAIZ / 'dados' / f'voz_google_{nome}.mp3'
            pal = voz_google.falar(texto, str(dest), voz, '+6%')
            tempos[nome] = pal
            log(f'Google {nome} ({voz_google.voz_gemini(voz)}): OK {len(pal)} palavras, fim {pal[-1]["fim"]}s, {time.time() - t:.1f}s')
        except Exception as e:  # noqa: BLE001
            log(f'Google {nome} falhou: ' + str(e)[:300])
    (RAIZ / 'dados' / 'voz_google_tempos.json').write_text(json.dumps(tempos, ensure_ascii=False))


def main():
    teste_google()
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
    try:
        import reels
        for nome, voz in (('narrador', 'pt-BR-AntonioNeural'), ('ana', 'pt-BR-FranciscaNeural')):
            dest = RAIZ / 'dados' / f'voz_reserva_{nome}.mp3'
            pal = asyncio.run(reels._narrar('O Thor fez xixi no tapete novo. Thor, de novo não!', str(dest), voz, '+12%'))
            log(f'reserva {nome}: {len(pal)} palavras, {dest.stat().st_size} bytes, fim {pal[-1]["fim"]}s')
    except Exception as e:  # noqa: BLE001
        import traceback; log('reserva no robô falhou: ' + traceback.format_exc()[-400:])


if __name__ == '__main__':
    main()
