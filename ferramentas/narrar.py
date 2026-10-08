"""Gera narração em português (voz neural) + tempo de cada palavra.

Uso: python ferramentas/narrar.py roteiro.txt saida/ pt-BR-FranciscaNeural "+0%"
Saída: saida/voz.mp3 e saida/palavras.json  ->  [{"t": 0.12, "d": 0.30, "w": "Seu"}, ...]
"""
import asyncio
import json
import sys
from pathlib import Path

import edge_tts


async def main(roteiro, pasta, voz, ritmo):
    texto = Path(roteiro).read_text(encoding="utf-8").strip()
    pasta = Path(pasta)
    pasta.mkdir(parents=True, exist_ok=True)
    try:
        com = edge_tts.Communicate(texto, voz, rate=ritmo, boundary="WordBoundary")
    except TypeError:
        com = edge_tts.Communicate(texto, voz, rate=ritmo)
    palavras = []
    with open(pasta / "voz.mp3", "wb") as audio:
        async for parte in com.stream():
            if parte["type"] == "audio":
                audio.write(parte["data"])
            elif parte["type"] == "WordBoundary":
                palavras.append({
                    "t": round(parte["offset"] / 1e7, 3),
                    "d": round(parte["duration"] / 1e7, 3),
                    "w": parte["text"],
                })
    (pasta / "palavras.json").write_text(json.dumps(palavras, ensure_ascii=False, indent=1), encoding="utf-8")
    print(f"{voz}: {len(palavras)} palavras, termina em {palavras[-1]['t'] + palavras[-1]['d']:.1f}s")


if __name__ == "__main__":
    asyncio.run(main(*sys.argv[1:5]))
