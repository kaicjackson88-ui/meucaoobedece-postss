"""Gera as vozes de um anúncio com o Gemini TTS: uma voz e um estilo por fala.
python scripts/vozes_anuncio.py <pasta>   (lê <pasta>/falas.json, grava <pasta>/voz/<id>.mp3 e <pasta>/voz/palavras.json)
falas.json: [{"id": "n1", "texto": "...", "voz": "Charon", "estilo": "..."}]. Usa o segredo GEMINI_API_KEY."""
import json, os, sys, time
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent))
import voz_google  # noqa: E402

pasta = Path(sys.argv[1])
falas = json.loads((pasta / 'falas.json').read_text(encoding='utf-8'))
out = pasta / 'voz'; out.mkdir(exist_ok=True)
arq = out / 'palavras.json'
tempos = json.loads(arq.read_text(encoding='utf-8')) if arq.exists() else {}
padrao = voz_google.ESTILO
for i, f in enumerate(falas):
    mp3 = out / f"{f['id']}.mp3"
    if mp3.exists() and f['id'] in tempos:
        print('já existe', f['id']); continue
    voz_google.ESTILO = (f.get('estilo') + ' Texto: ') if f.get('estilo') else padrao
    os.environ['GEMINI_VOZ'] = f['voz']
    for t in range(3):
        try:
            tempos[f['id']] = voz_google.falar(f['texto'], str(mp3), rate=f.get('vel', '+0%'))
            print('ok', f['id'], f['voz']); break
        except RuntimeError as e:
            print('tentativa', t + 1, f['id'], str(e)[:120]); voz_google._ESTADO['fora_ate'] = 0; time.sleep(40)
    arq.write_text(json.dumps(tempos, ensure_ascii=False, indent=1), encoding='utf-8')
    time.sleep(6)
faltam = [f['id'] for f in falas if f['id'] not in tempos]
print('faltam:', faltam or 'nenhuma')
sys.exit(1 if faltam else 0)
