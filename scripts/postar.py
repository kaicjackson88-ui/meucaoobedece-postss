"""Publica no Instagram o próximo carrossel da fila que já chegou na hora.

Cada post fica em posts/<pasta>/ com:
  post.json      -> {"quando": "2026-10-08T12:00:00-03:00", "legenda": "...", "tema": "..."}
  slide-1.jpg ... slide-N.jpg  (2 a 10 imagens, JPEG)
Depois de publicado, o robô cria posts/<pasta>/publicado.json e não posta de novo.

Precisa da variável de ambiente IG_TOKEN (segredo do GitHub).
"""
import json
import os
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
from datetime import datetime, timezone
from pathlib import Path

API = "https://graph.facebook.com/v26.0"
RAIZ = Path(__file__).resolve().parent.parent
POSTS = RAIZ / "posts"
REPO = os.environ.get("GITHUB_REPOSITORY", "kaicjackson88-ui/meucaoobedece-postss")
BRANCH = os.environ.get("GITHUB_REF_NAME", "main")
TOKEN = os.environ.get("IG_TOKEN", "").strip()


def chamar(metodo, caminho, params):
    params = dict(params)
    params["access_token"] = TOKEN
    dados = urllib.parse.urlencode(params).encode()
    url = f"{API}/{caminho}"
    if metodo == "GET":
        req = urllib.request.Request(f"{url}?{dados.decode()}")
    else:
        req = urllib.request.Request(url, data=dados, method="POST")
    try:
        with urllib.request.urlopen(req, timeout=60) as r:
            return json.loads(r.read().decode())
    except urllib.error.HTTPError as e:
        corpo = e.read().decode(errors="replace")
        try:
            erro = json.loads(corpo).get("error", {})
        except ValueError:
            erro = {"message": corpo[:300]}
        raise RuntimeError(f"Erro da Meta em {caminho}: {erro.get('message')} (código {erro.get('code')})") from None


def conta_instagram():
    r = chamar("GET", "me/accounts", {"fields": "name,instagram_business_account{id,username}"})
    for pagina in r.get("data", []):
        ig = pagina.get("instagram_business_account")
        if ig:
            print(f"Conta: @{ig.get('username')} (página {pagina.get('name')})")
            return ig["id"]
    raise RuntimeError("Nenhuma página do Facebook com Instagram ligado foi encontrada para essa chave.")


def proximo_post(forcar=None):
    agora = datetime.now(timezone.utc)
    fila = []
    for pasta in sorted(POSTS.iterdir()):
        if not pasta.is_dir() or (pasta / "publicado.json").exists():
            continue
        info = json.loads((pasta / "post.json").read_text(encoding="utf-8"))
        quando = datetime.fromisoformat(info["quando"])
        if forcar and pasta.name == forcar:
            return pasta, info
        if not forcar and quando <= agora:
            fila.append((quando, pasta, info))
    if forcar:
        raise RuntimeError(f"Post '{forcar}' não encontrado ou já publicado.")
    if not fila:
        return None, None
    fila.sort(key=lambda x: x[0])
    _, pasta, info = fila[0]
    return pasta, info


def esperar_pronto(container_id):
    for _ in range(30):
        r = chamar("GET", container_id, {"fields": "status_code"})
        status = r.get("status_code")
        if status == "FINISHED":
            return
        if status in ("ERROR", "EXPIRED"):
            raise RuntimeError(f"A Meta recusou a mídia {container_id}: {status}")
        time.sleep(4)
    raise RuntimeError(f"A mídia {container_id} demorou demais para ficar pronta.")


def publicar(ig_id, pasta, info):
    slides = sorted(pasta.glob("slide-*.jpg"), key=lambda p: int(p.stem.split("-")[1]))
    if not 2 <= len(slides) <= 10:
        raise RuntimeError(f"{pasta.name}: um carrossel precisa de 2 a 10 imagens (tem {len(slides)}).")
    filhos = []
    for s in slides:
        url = f"https://raw.githubusercontent.com/{REPO}/{BRANCH}/posts/{pasta.name}/{s.name}"
        r = chamar("POST", f"{ig_id}/media", {"image_url": url, "is_carousel_item": "true"})
        filhos.append(r["id"])
        print(f"  imagem enviada: {s.name}")
    for f in filhos:
        esperar_pronto(f)
    r = chamar("POST", f"{ig_id}/media", {
        "media_type": "CAROUSEL",
        "children": ",".join(filhos),
        "caption": info["legenda"],
    })
    carrossel = r["id"]
    esperar_pronto(carrossel)
    r = chamar("POST", f"{ig_id}/media_publish", {"creation_id": carrossel})
    media_id = r["id"]
    link = chamar("GET", media_id, {"fields": "permalink"}).get("permalink", "")
    (pasta / "publicado.json").write_text(json.dumps({
        "media_id": media_id,
        "link": link,
        "publicado_em": datetime.now(timezone.utc).isoformat(),
    }, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"Publicado! {link}")


def main():
    if not TOKEN:
        sys.exit("Falta o segredo IG_TOKEN no GitHub (Settings > Secrets and variables > Actions).")
    forcar = (os.environ.get("POST_FORCADO") or "").strip() or None
    pasta, info = proximo_post(forcar)
    if not pasta:
        print("Nenhum post na hora agora. Nada a fazer.")
        return
    print(f"Publicando {pasta.name} ({info.get('tema', '')})")
    ig_id = conta_instagram()
    publicar(ig_id, pasta, info)


if __name__ == "__main__":
    try:
        main()
    except RuntimeError as e:
        sys.exit(str(e))
