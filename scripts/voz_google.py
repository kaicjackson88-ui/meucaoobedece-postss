"""Voz natural do Google (Gemini TTS) — usa o segredo GEMINI_API_KEY (o mesmo da IA gratuita).
falar(texto, mp3, voz_edge, rate, pitch) -> lista de palavras com início/fim (s), no formato do reels._narrar_edge.
O Gemini não devolve o tempo de cada palavra: estimamos pelas pausas reais do áudio (silêncios) e pelo tamanho das palavras."""
import base64, json, os, re, subprocess, tempfile, time, urllib.error, urllib.request

API = 'https://generativelanguage.googleapis.com/v1beta/models'
PREFERIDOS = [m.strip() for m in os.environ.get('GEMINI_TTS_MODELOS', 'gemini-2.5-flash-preview-tts,gemini-2.5-pro-preview-tts').split(',') if m.strip()]
_ESTADO = {'modelos': None, 'fora_ate': 0.0}

# voz da Microsoft (como está nos roteiros) -> voz do Gemini. Tom: pitch alto/baixo escolhe outra voz do mesmo tipo.
FEM = {'base': 'Kore', 'aguda': 'Leda', 'grave': 'Aoede'}
MASC = {'base': 'Charon', 'aguda': 'Puck', 'grave': 'Algenib'}
ESTILO = ('Leia em português do Brasil, com sotaque brasileiro natural, como uma pessoa real conversando com um amigo '
          'sobre o cachorro dele: tom caloroso, próximo e animado, sem soar como locutor nem robô. '
          'Respeite a pontuação com pausas curtas. Texto: ')


def disponivel():
    return bool(os.environ.get('GEMINI_API_KEY', '').strip()) and time.time() > _ESTADO['fora_ate']


def voz_gemini(voz_edge, pitch='+0Hz'):
    if os.environ.get('GEMINI_VOZ'):
        return os.environ['GEMINI_VOZ']
    fem = any(n in (voz_edge or '') for n in ('Francisca', 'Thalita', 'Leila', 'Manuela', 'Brenda', 'Giovanna'))
    try:
        p = int(re.sub(r'[^\d\-+]', '', str(pitch)) or 0)
    except ValueError:
        p = 0
    t = FEM if fem else MASC
    return t['aguda'] if p >= 6 else t['grave'] if p <= -6 else t['base']


def _modelos(chave):
    if _ESTADO['modelos'] is None:
        achados = []
        try:
            with urllib.request.urlopen(f'{API}?key={chave}&pageSize=200', timeout=30) as r:
                achados = [m['name'].split('/')[-1] for m in json.loads(r.read().decode()).get('models', []) if 'tts' in m['name']]
        except Exception as e:  # noqa: BLE001
            print('  voz Google: não listei os modelos:', str(e)[:80])
        achados.sort(key=lambda n: ('flash' in n, n), reverse=True)
        _ESTADO['modelos'] = list(dict.fromkeys([m for m in PREFERIDOS if not achados or m in achados] + achados))[:4] or PREFERIDOS
        print('  voz Google: modelos', _ESTADO['modelos'], flush=True)
    return _ESTADO['modelos']


def _pedir(texto, voz):
    chave = os.environ['GEMINI_API_KEY'].strip()
    corpo = {'contents': [{'parts': [{'text': ESTILO + texto}]}],
             'generationConfig': {'responseModalities': ['AUDIO'],
                                  'speechConfig': {'voiceConfig': {'prebuiltVoiceConfig': {'voiceName': voz}}}}}
    ultimo = None
    for m in _modelos(chave):
        for tentativa in range(2):
            req = urllib.request.Request(f'{API}/{m}:generateContent?key={chave}', data=json.dumps(corpo).encode(), method='POST',
                                         headers={'Content-Type': 'application/json'})
            try:
                with urllib.request.urlopen(req, timeout=180) as r:
                    d = json.loads(r.read().decode())
                for p in d['candidates'][0]['content']['parts']:
                    if 'inlineData' in p:
                        mime = p['inlineData'].get('mimeType', '')
                        taxa = int((re.search(r'rate=(\d+)', mime) or [0, 24000])[1])
                        return base64.b64decode(p['inlineData']['data']), taxa
                ultimo = f'{m}: resposta sem áudio'
            except urllib.error.HTTPError as e:
                ultimo = f'{m}: {e.code} {e.read().decode(errors="replace")[:200]}'
                if e.code == 429:  # cota do plano grátis: espera um pouco; se persistir, deixa o Google de lado por 30 min
                    if tentativa == 0:
                        time.sleep(25); continue
                    _ESTADO['fora_ate'] = time.time() + 1800
                    raise RuntimeError('voz Google sem cota agora: ' + ultimo)
                if e.code in (500, 503) and tentativa == 0:
                    time.sleep(8); continue
            except Exception as e:  # noqa: BLE001
                ultimo = f'{m}: {e}'
            break
    raise RuntimeError('voz Google falhou: ' + str(ultimo))


def _tempos(x, palavras):
    """Distribui as palavras no tempo de fala real (pula os silêncios), proporcional ao tamanho de cada palavra.
    x: áudio mono float a 24 kHz."""
    import numpy as np
    jan = 480  # 20 ms a 24 kHz
    n = len(x) // jan
    en = np.sqrt((x[:n * jan].reshape(n, jan) ** 2).mean(1)) if n else np.zeros(1)
    lim = max(0.01, float(np.percentile(en, 95)) * 0.06)
    fala = en > lim
    i = 0  # fecha buracos curtos (< 0,12 s) para não picotar dentro das palavras
    while i < len(fala):
        if fala[i]:
            i += 1; continue
        j = i
        while j < len(fala) and not fala[j]:
            j += 1
        if i > 0 and j < len(fala) and (j - i) * 0.02 < 0.12:
            fala[i:j] = True
        i = j
    idx = np.where(fala)[0]
    if not len(idx):
        idx = np.arange(max(n, 1))
    pesos = [len(w) + 1.5 for w in palavras]
    tot = sum(pesos); acc = 0.0; out = []
    for w, p in zip(palavras, pesos):
        a = int(acc / tot * (len(idx) - 1)); acc += p
        b = int(acc / tot * (len(idx) - 1))
        ini, fim = idx[a] * 0.02, idx[max(a, b)] * 0.02 + 0.02
        out.append({'palavra': w, 'inicio': round(float(ini), 3), 'fim': round(float(max(fim, ini + 0.08)), 3)})
    return out


def falar(texto, mp3, voz_edge='pt-BR-FranciscaNeural', rate='+0%', pitch='+0Hz'):
    import numpy as np
    from scipy.io import wavfile
    pcm, taxa = _pedir(texto, voz_gemini(voz_edge, pitch))
    try:
        vel = 1 + int(str(rate).replace('%', '').replace('+', '') or 0) / 100
    except ValueError:
        vel = 1.0
    vel = min(max(vel, 0.8), 1.25)
    tmp = tempfile.mkdtemp(prefix='vozg-')
    raw = os.path.join(tmp, 'v.pcm'); wav = os.path.join(tmp, 'v.wav')
    open(raw, 'wb').write(pcm)
    # corta silêncio do começo/fim, ajusta velocidade e normaliza o volume
    filtro = ('silenceremove=start_periods=1:start_threshold=-45dB:start_silence=0.05,areverse,'
              'silenceremove=start_periods=1:start_threshold=-45dB:start_silence=0.08,areverse,'
              f'atempo={vel:.3f},loudnorm=I=-16:TP=-1.5:LRA=11')
    subprocess.run(['ffmpeg', '-y', '-v', 'error', '-f', 's16le', '-ar', str(taxa), '-ac', '1', '-i', raw, '-af', filtro,
                    '-ar', '24000', '-ac', '1', wav], check=True)
    subprocess.run(['ffmpeg', '-y', '-v', 'error', '-i', wav, '-c:a', 'libmp3lame', '-b:a', '160k', mp3], check=True)
    sr, x = wavfile.read(wav)
    x = x.astype(np.float32) / 32768
    palavras = re.findall(r'[\w]+', texto, flags=re.UNICODE) or [texto]
    return _tempos(x, palavras)
