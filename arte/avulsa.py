"""Gera imagens avulsas com o modelo de imagem do Gemini (GEMINI_API_KEY), a partir de arte/avulsa.json:
[{"id": "nome", "proporcao": "1:1", "prompt": "...", "ref": "id_de_uma_imagem_ja_gerada (opcional)"}]
Salva em avulsas/<id>.png. Não posta nada. python arte/avulsa.py"""
import base64, json, sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import gerar_arte as g  # noqa: E402

SAIDA = Path(__file__).resolve().parents[1] / 'avulsas'
SAIDA.mkdir(exist_ok=True)


def gerar(modelo, texto, proporcao, refs):
    partes = [g.parte_img(r) for r in refs] + [{'text': texto}]
    corpo = {'contents': [{'parts': partes}], 'generationConfig': {'responseModalities': ['IMAGE', 'TEXT'], 'imageConfig': {'aspectRatio': proporcao}}}
    url = f'{g.API}/models/{modelo}:generateContent?key={g.CHAVE}'
    try:
        r = g.pedir(url, corpo)
    except RuntimeError as e:
        if 'HTTP 400' not in str(e): raise
        corpo['generationConfig'].pop('imageConfig'); r = g.pedir(url, corpo)
    for c in r.get('candidates', []):
        for p in c.get('content', {}).get('parts', []):
            d = p.get('inlineData') or p.get('inline_data')
            if d: return base64.b64decode(d['data'])
    raise RuntimeError('sem imagem na resposta: ' + json.dumps(r)[:300])


def main():
    itens = json.loads((Path(__file__).resolve().parent / 'avulsa.json').read_text(encoding='utf-8'))
    modelos = g.modelos_imagem()
    for it in itens:
        refs = [SAIDA / f"{it['ref']}.png"] if it.get('ref') and (SAIDA / f"{it['ref']}.png").exists() else []
        for m in modelos:
            try:
                (SAIDA / f"{it['id']}.png").write_bytes(gerar(m, it['prompt'], it.get('proporcao', '1:1'), refs))
                print('OK', it['id'], m, flush=True); break
            except Exception as e:  # noqa: BLE001
                print('falhou', it['id'], m, str(e)[:200], flush=True)


if __name__ == '__main__':
    main()
