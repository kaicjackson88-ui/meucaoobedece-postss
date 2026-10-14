"""Baixa em HD os vídeos escolhidos e deixa cifrados em escolhidos/ para subir num branch.
Aceita, separados por vírgula ou espaço (variável ESCOLHIDOS):
- número da prancha do último garimpo (1 a 3 dígitos), lido do candidatos.json passado como argumento;
- link ou ID do Pixabay (usa o segredo PIXABAY_API_KEY);
- link do Mixkit (só se a licença for a gratuita).
O repositório é público e a licença dos bancos não deixa distribuir o vídeo cru, então cada arquivo sobe cifrado:
AES-256 com uma chave aleatória, e essa chave cifrada com scripts/chave_publica.pem. Só quem tem a chave privada abre:
  openssl pkeyutl -decrypt -inkey privada.pem -pkeyopt rsa_padding_mode:oaep -in X.mp4.chave -out k.txt
  openssl enc -d -aes-256-cbc -pbkdf2 -pass file:k.txt -in X.mp4.enc -out X.mp4
Se a chave privada se perder: gerar outro par e trocar scripts/chave_publica.pem.
Uso: ESCOLHIDOS="3, 8, https://pixabay.com/videos/xxx-123456/" python scripts/baixar_escolhidos.py candidatos.json"""
import json, os, re, subprocess, sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import garimpo_videos as gv  # noqa: E402
import garimpo_pixabay as gp  # noqa: E402

RAIZ = Path(__file__).resolve().parents[1]
OUT = RAIZ / 'escolhidos'
PUB = RAIZ / 'scripts' / 'chave_publica.pem'
LIMITE = 95_000_000  # o GitHub recusa arquivo acima de 100 MB


def pixabay(vid, base=None):
    """Consulta o vídeo pelo ID (links frescos, HD 1080 com 720 de reserva)."""
    hits = gp.api(id=vid) if gp.CHAVE else []
    if not hits:
        return None
    h = hits[0]
    d = dict(base or {}, id=str(h['id']), pagina=h.get('pageURL', ''), autor=h.get('user', ''), licenca='Pixabay (uso comercial ok)')
    d.setdefault('cat', 'link')
    d['urls'] = [u for u in dict.fromkeys((gp.arquivo(h, 1080, LIMITE), gp.arquivo(h, 720, LIMITE))) if u]
    return d


def mixkit(vid, pagina, base=None):
    lic = gv.licenca(pagina) if pagina else 'conferir'
    if lic.startswith('Restrita'):
        print('  Mixkit', vid, 'tem licença restrita: não pode ir em anúncio, pulei'); return None
    d = dict(base or {}, id=str(vid), pagina=pagina, licenca=lic)
    d.setdefault('cat', 'link')
    d['urls'] = [f'https://assets.mixkit.co/videos/{vid}/{vid}-{q}.mp4' for q in (1080, 720)]
    return d


def resolver(token, por_n):
    """Transforma um item do pedido num dicionário com as URLs a tentar (a melhor primeiro)."""
    t = token.strip().split('?')[0].rstrip('/')
    if re.fullmatch(r'\d{1,3}', t):
        c = por_n.get(int(t))
        if not c:
            print('  número', t, 'não está no último garimpo'); return None
        pag = c.get('pagina') or ''
        if 'pixabay.com' in pag:
            return pixabay(c['id'], c) or dict(c, urls=[c['hd']] if c.get('hd') else [])
        if 'mixkit.co' in pag:
            return mixkit(c['id'], pag, c)
        return dict(c, urls=[c['hd']] if c.get('hd') else [])
    if 'pixabay.com' in t or re.fullmatch(r'\d{4,}', t):
        m = re.search(r'(\d+)$', t)
        return pixabay(m.group(1)) if m else None
    if 'mixkit.co' in t:
        m = re.search(r'-(\d+)$', t)
        return mixkit(m.group(1), t + '/') if m else None
    print('  não entendi', token, '(link do Pexels não dá sem chave; manda do Pixabay)')
    return None


def encolher(arq):
    """Se passar do limite do GitHub, recodifica em até 1920 px no lado maior."""
    if arq.stat().st_size <= LIMITE:
        return True
    menor = arq.with_name(arq.stem + '_menor.mp4')
    subprocess.run(['ffmpeg', '-y', '-v', 'error', '-i', str(arq), '-vf',
                    "scale='min(1920,iw)':'min(1920,ih)':force_original_aspect_ratio=decrease:force_divisible_by=2",
                    '-c:v', 'libx264', '-crf', '21', '-preset', 'fast', '-pix_fmt', 'yuv420p', '-c:a', 'aac', str(menor)], check=False)
    if menor.exists() and 0 < menor.stat().st_size <= LIMITE:
        menor.replace(arq); return True
    print('  grande demais mesmo recodificado:', arq.name)
    return False


def cifrar(arq, destino):
    """AES-256 com chave aleatória; a chave vai cifrada com a chave pública (RSA-OAEP). Apaga o arquivo cru."""
    k = gv.TMP / 'k.txt'
    try:
        subprocess.run(['openssl', 'rand', '-hex', '-out', str(k), '32'], check=True)
        subprocess.run(['openssl', 'enc', '-aes-256-cbc', '-pbkdf2', '-salt', '-pass', f'file:{k}', '-in', str(arq), '-out', f'{destino}.enc'], check=True)
        subprocess.run(['openssl', 'pkeyutl', '-encrypt', '-pubin', '-inkey', str(PUB), '-pkeyopt', 'rsa_padding_mode:oaep',
                        '-in', str(k), '-out', f'{destino}.chave'], check=True)
    finally:
        k.unlink(missing_ok=True); arq.unlink(missing_ok=True)


def main():
    OUT.mkdir(exist_ok=True)
    if not PUB.exists():
        sys.exit('Falta scripts/chave_publica.pem.')
    cands = []
    if len(sys.argv) > 1 and Path(sys.argv[1]).exists():
        try:
            cands = json.loads(Path(sys.argv[1]).read_text(encoding='utf-8'))
        except ValueError:
            cands = []
    por_n = {int(c['n']): c for c in cands if c.get('n')}
    pedido = [p for p in re.split(r'[\s,;]+', os.environ.get('ESCOLHIDOS', '')) if p]
    if not pedido:
        sys.exit('Nada pedido em ESCOLHIDOS.')
    feitos = []
    for token in pedido:
        d = resolver(token, por_n)
        if not d:
            continue
        cat = re.sub(r'[^a-z0-9]+', '-', (d.get('cat') or 'link').lower()).strip('-')
        nome = (f"{int(d['n']):02d}_" if d.get('n') and re.fullmatch(r'\d{1,3}', token.strip()) else '') + f"{cat}_{d['id']}.mp4"
        arq = gv.TMP / nome
        for u in d.get('urls', []):
            dados = gv.get(u)
            if len(dados) > 20000:
                arq.write_bytes(dados); break
        else:
            print('  não consegui baixar', token); continue
        if not encolher(arq):
            arq.unlink(missing_ok=True); continue
        info = gv.medir(arq)
        feitos.append({k: d.get(k) for k in ('n', 'id', 'cat', 'titulo', 'pagina', 'autor', 'licenca')} | info | {'arquivo': nome})
        cifrar(arq, OUT / nome)
        print('  ok', nome, info)
    (OUT / 'lista.json').write_text(json.dumps(feitos, ensure_ascii=False, indent=1), encoding='utf-8')
    print('baixados:', len(feitos), 'de', len(pedido))
    if not feitos:
        sys.exit(1)


if __name__ == '__main__':
    main()
