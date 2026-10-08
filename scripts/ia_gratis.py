"""IA gratuita do GitHub (GitHub Models) — o "cérebro reserva" que roda sem o Claude.

Usa o GITHUB_TOKEN do próprio workflow (permissão `models: read`). Tem limite diário gratuito,
então o código faz poucas chamadas e tenta outro modelo se um estiver no limite.
"""
import json, os, time, urllib.error, urllib.request

URL = 'https://models.github.ai/inference/chat/completions'
MODELOS = ['openai/gpt-4.1-mini', 'openai/gpt-4o-mini', 'meta/Llama-4-Scout-17B-16E-Instruct']


def disponivel():
    return bool(os.environ.get('GITHUB_TOKEN'))


def perguntar(sistema, usuario, max_tokens=3500, temperatura=0.8, json_saida=False):
    tok = os.environ.get('GITHUB_TOKEN', '')
    if not tok:
        raise RuntimeError('sem GITHUB_TOKEN (IA gratuita indisponível)')
    ultimo = None
    for modelo in MODELOS:
        corpo = {'model': modelo, 'temperature': temperatura, 'max_tokens': max_tokens,
                 'messages': [{'role': 'system', 'content': sistema}, {'role': 'user', 'content': usuario}]}
        if json_saida and modelo.startswith('openai/'):
            corpo['response_format'] = {'type': 'json_object'}
        for tentativa in range(2):
            req = urllib.request.Request(URL, data=json.dumps(corpo).encode(), method='POST',
                                         headers={'Authorization': f'Bearer {tok}', 'Content-Type': 'application/json',
                                                  'Accept': 'application/vnd.github+json'})
            try:
                with urllib.request.urlopen(req, timeout=180) as r:
                    d = json.loads(r.read().decode())
                return d['choices'][0]['message']['content']
            except urllib.error.HTTPError as e:
                ultimo = f'{modelo}: {e.code} {e.read().decode(errors="replace")[:200]}'
                if e.code == 429:  # limite: espera um pouco e/ou passa pro próximo modelo
                    time.sleep(20 if tentativa == 0 else 0); continue
                break
            except Exception as e:
                ultimo = f'{modelo}: {e}'; time.sleep(5)
    raise RuntimeError(f'IA gratuita falhou: {ultimo}')


def json_de(texto):
    """Extrai o primeiro objeto JSON de uma resposta (tolerante a ```json ... ```)."""
    t = texto.strip()
    if '```' in t:
        t = t.split('```')[1]
        if t.startswith('json'): t = t[4:]
    i, j = t.find('{'), t.rfind('}')
    return json.loads(t[i:j + 1])
