# Como escrever um roteiro de Reels

Cada arquivo em `reels/banco/` é um Reels. O robô escolhe um roteiro ainda não usado (dando preferência aos formatos e ganchos com melhor `dados/pesos.json`), gera a voz, monta o vídeo e posta.

## Campos do roteiro

```json
{
 "id": "r031-lista-tema-curto",          // único, igual ao nome do arquivo
 "formato": "lista|curiosidades|objecao|mito|erro",
 "gancho_tipo": "objecao|pergunta-dor|numero|curiosidade|negacao|segredo|pergunta|erro",
 "tema": "latido|xixi|coleira|roer|pulo|ansiedade|chamado|mordida|fogos|obediencia|curiosidade",
 "legenda": "texto do post (termina com o CTA do XIXI)",
 "hashtags": "#adestramento #cachorro #meucaoobedece #dicasdecachorro #tema",
 "cenas": [ ... ]
}
```

## Tipos de cena

Toda cena tem `fala` (o que a voz diz). Escreva números **por extenso** na fala ("cinco minutos") e em algarismo nos textos da tela ("5 minutos"). Sem símbolos na fala (nada de R$, %, /).

| tipo | campos |
|---|---|
| `gancho` | `linhas` (2–3 linhas curtas, MAIÚSCULAS), `destaque` (índice da linha em pílula), `icone`, `mascote`, opcional `carimbo` + `carimbo_palavra` |
| `texto` | `linhas`, `destaque`, `icone`, `mascote` |
| `dica` | `n`, `total`, `titulo`, `sub`, `icone` |
| `curiosidade` | `n`, `numero` (ou `null`), `prefixo`, `sufixo`, `rotulo` [linha grande, linha pequena], `icone`, `numero_palavra` |
| `objecao` | `objecao` (frase do tutor), `resposta` (carimbo), `resposta_palavra`, `explica` [2 linhas], `resposta_cor` red/teal, opcional `tag` |
| `mito` | `frase`, `veredito` MITO/VERDADE, `veredito_palavra`, `explica` [2 linhas], `icone`, `tag` |
| `virada` | `topo` [linhas], `de`, `para`, `para_palavra` (palavra da fala em que vira) |
| `cta_meio` | `linhas`, `selos` [3 chips] — sempre antes do final |
| `cta_final` | `palavra`: "XIXI" — fala tipo "Comenta XIXI, que eu te mando o teste." |

Mascotes: `normal`, `bravo`, `dorminhoco`, `feliz`, `lendario`.
Ícones: `sino osso moeda casa relogio coracao lampada bola guia calendario megafone pata alvo cerebro focinho porta escudo x check sofa`.

## Regras

- Gancho que faz a pessoa se reconhecer nos 3 primeiros segundos. Máx. 6–8 palavras por linha de tela.
- 25 a 45 segundos de fala (≈ 70–120 palavras no total).
- Sempre terminar com `cta_meio` + `cta_final`.
- Curiosidade só com fato confirmado em fonte confiável. Nada de promessa de resultado garantido nem diagnóstico de saúde; medo intenso ou agressividade → sugerir veterinário/profissional na legenda.
- Usar 5 hashtags.

## Histórias animadas (tiktok/banco/hNNN-*.json) — ESTILO 2 (desde 09/10)

Postadas no TikTok (1 rascunho a cada 2h, das 6h30 às 22h30) e no Instagram nos horários de `historia_horarios`.
Campos obrigatórios novos: `"versao": 2` e `"formato_historia"` (um dos formatos abaixo). O robô posta primeiro as de versão 2
e nunca dois vídeos seguidos do mesmo formato — por isso, num lote de histórias, use pelo menos 4 formatos diferentes.

**Duração: 30 a 45 segundos** (≈ 70 a 120 palavras faladas no total), **6 a 9 cenas** contando gancho e final.
O caos/conflito aparece JÁ na primeira cena depois do gancho (nada de apresentação lenta).

### Formatos (`formato_historia`)
- `classica` — gancho → 3–4 cenas → virada → 1 cena de solução → cta. A clássica NÃO pode passar de 1/3 do lote.
- `pov_cao` — o próprio cachorro narra em primeira pessoa ("Eu sou o Thor. E hoje eu…"). A `fala` é a voz do cão contando; os humanos falam no `dialogo`. Engraçado e com o ponto de vista dele (o que ele entende errado).
- `grupo` — a história é contada quase só pelo grupo do condomínio/família: gancho → 3–4 cenas `chat` com reações, prints, áudio "transcrito" → 1–2 cenas `historia` → cta. Fofoca, indireta, figurinha em texto.
- `quiz` — gancho é uma pergunta ("O que você faria?"); mostra a situação em 2–3 cenas; uma cena (virada ou curiosidade) mostra "1, 2 ou 3?" e PARA (fala: "Comenta 1, 2 ou 3 antes de ver a resposta"); depois revela a resposta certa. A legenda pede o número nos comentários.
- `serie` — história em 2 partes com os mesmos personagens: campos `"serie": "slug-da-serie"` e `"parte": 1` ou `2`. A Parte 1 termina num gancho forte ("…e aí a síndica abriu a porta.") e o cta diz "Segue pra ver a Parte 2". A Parte 2 começa recapitulando em 1 frase. O robô posta a Parte 2 logo depois da Parte 1.
- `erros` — "3 coisas que você faz e o seu cão entende errado": gancho → 3 cenas curtas (cada uma com o tutor fazendo o erro e o cão reagindo) → 1 cena com o certo → cta.
- `antes_depois` — mesma situação duas vezes: "Mês passado:" (caos) e "Hoje:" (calma), cenas espelhadas, mesmo cenário e horário, com a reação de alguém de fora no final.

### Proibido (vira repetição)
- A frase da virada "X não era Y. Ninguém tinha ensinado/mostrado…" e qualquer variação ("não era teimoso/bagunceiro/desobediente… ninguém ensinou"). Ela foi usada em TODAS as histórias antigas.
- Virar sempre pela mesma pessoa. Varie QUEM revela: um vizinho que já passou por isso, a criança da casa, o veterinário, a síndica, o próprio cão (pov_cao), um comentário no grupo, o tutor sozinho às 2h da manhã.
- Mais de 2 cenas `historia` no MESMO cenário por vídeo (antes, quase metade era "sala"). Use corredor, rua, cozinha, quarto e noite.
- Repetir a mesma `acao` do cão em mais de 2 cenas (antes "senta" aparecia em quase tudo). Varie late, pula, corre, dorme, feliz e cenas sem ação.
- Repetir premissa, nome de cão ou nome de tutor de uma história recente.

### Comentários e legenda
- A última fala ou a legenda faz uma pergunta fácil de responder: "O seu faz isso? Comenta 1 pra sim, 2 pra não" / "Qual você escolheria?".
- Legenda: gancho único + pergunta + "(História ilustrativa, inspirada no que muitos tutores vivem.)" + chamada pro teste do link do perfil.

Cena `historia`:
- `cenario`: sala | noite | quarto | cozinha | corredor | rua ; `relogio` ("02:47"), `quando` (tag curta), `campainha` (0–1 ou palavra)
- `elenco`: [{quem, x, humor, pose, dir(-1 olha pra esquerda), anda, inclina}] — no máximo 2 pessoas (x≈280–330 e 780–830)
  - quem: ana, carla, bia (mulheres) · vizinho (idoso, óculos) · sindica (senhora, óculos — também serve de sogra) · joao, pedro (homens)
  - humor: normal feliz radiante triste bravo surpreso preocupado vergonha cansado
  - pose: parado aponta maos_cabeca bracos_cruzados maos_cintura petisco acena celular comemora maos_rosto carinho guia bilhete explica
- `cao`: {mascote: normal|bravo|feliz|dorminhoco, x, acao: late|pula|corre|senta|dorme|feliz} ou false
- `objetos`: [{nome: poca|almofada|sapato|petisco|coracoes, x, y, em|palavra, frente}]
- `fala`: narração (voz do narrador). `dialogo`: [{quem, texto, humor?, pose?, pensa?, grito?}] — cada personagem tem voz própria; `quem: "cao"` vira balão de latido (sem voz)
- `camera`: {foco: quem|"cao", z: 1.4–1.6, em: 0–1} para zoom no momento forte. `fala_depois: true` põe a narração depois do diálogo.

Cena `chat` (grupo do prédio etc.): `grupo`, `membros`, `quando` ("22:47"), `fala`, `dialogo` [{quem, texto, eu?}].

Regras: 1–2 falas por cena, frases curtas e faladas; dor real (vizinho, condomínio, visita, aluguel, bebê, passeio). A solução cita treino curto e diário quando fizer sentido, sem fórmula fixa. Sem prometer prazo de resultado; legenda termina com "(História ilustrativa…)" + chamada pro teste do link do perfil. Sem emoji dentro de textos que aparecem no vídeo.

Final das histórias (`cta_quiz`): sempre `"seguir": true` e a fala termina com "Segue o perfil pra não perder a próxima história. E faz o teste grátis no link do perfil." (aparece o botão vermelho "+ SEGUE PRA MAIS HISTÓRIAS").
Ritmo de produção: o TikTok usa 9 histórias por dia (renderizadas de madrugada, 1 rascunho a cada 2h). Manter sempre pelo menos 18 histórias não usadas no banco.

História + curiosidade: em cerca de metade das histórias (não em todas, e nem sempre no mesmo lugar), inclua 1 cena `curiosidade` com `"tag": "VOCÊ SABIA?"` explicando o PORQUÊ do comportamento (fato verdadeiro e conhecido; use `numero` só se o número for amplamente aceito, senão `"numero": null`). Campos: fala (começa com "Você sabia?"), numero, numero_palavra, prefixo, sufixo, rotulo [linha grande, linha pequena], icone (sino osso moeda casa relogio coracao lampada bola guia calendario megafone pata alvo cerebro focinho porta escudo).

## Padrões dos perfis de referência (observados em 09/10 — @medicadopet, @adestradorbernardo, @avetday, @comandocanino, @petlinie)
- Gancho em forma de ORDEM ou ALERTA: "Pare de…", "Para de fazer X errado", "3 erros que fazem ele te morder", "ALERTA: …", "… está me envenenando em silêncio". Os maiores (@medicadopet, 4 mi / 2,6 mi / 1,5 mi) usam pergunta prática do dia a dia: "O que meu cachorro pode beber além de água?", "Quais as formas certas de carregar seu cachorro no colo?".
- Objeção do tutor como gancho: "Tutor: sempre dei e nunca morreu" — ótimo para histórias (o tutor fala a frase errada e a história mostra a consequência).
- Séries numeradas ("Parte 3") prendem o seguidor — use "parte" no gancho de histórias em sequência com os mesmos personagens.
- "O que acontece no cérebro do seu cachorro quando…" e "O coração do seu cão se parte em silêncio toda vez que você faz essas 3 coisas" — curiosidade emocional; bom para a cena "VOCÊ SABIA?".
- Texto grande no topo da tela, curto (até ~8 palavras), em caixa de cor forte — nosso gancho já segue isso; manter frases curtas.
