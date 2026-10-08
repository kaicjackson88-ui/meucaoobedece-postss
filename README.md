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

## Reels automáticos (3 por dia)

- O robô `.github/workflows/reels.yml` confere de hora em hora. Nos horários de `reels/config.json` (11h, 17h e 20h) ele escolhe um roteiro de `reels/banco/`, gera a voz, monta o vídeo e posta.
- **Testar um vídeo sem postar:** Actions › *Reels automáticos* › Run workflow (modo `teste`). O vídeo fica no branch `midia`.
- **Postar um roteiro agora:** mesmo lugar, escreva o ID do roteiro e o modo `postar`.
- **Pausar só os Reels:** Actions › *Reels automáticos* › ⋯ › Disable workflow.
- **Aprendizado:** todo dia às 23:40 o *Aprender com as métricas* lê alcance, compartilhamentos, salvamentos e tempo assistido e atualiza `dados/pesos.json` e `dados/relatorio.md`. O robô passa a escolher mais os formatos e ganchos que performam.
- **XIXI:** a cada execução o robô responde quem comentou XIXI (direct quando a Meta liberar; enquanto isso, resposta no comentário).
- **Escrever roteiros novos:** veja `reels/COMO_ESCREVER.md`.
- **Conferir a chave:** Actions › *Diagnóstico da chave* › Run workflow → resultado em `dados/diagnostico.txt`.
