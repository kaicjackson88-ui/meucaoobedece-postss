"""Busca no Google Trends (Brasil, 12 meses) o interesse relativo pelas dores de comportamento canino.
Grava dados/google_trends.txt. Uso: python scripts/tendencias_google.py"""
import time, json
from pytrends.request import TrendReq

GRUPOS = [
    ['cachorro xixi', 'cachorro puxando', 'cachorro latindo', 'cachorro mordendo', 'ansiedade de separação'],
    ['cachorro xixi', 'adestramento', 'adestrar cachorro', 'cachorro pulando', 'cachorro não obedece'],
]
out = []
py = TrendReq(hl='pt-BR', tz=180, retries=3, backoff_factor=2)
for g in GRUPOS:
    for tent in range(4):
        try:
            py.build_payload(g, timeframe='today 12-m', geo='BR')
            df = py.interest_over_time()
            med = {k: round(float(df[k].mean()), 1) for k in g}
            out.append('MÉDIA 12 MESES (0-100, relativo dentro do grupo): ' + json.dumps(med, ensure_ascii=False))
            break
        except Exception as e:  # noqa: BLE001
            out.append(f'erro tentativa {tent}: {str(e)[:120]}'); time.sleep(20 * (tent + 1))
    time.sleep(15)
for termo in ['adestramento', 'cachorro xixi']:
    for tent in range(3):
        try:
            py.build_payload([termo], timeframe='today 12-m', geo='BR')
            rq = py.related_queries()[termo]
            for tipo in ('top', 'rising'):
                df = rq.get(tipo)
                if df is not None:
                    out.append(f'{termo} | buscas relacionadas {tipo}: ' + '; '.join(f'{r.query} ({r.value})' for r in df.head(15).itertuples()))
            reg = py.interest_by_region(resolution='REGION').sort_values(termo, ascending=False).head(8)
            out.append(f'{termo} | estados com mais interesse: ' + ', '.join(f'{i} ({int(v)})' for i, v in reg[termo].items()))
            break
        except Exception as e:  # noqa: BLE001
            out.append(f'erro {termo} tentativa {tent}: {str(e)[:120]}'); time.sleep(25 * (tent + 1))
    time.sleep(15)
texto = '\n'.join(out); print(texto)
open('dados/google_trends.txt', 'w', encoding='utf-8').write(texto + '\n')
