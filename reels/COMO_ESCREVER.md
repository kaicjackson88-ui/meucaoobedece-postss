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

## Histórias animadas (tiktok/banco/hNNN-*.json)

Postadas no TikTok (rascunhos) e no Instagram nos horários de `historia_horarios` (14h e 20h).
`formato: "tiktok-historia"`. Estrutura: gancho → 5–7 cenas `historia`/`chat` → `virada` → 1–2 cenas de solução → `cta_quiz`. 70–90 s.

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

Regras: 1–2 falas por cena, frases curtas e faladas; dor real (vizinho, condomínio, visita, aluguel, bebê, passeio) → vergonha → quase desistir → virada "ninguém ensinou" → 15 min/dia → reação de outra pessoa. Sem prometer prazo de resultado; legenda termina com "(História ilustrativa…)" + chamada pro teste do link do perfil. Sem emoji dentro de textos que aparecem no vídeo.
