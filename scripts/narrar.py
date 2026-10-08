"""Gera narração (MP3) e o tempo de cada palavra (JSON) a partir de um roteiro.

Uso: python scripts/narrar.py <arquivo_roteiro.txt> <pasta_saida> [voz] [velocidade]
Saída: <pasta_saida>/narracao.mp3 e <pasta_saida>/palavras.json
"""
import asyncio
import json
import sys
from pathlib import Path

import edge_tts


async def main(roteiro, saida, voz, rate):
    texto = Path(roteiro).read_text(encoding="utf-8").strip()
    saida = Path(saida)
    saida.mkdir(parents=True, exist_ok=True)
    com = edge_tts.Communicate(texto, voz, rate=rate, boundary="WordBoundary")
    palavras = []
    with open(saida / "narracao.mp3", "wb") as f:
        async for parte in com.stream():
            if parte["type"] == "audio":
                f.write(parte["data"])
            elif parte["type"] == "WordBoundary":
                palavras.append({
                    "palavra": parte["text"],
                    "inicio": round(parte["offset"] / 1e7, 3),
                    "fim": round((parte["offset"] + parte["duration"]) / 1e7, 3),
                })
    (saida / "palavras.json").write_text(json.dumps(palavras, ensure_ascii=False, indent=1), encoding="utf-8")
    print(f"{len(palavras)} palavras, termina em {palavras[-1]['fim'] if palavras else 0}s")


if __name__ == "__main__":
    voz = sys.argv[3] if len(sys.argv) > 3 else "pt-BR-AntonioNeural"
    rate = sys.argv[4] if len(sys.argv) > 4 else "+8%"
    asyncio.run(main(sys.argv[1], sys.argv[2], voz, rate))
