# Robô de postagem — Meu Cão Obedece

Posta sozinho no Instagram **@meu_cao_obedece** os carrosséis da pasta `posts/`, no dia e hora marcados.

## Como funciona

- De hora em hora o GitHub roda o robô (`.github/workflows/postar.yml`).
- Ele procura em `posts/` o post mais antigo que já chegou na hora e ainda não foi publicado.
- Publica o carrossel com a legenda e cria `publicado.json` na pasta do post, com o link.
- Usa a chave guardada no segredo `IG_TOKEN` (Settings › Secrets and variables › Actions).

## Cada post é uma pasta

```
posts/2026-10-08-1200-xixi/
  post.json      ← "quando" (data e hora), "legenda", "tema"
  slide-1.jpg … slide-5.jpg   (JPEG, 1080×1350)
```

## Comandos úteis (pelo celular)

- **Postar agora:** aba **Actions** › *Postar no Instagram* › **Run workflow**. Deixe o campo vazio para postar o próximo da fila, ou escreva o nome da pasta.
- **Pausar o robô:** aba **Actions** › *Postar no Instagram* › **⋯** › **Disable workflow**. Para voltar, **Enable workflow**.
- **Tirar um post da fila:** apague a pasta dele em `posts/`.
- **Ver se deu certo:** aba **Actions** mostra cada execução com ✔ ou ✖. Se der ✖, o GitHub manda e-mail.

## Chave da Meta

A chave dura 60 dias (a atual vence perto de 6/12/2026). Antes disso, gere outra no
Graph API Explorer, estique no Depurador de Token e troque o valor do segredo `IG_TOKEN`.
