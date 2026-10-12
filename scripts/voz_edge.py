"""Mantém o edge-tts funcionando quando a Microsoft passa a exigir uma versão mais nova do Edge (erro 403).
aplicar_salva() usa a versão guardada em dados/voz_versao.txt; descobrir_versao() testa versões novas e guarda a que funcionar."""
import asyncio
from pathlib import Path

ARQ = Path(__file__).resolve().parents[1] / 'dados' / 'voz_versao.txt'


def versao_atual():
    import edge_tts.communicate as c
    return c.SEC_MS_GEC_VERSION.split('-', 1)[1]


def aplicar(v):
    import edge_tts.communicate as c, edge_tts.constants as k
    maior = v.split('.')[0]
    c.SEC_MS_GEC_VERSION = k.SEC_MS_GEC_VERSION = '1-' + v
    for h in (c.WSS_HEADERS, k.WSS_HEADERS, k.BASE_HEADERS):
        h['User-Agent'] = ('Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) '
                           f'Chrome/{maior}.0.0.0 Safari/537.36 Edg/{maior}.0.0.0')
    try:
        import edge_tts.voices as vv
        vv.SEC_MS_GEC_VERSION = '1-' + v
    except Exception:  # noqa: BLE001
        pass


def aplicar_salva():
    try:
        v = ARQ.read_text().strip()
        if v: aplicar(v)
        return v
    except FileNotFoundError:
        return ''


async def _ok():
    import edge_tts
    n = 0
    async for m in edge_tts.Communicate('Teste.', 'pt-BR-FranciscaNeural').stream():
        if m['type'] == 'audio': n += 1
    return n > 0


def descobrir_versao(log=print):
    base = 143, 3650
    for maior in range(144, 162):
        for build in (base[1] + (maior - base[0]) * 60, base[1] + (maior - base[0]) * 75):
            v = f'{maior}.0.{build}.{50 + maior % 40}'
            aplicar(v)
            try:
                if asyncio.run(_ok()):
                    ARQ.write_text(v + '\n'); log(f'  {v}: OK'); return v
            except Exception as e:  # noqa: BLE001
                log(f'  {v}: {str(e)[:40]}')
    return None
