"""IA gratuita do GitHub (GitHub Models) — o "cérebro reserva" que roda sem o Claude.

Usa o GITHUB_TOKEN do próprio workflow (permissão `models: read`). Tem limite diário gratuito,
então o código faz poucas chamadas e tenta outro modelo se um estiver no limite.
"""
import json, os, time, urllib.error, urllib.parse, urllib.request


class _SemRedirect(urllib.request.HTTPRedirectHandler):
    def redirect_request(self, *a, **k):
        return None  # não segue: o GitHub Models redireciona e o urllib trocaria POST por GET


_abrir = urllib.request.build_opener(_SemRedirect).open


def _post(url, corpo, headers, timeout=180):
    for _ in range(4):  # segue redirecionamentos mantendo o POST (igual curl -L -X POST)
        req = urllib.request.Request(url, data=corpo, method='POST', headers=headers)
        try:
            with _abrir(req, timeout=timeout) as r:
                return r.status, r.headers.get('Content-Type'), r.read().decode(errors='replace')
        except urllib.error.HTTPError as e:
            if e.code in (301, 302, 303, 307, 308) and e.headers.get('Location'):
                url = urllib.parse.urljoin(url, e.headers['Location']); continue
            raise
    raise RuntimeError('redirecionamentos demais')

# dois endereços do GitHub Models (o novo e o antigo); usa o que responder
ROTAS = [('https://models.github.ai/inference/chat/completions', ['openai/gpt-4.1-mini', 'openai/gpt-4o-mini']),
         ('https://models.inference.ai.azure.com/chat/completions', ['gpt-4o-mini', 'gpt-4o'])]


def disponivel():
    return bool(os.environ.get('GITHUB_TOKEN'))


def perguntar(sistema, usuario, max_tokens=3500, temperatura=0.8, json_saida=False):
    tok = os.environ.get('GITHUB_TOKEN', '')
    if not tok:
        raise RuntimeError('sem GITHUB_TOKEN (IA gratuita indisponível)')
    ultimo = None
    for URL, modelos in ROTAS:
      for modelo in modelos:
        corpo = {'model': modelo, 'temperature': temperatura, 'max_tokens': max_tokens,
                 'messages': [{'role': 'system', 'content': sistema}, {'role': 'user', 'content': usuario}]}
        if json_saida and 'gpt' in modelo:
            corpo['response_format'] = {'type': 'json_object'}
        for tentativa in range(2):
            try:
                st, ct, bruto = _post(URL, json.dumps(corpo).encode(), {'Authorization': f'Bearer {tok}', 'Content-Type': 'application/json',
                                                                      'Accept': 'application/vnd.github+json', 'X-GitHub-Api-Version': '2022-11-28'})
                try:
                    d = json.loads(bruto)
                except ValueError:
                    raise RuntimeError(f'resposta não-JSON (HTTP {st}, {ct}): {bruto[:200]!r}')
                return d['choices'][0]['message']['content']
            except urllib.error.HTTPError as e:
                ultimo = f'{modelo}: {e.code} {e.read().decode(errors="replace")[:300]}'; print('  IA:', ultimo)
                if e.code == 429:  # limite: espera um pouco e/ou passa pro próximo modelo
                    time.sleep(20 if tentativa == 0 else 0); continue
                break
            except Exception as e:
                ultimo = f'{modelo}: {e}'; print('  IA:', ultimo); time.sleep(5)
    raise RuntimeError(f'IA gratuita falhou: {ultimo}')


def json_de(texto):
    """Extrai o primeiro objeto JSON de uma resposta (tolerante a ```json ... ```)."""
    t = texto.strip()
    if '```' in t:
        t = t.split('```')[1]
        if t.startswith('json'): t = t[4:]
    i, j = t.find('{'), t.rfind('}')
    return json.loads(t[i:j + 1])
