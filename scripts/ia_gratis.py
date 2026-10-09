"""IA gratuita (Google Gemini, plano grátis) — o "cérebro reserva" que roda sem o Claude.

Precisa do segredo GEMINI_API_KEY (chave grátis do Google AI Studio). Com pesquisar=True a IA usa a
Busca do Google embutida (grounding) para pesquisar na internet antes de responder.
(O GitHub Models, usado antes, foi encerrado pelo GitHub em 30/07/2026.)
"""
import json, os, time, urllib.error, urllib.request

MODELOS = [m.strip() for m in os.environ.get('GEMINI_MODELOS', 'gemini-2.5-flash,gemini-flash-latest,gemini-2.0-flash').split(',') if m.strip()]
BASE = 'https://generativelanguage.googleapis.com/v1beta/models/{m}:generateContent?key={k}'


def disponivel():
    return bool(os.environ.get('GEMINI_API_KEY', '').strip())


def perguntar(sistema, usuario, max_tokens=3500, temperatura=0.8, json_saida=False, pesquisar=False):
    chave = os.environ.get('GEMINI_API_KEY', '').strip()
    if not chave:
        raise RuntimeError('sem GEMINI_API_KEY (IA gratuita indisponível)')
    cfg = {'temperature': temperatura, 'maxOutputTokens': max_tokens}
    if json_saida and not pesquisar:
        cfg['responseMimeType'] = 'application/json'
    corpo = {'systemInstruction': {'parts': [{'text': sistema}]}, 'contents': [{'role': 'user', 'parts': [{'text': usuario}]}],
             'generationConfig': cfg}
    if pesquisar:
        corpo['tools'] = [{'google_search': {}}]
    ultimo = None
    for m in MODELOS:
        for tentativa in range(3):
            req = urllib.request.Request(BASE.format(m=m, k=chave), data=json.dumps(corpo).encode(), method='POST',
                                         headers={'Content-Type': 'application/json'})
            try:
                with urllib.request.urlopen(req, timeout=240) as r:
                    d = json.loads(r.read().decode())
                partes = d['candidates'][0]['content']['parts']
                texto = ''.join(p.get('text', '') for p in partes)
                fontes = [c.get('web', {}).get('uri') for c in d['candidates'][0].get('groundingMetadata', {}).get('groundingChunks', [])]
                if fontes:
                    texto += '\n\nFONTES:\n' + '\n'.join(f for f in fontes if f)
                return texto
            except urllib.error.HTTPError as e:
                ultimo = f'{m}: {e.code} {e.read().decode(errors="replace")[:300]}'; print('  IA:', ultimo)
                if e.code in (429, 500, 503):
                    time.sleep(30 * (tentativa + 1)); continue
                break  # modelo inexistente/sem acesso: tenta o próximo
            except Exception as e:
                ultimo = f'{m}: {e}'; print('  IA:', ultimo); time.sleep(5)
    raise RuntimeError(f'IA gratuita falhou: {ultimo}')


def json_de(texto):
    """Extrai o primeiro objeto JSON de uma resposta (tolerante a ```json ... ```)."""
    t = texto.split('\n\nFONTES:\n')[0].strip()
    if '```' in t:
        t = t.split('```')[1]
        if t.startswith('json'): t = t[4:]
    i, j = t.find('{'), t.rfind('}')
    return json.loads(t[i:j + 1])
