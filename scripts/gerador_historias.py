"""Gerador de histórias RESERVA (válvula de emergência).

Funciona sem o roteirista (sem Claude): monta histórias novas combinando peças prontas por dor —
gancho, problema, consequência (chat/vizinho/visita), virada, "Você sabia?", solução e final —
com tutor, nome do cão e variações sorteadas. O robô chama sozinho quando o banco de histórias acaba.

python scripts/gerador_historias.py 9      # cria 9 histórias reserva em tiktok/banco/
"""
import json, random, sys
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent
BANCO = RAIZ / 'tiktok' / 'banco'
REG = RAIZ / 'dados' / 'reserva_combinacoes.json'

TUTORES = {'ana': ('Ana', 'f'), 'carla': ('Carla', 'f'), 'bia': ('Bia', 'f'), 'joao': ('João', 'm'), 'pedro': ('Pedro', 'm')}
CAES = ['Thor', 'Bolt', 'Paçoca', 'Fred', 'Bob', 'Zeca', 'Toddy', 'Biscoito', 'Max', 'Rex', 'Nescau', 'Billy', 'Duke', 'Tobias', 'Pingo', 'Bidu']
TAG = ' (História ilustrativa, inspirada no que muitos tutores vivem.) Faz o teste do link do perfil e descobre o que o SEU cão precisa 🐾'
FIM_FALA = ' Segue o perfil pra não perder a próxima história. E faz o teste grátis no link do perfil.'


def H(**k):
    return dict(tipo='historia', **k)


# Nos textos: {T}=nome do tutor, {C}=nome do cão, {ela}=ela|ele. Em "quem"/"foco", 'T' = o tutor sorteado.
DORES = {
 'campainha': {
  'tema': 'latido', 'hashtags': '#cachorro #adestramento #historiadecachorro #cachorrolatindo #campainha',
  'quiz': ('Quando a campainha toca, ele…', ['Late sem parar', 'Corre pra porta', 'Fica no cantinho'], 'CÃO ALARME'),
  'ganchos': [
   ('Bastava a campainha tocar e o {C} virava outro cachorro.', ['BASTAVA A', 'CAMPAINHA', 'TOCAR…'], 1, 'sino', '{C} vira outro cachorro quando a campainha toca 🔔'),
   ('{T} já tinha vergonha de pedir comida em casa. Por causa do latido do {C}.', ['VERGONHA DE', 'PEDIR COMIDA', 'EM CASA'], 1, 'sino', '{T} tinha vergonha até de pedir delivery por causa do {C} 😩'),
   ('O entregador nem queria mais subir. Tudo por causa do {C}.', ['O ENTREGADOR', 'NÃO QUERIA', 'MAIS SUBIR'], 1, 'porta', 'Até o entregador já tinha medo do {C} 😬')],
  'problema': [
   H(cenario='sala', quando='SEXTA, 20H', campainha=0.0, fala='Sexta à noite. A campainha tocou.', elenco=[{'quem': 'T', 'x': 300, 'humor': 'preocupado', 'pose': 'maos_cabeca'}], cao={'mascote': 'bravo', 'x': 770, 'acao': 'late'},
     dialogo=[{'quem': 'cao', 'texto': 'AU! AU! AU! AU!', 'em': 0.2}, {'quem': 'T', 'texto': '{C}, chega! É só o entregador!', 'grito': True, 'humor': 'bravo', 'pose': 'aponta'}]),
   H(cenario='sala', quando='TODO DIA', campainha=0.0, fala='Todo dia era a mesma coisa. Tocou, latiu. E não parava mais.', elenco=[{'quem': 'T', 'x': 300, 'humor': 'cansado', 'pose': 'maos_cintura'}], cao={'mascote': 'bravo', 'x': 770, 'acao': 'late'},
     dialogo=[{'quem': 'cao', 'texto': 'AU! AU! AU!', 'em': 0.3}, {'quem': 'T', 'texto': 'Quieto, {C}… por favor…', 'humor': 'triste'}])],
  'consequencia': [
   {'tipo': 'chat', 'quando': '20:14', 'grupo': 'Condomínio Bloco C', 'membros': '52 participantes', 'fala': 'Em dois minutos, o grupo do prédio já sabia.',
    'dialogo': [{'quem': 'sindica', 'texto': 'Quem tem cachorro no terceiro andar? Que latido é esse?'}, {'quem': 'vizinho', 'texto': 'Todo dia isso. Tem gente que trabalha cedo!'}]},
   H(cenario='corredor', quando='NO DIA SEGUINTE', porta_aberta=True, porta_num='304', porta_num2='303', fala='No dia seguinte, o vizinho bateu na porta.', elenco=[{'quem': 'T', 'x': 280, 'humor': 'vergonha', 'pose': 'maos_rosto'}, {'quem': 'vizinho', 'x': 800, 'humor': 'bravo', 'pose': 'bilhete', 'dir': -1}], cao=False,
     dialogo=[{'quem': 'vizinho', 'texto': 'Olha, de novo esse latido, não dá. Vou falar com o síndico.'}, {'quem': 'T', 'texto': 'Desculpa… eu vou dar um jeito.'}], camera={'foco': 'vizinho', 'z': 1.45, 'em': 0.3})],
  'curiosidade': [{'tipo': 'curiosidade', 'tag': 'VOCÊ SABIA?', 'fala': 'Você sabia? O cão ouve sons até quatro vezes mais longe que a gente. Pra ele, a campainha é um alarme de perigo.', 'numero': 4, 'numero_palavra': 'quatro', 'prefixo': '', 'sufixo': 'x', 'rotulo': ['MAIS LONGE', 'que um ser humano'], 'icone': 'sino'}],
  'virada': ('O {C} não latia pra irritar. Pra ele, campainha era perigo. E dava pra ensinar que campainha significa outra coisa.', ['CAMPAINHA NÃO É'], 'PERIGO', 'VAI PRO CANTINHO', 'ensinar'),
  'solucao': [H(cenario='sala', quando='DIA 1 · 15 MIN', campainha=0.3, fala='Quinze minutos por dia. Toca a campainha, {ela} manda pro cantinho, petisco. De novo. E de novo.', elenco=[{'quem': 'T', 'x': 300, 'humor': 'normal', 'pose': 'petisco'}], cao={'mascote': 'normal', 'x': 760, 'acao': 'senta'},
     dialogo=[{'quem': 'T', 'texto': 'Cantinho… isso! Muito bem!', 'humor': 'feliz'}])],
  'final': [H(cenario='corredor', quando='SEMANAS DEPOIS', porta_aberta=True, porta_num='304', porta_num2='303', fala='Semanas depois, o vizinho apareceu de novo. Mas por outro motivo.', elenco=[{'quem': 'T', 'x': 280, 'humor': 'radiante', 'pose': 'guia'}, {'quem': 'vizinho', 'x': 800, 'humor': 'surpreso', 'pose': 'parado', 'dir': -1}], cao={'mascote': 'normal', 'x': 540, 'acao': 'senta'},
     dialogo=[{'quem': 'vizinho', 'texto': 'Tocaram aí agora e… nenhum latido?'}, {'quem': 'T', 'texto': 'A gente treinou junto. Ele aprendeu.'}])]},
 'xixi': {
  'tema': 'xixi', 'hashtags': '#cachorro #adestramento #historiadecachorro #xixinolugarcerto #filhote',
  'quiz': ('Seu cão faz xixi…', ['Em qualquer lugar', 'Só quando fica sozinho', 'No lugar certo'], 'CÃO SEM ROTINA'),
  'ganchos': [
   ('{T} já tinha gastado mais com desinfetante do que com ração.', ['MAIS COM', 'DESINFETANTE', 'QUE RAÇÃO'], 1, 'casa', '{T} já gastava mais com desinfetante do que com ração 🧽'),
   ('Toda manhã, {T} acordava e pisava no xixi do {C}.', ['TODA MANHÃ', 'O MESMO', 'XIXI'], 2, 'casa', 'Toda manhã {T} pisava no xixi do {C} 😩'),
   ('A visita sentou no sofá… e sentiu o cheiro.', ['A VISITA', 'SENTIU', 'O CHEIRO'], 1, 'sofa', 'A visita sentou no sofá da casa d{a} {T} e sentiu o cheiro 😳')],
  'problema': [
   H(cenario='sala', quando='SEGUNDA, 7H', fala='Sete da manhã. Mais uma vez, no tapete.', elenco=[{'quem': 'T', 'x': 300, 'humor': 'surpreso', 'pose': 'maos_cabeca'}], cao={'mascote': 'feliz', 'x': 780, 'acao': 'feliz'}, objetos=[{'nome': 'poca', 'x': 480, 'y': 1440, 'em': 0.0}],
     dialogo=[{'quem': 'T', 'texto': 'De novo no tapete, {C}?!', 'grito': True, 'humor': 'bravo'}]),
   H(cenario='cozinha', quando='DEPOIS DO TRABALHO', fala='Chegava do trabalho e já sabia: tinha xixi escondido em algum canto.', elenco=[{'quem': 'T', 'x': 320, 'humor': 'cansado', 'pose': 'maos_cintura'}], cao={'mascote': 'normal', 'x': 800, 'acao': 'senta'}, objetos=[{'nome': 'poca', 'x': 820, 'y': 1450, 'palavra': 'escondido'}],
     dialogo=[{'quem': 'T', 'texto': 'Atrás da geladeira agora?', 'pensa': True}])],
  'consequencia': [
   H(cenario='sala', quando='NO ALMOÇO', fala='No almoço de domingo, a sogra comentou o que ninguém queria ouvir.', elenco=[{'quem': 'T', 'x': 280, 'humor': 'vergonha', 'pose': 'maos_rosto'}, {'quem': 'sindica', 'x': 820, 'humor': 'bravo', 'pose': 'bracos_cruzados', 'dir': -1}], cao={'mascote': 'feliz', 'x': 560},
     dialogo=[{'quem': 'sindica', 'texto': 'Essa casa tá com um cheirinho, hein?'}, {'quem': 'T', 'texto': 'É que… eu limpei hoje cedo.'}]),
   H(cenario='sala', quando='CORRIDA', fala='Pano, desinfetante, vela cheirosa. E a bronca de sempre.', elenco=[{'quem': 'T', 'x': 300, 'humor': 'bravo', 'pose': 'aponta'}], cao={'mascote': 'dorminhoco', 'x': 760}, objetos=[{'nome': 'poca', 'x': 560, 'y': 1440}],
     dialogo=[{'quem': 'T', 'texto': 'Feio! Aqui não pode!'}])],
  'curiosidade': [{'tipo': 'curiosidade', 'tag': 'VOCÊ SABIA?', 'fala': 'Você sabia? O olfato do cão é dez mil vezes mais sensível que o nosso, ou mais. Mesmo limpo, ele ainda sente o cheiro e volta no mesmo lugar.', 'numero': 10, 'numero_palavra': 'dez', 'sufixo': ' mil x', 'prefixo': '', 'rotulo': ['MAIS SENSÍVEL', 'que o nosso olfato'], 'icone': 'focinho'}],
  'virada': ('O {C} não fazia por pirraça. Ninguém tinha mostrado pra ele onde era o lugar. A bronca só ensinava a se esconder.', ['NÃO ERA'], 'PIRRAÇA', 'NINGUÉM MOSTROU', 'mostrado'),
  'solucao': [H(cenario='sala', quando='DIA 1 · 15 MIN', fala='Horário certo, tapete no mesmo lugar e festa quando ele acerta. Quinze minutos por dia.', elenco=[{'quem': 'T', 'x': 300, 'humor': 'radiante', 'pose': 'comemora'}], cao={'mascote': 'feliz', 'x': 760, 'acao': 'feliz'},
     dialogo=[{'quem': 'T', 'texto': 'Isso, {C}! No lugar certo!'}])],
  'final': [H(cenario='sala', quando='HOJE', fala='Hoje, a visita chega e só sente cheiro de café.', elenco=[{'quem': 'T', 'x': 280, 'humor': 'feliz', 'pose': 'carinho'}, {'quem': 'sindica', 'x': 820, 'humor': 'surpreso', 'pose': 'parado', 'dir': -1}], cao={'mascote': 'feliz', 'x': 560, 'acao': 'feliz'},
     dialogo=[{'quem': 'sindica', 'texto': 'Nem parece que tem cachorro aqui!'}, {'quem': 'T', 'texto': 'Ele aprendeu o lugar dele.', 'humor': 'radiante'}])]},
 'visita': {
  'tema': 'pulo', 'hashtags': '#cachorro #adestramento #historiadecachorro #cachorropulando #visita',
  'quiz': ('Quando chega visita, seu cão…', ['Pula em todo mundo', 'Late sem parar', 'Fica tranquilo'], 'CÃO CANGURU'),
  'ganchos': [
   ('A amiga d{a} {T} veio de roupa nova. O {C} não perdoou.', ['ROUPA NOVA', 'E O CÃO', 'NÃO PERDOOU'], 1, 'porta', 'A visita veio de roupa nova e o {C} não perdoou 😬'),
   ('{T} parou de convidar gente pra casa. O motivo tinha quatro patas.', ['PAROU DE', 'RECEBER', 'VISITA'], 1, 'porta', '{T} parou de receber visita por causa do {C} 🙈'),
   ('A visita mal entrou e já estava encurralada no sofá. Obra do {C}.', ['ENCURRALADA', 'NO', 'SOFÁ'], 0, 'sofa', 'A visita mal entrou e o {C} já tinha encurralado ela no sofá 😅')],
  'problema': [
   H(cenario='corredor', quando='SÁBADO, 15H', porta_aberta=True, porta_num='201', porta_num2='202', fala='Era só abrir a porta.', elenco=[{'quem': 'bia', 'x': 800, 'humor': 'surpreso', 'pose': 'maos_rosto', 'dir': -1}], cao={'mascote': 'feliz', 'x': 560, 'acao': 'pula'},
     dialogo=[{'quem': 'bia', 'texto': 'Ai! Calma, calma, desce!', 'grito': True}], camera={'foco': 'bia', 'z': 1.4, 'em': 0.2}),
   H(cenario='sala', quando='A VISITA TODA', fala='A visita inteira foi assim. Ele pulava, a visita desviava, e {T} pedia desculpa.', elenco=[{'quem': 'T', 'x': 260, 'humor': 'vergonha', 'pose': 'maos_rosto'}, {'quem': 'sindica', 'x': 820, 'humor': 'bravo', 'pose': 'bracos_cruzados', 'dir': -1}], cao={'mascote': 'feliz', 'x': 540, 'acao': 'pula'},
     dialogo=[{'quem': 'sindica', 'texto': 'Esse cachorro não tem educação, não?'}, {'quem': 'T', 'texto': 'Ele só tá animado… desculpa.'}])],
  'consequencia': [
   H(cenario='noite', relogio='23:10', quando='À NOITE', fala='À noite, veio o desabafo.', elenco=[{'quem': 'T', 'x': 300, 'humor': 'triste', 'pose': 'parado'}, {'quem': 'joao', 'x': 780, 'humor': 'preocupado', 'pose': 'bracos_cruzados', 'dir': -1}], cao={'mascote': 'dorminhoco', 'x': 560, 'acao': 'dorme'},
     dialogo=[{'quem': 'T', 'texto': 'Eu tenho vergonha de receber qualquer pessoa aqui.'}, {'quem': 'joao', 'texto': 'E se a gente deixar ele preso quando vier alguém?'}])],
  'curiosidade': [{'tipo': 'curiosidade', 'tag': 'VOCÊ SABIA?', 'fala': 'Você sabia? Entre cães, o cumprimento é focinho com focinho. Quando ele pula, está tentando alcançar o seu rosto pra dizer oi.', 'numero': None, 'rotulo': ['FOCINHO COM FOCINHO', 'é o oi dos cães'], 'icone': 'focinho'}],
  'virada': ('O {C} não pulava por falta de educação. Era o único jeito que ele conhecia de dizer oi. Ninguém tinha ensinado outro.', ['ELE NÃO PULAVA POR'], 'MALCRIAÇÃO', 'NINGUÉM ENSINOU', 'único'),
  'solucao': [H(cenario='sala', quando='DIA 1 · 15 MIN', fala='Pulou? Vira de costas. Sentou? Ganha atenção e petisco. Quinze minutos por dia.', elenco=[{'quem': 'T', 'x': 300, 'humor': 'normal', 'pose': 'petisco'}], cao={'mascote': 'normal', 'x': 740, 'acao': 'senta'},
     dialogo=[{'quem': 'T', 'texto': 'Senta… isso! Agora sim, oi!'}])],
  'final': [H(cenario='corredor', quando='UM MÊS DEPOIS', porta_aberta=True, porta_num='201', porta_num2='202', fala='Um mês depois, a visita voltou.', elenco=[{'quem': 'T', 'x': 280, 'humor': 'feliz', 'pose': 'parado'}, {'quem': 'sindica', 'x': 800, 'humor': 'surpreso', 'pose': 'parado', 'dir': -1}], cao={'mascote': 'normal', 'x': 540, 'acao': 'senta'},
     dialogo=[{'quem': 'sindica', 'texto': 'Ué… ele sentou pra me esperar?'}, {'quem': 'T', 'texto': 'A gente treinou junto!', 'humor': 'radiante'}])]},
 'guia': {
  'tema': 'guia', 'hashtags': '#cachorro #adestramento #historiadecachorro #passeio #cachorropuxandoguia',
  'quiz': ('No passeio, seu cão…', ['Me arrasta', 'Late pra outros cães', 'Anda do meu lado'], 'CÃO TRATOR'),
  'ganchos': [
   ('{T} tinha vergonha de passear com o próprio cachorro.', ['VERGONHA', 'DE PASSEAR', 'COM ELE'], 0, 'guia', '{T} tinha vergonha de passear com o {C} 😅'),
   ('O {C} arrastou {T} pela calçada. Na frente de todo mundo.', ['ARRASTOU', 'NA FRENTE DE', 'TODO MUNDO'], 0, 'guia', 'O {C} arrastou {T} na frente de todo mundo 😳'),
   ('Era pra ser só uma volta no quarteirão.', ['SÓ UMA', 'VOLTA NO', 'QUARTEIRÃO'], 1, 'guia', 'Era pra ser só uma volta no quarteirão com o {C}… 🙃')],
  'problema': [
   H(cenario='rua', quando='SÁBADO, 9H', fala='Sábado de manhã. Era só sair do prédio.', elenco=[{'quem': 'T', 'x': 300, 'humor': 'preocupado', 'pose': 'guia', 'anda': True, 'inclina': 0.1}], cao={'mascote': 'bravo', 'x': 820, 'acao': 'late'},
     dialogo=[{'quem': 'cao', 'texto': 'AU! AU! AU!', 'em': 0.3}, {'quem': 'T', 'texto': '{C}, devagar! Você vai me derrubar!', 'grito': True}])],
  'consequencia': [
   H(cenario='rua', quando='NA ESQUINA', fala='Na esquina, apareceu outro cachorro. E aí não teve guia que segurasse.', elenco=[{'quem': 'T', 'x': 280, 'humor': 'surpreso', 'pose': 'guia', 'inclina': 0.14}, {'quem': 'joao', 'x': 860, 'humor': 'bravo', 'pose': 'aponta', 'dir': -1}], cao={'mascote': 'bravo', 'x': 600, 'acao': 'pula'},
     dialogo=[{'quem': 'joao', 'texto': 'Ei, segura esse cachorro!'}, {'quem': 'T', 'texto': 'Desculpa! Ele não é bravo, juro!', 'humor': 'vergonha'}], camera={'foco': 'T', 'z': 1.4, 'em': 0.5}),
   H(cenario='sala', quando='DE VOLTA', fala='Voltou pra casa com o braço doendo. E tomou a decisão errada.', elenco=[{'quem': 'T', 'x': 320, 'humor': 'triste', 'pose': 'maos_rosto'}], cao={'mascote': 'normal', 'x': 760},
     dialogo=[{'quem': 'T', 'texto': 'Pronto. A gente não passeia mais.', 'humor': 'bravo'}])],
  'curiosidade': [{'tipo': 'curiosidade', 'tag': 'VOCÊ SABIA?', 'fala': 'Você sabia? Quando a guia estica, o cão tende a fazer força pro lado contrário. É um reflexo. Quanto mais você puxa, mais ele puxa.', 'numero': None, 'rotulo': ['GUIA ESTICADA', 'faz ele puxar mais'], 'icone': 'guia'}],
  'virada': ('O {C} não puxava por teimosia. Ninguém tinha ensinado que é a guia frouxa que leva pra frente.', ['ELE NÃO PUXAVA POR'], 'TEIMOSIA', 'GUIA FROUXA', 'frouxa'),
  'solucao': [H(cenario='rua', quando='DIA 1 · 15 MIN', fala='Puxou? Para. Afrouxou? Anda. Quinze minutos por dia, sem pressa.', elenco=[{'quem': 'T', 'x': 320, 'humor': 'normal', 'pose': 'guia'}], cao={'mascote': 'normal', 'x': 700, 'acao': 'senta'},
     dialogo=[{'quem': 'T', 'texto': 'Isso, {C}. Junto comigo.'}])],
  'final': [H(cenario='rua', quando='HOJE', fala='Hoje o passeio é a melhor parte do dia. Dos dois.', elenco=[{'quem': 'T', 'x': 330, 'humor': 'radiante', 'pose': 'guia', 'anda': True}, {'quem': 'joao', 'x': 870, 'humor': 'feliz', 'pose': 'acena', 'dir': -1}], cao={'mascote': 'feliz', 'x': 640, 'acao': 'feliz'},
     dialogo=[{'quem': 'joao', 'texto': 'Nossa, é o mesmo cachorro?'}, {'quem': 'T', 'texto': 'O mesmo. Só que agora ele sabe passear!'}])]},
 'sozinho': {
  'tema': 'ansiedade', 'hashtags': '#cachorro #adestramento #historiadecachorro #ansiedadedeseparacao #cachorrodestruidor',
  'quiz': ('Quando você sai de casa, ele…', ['Chora e destrói', 'Late na porta', 'Dorme tranquilo'], 'CÃO GRUDE'),
  'ganchos': [
   ('Todo dia, {T} abria a porta com medo do que ia encontrar.', ['MEDO DE', 'ABRIR A', 'PORTA'], 1, 'porta', 'Todo dia {T} tinha medo de abrir a porta de casa 😰'),
   ('O {C} chorava a tarde inteira. O prédio inteiro ouvia.', ['O PRÉDIO', 'INTEIRO', 'OUVIA'], 1, 'casa', 'O {C} chorava a tarde inteira… e o prédio todo ouvia 😢'),
   ('Primeiro foi o chinelo. Depois a almofada. Depois o sofá.', ['PRIMEIRO O', 'CHINELO', 'DEPOIS O SOFÁ'], 2, 'sofa', 'Primeiro o chinelo, depois o sofá… o {C} não parava 😩')],
  'problema': [
   H(cenario='sala', quando='18:40', fala='Seis e quarenta da tarde. A porta abriu.', elenco=[{'quem': 'T', 'x': 300, 'humor': 'surpreso', 'pose': 'maos_cabeca'}], cao={'mascote': 'feliz', 'x': 760, 'acao': 'feliz'}, objetos=[{'nome': 'almofada', 'x': 880, 'y': 1300, 'em': 0.3, 'frente': True}, {'nome': 'sapato', 'x': 560, 'y': 1450, 'em': 0.5}],
     dialogo=[{'quem': 'T', 'texto': 'Meu tênis… e o sofá?!', 'grito': True}])],
  'consequencia': [
   {'tipo': 'chat', 'quando': '18:52', 'grupo': 'Moradores Ed. Aurora', 'membros': '36 participantes', 'fala': 'E, como sempre, tinha mensagem no grupo.',
    'dialogo': [{'quem': 'bia', 'texto': 'O cachorro do 103 chorou a tarde INTEIRA de novo.'}, {'quem': 'sindica', 'texto': 'Precisamos conversar sobre isso.'}]},
   H(cenario='noite', relogio='00:30', quando='MEIA-NOITE', fala='Naquela noite, não deu pra dormir.', elenco=[{'quem': 'T', 'x': 330, 'humor': 'cansado', 'pose': 'celular'}], cao={'mascote': 'dorminhoco', 'x': 790, 'acao': 'dorme'},
     dialogo=[{'quem': 'T', 'texto': 'Eu não posso largar o emprego pra ficar com ele…', 'pensa': True}], camera={'foco': 'T', 'z': 1.5, 'em': 0.4})],
  'curiosidade': [{'tipo': 'curiosidade', 'tag': 'VOCÊ SABIA?', 'fala': 'Você sabia? Cães evoluíram vivendo em grupo. Ficar sozinho é uma coisa que eles precisam aprender, não vem pronta.', 'numero': None, 'rotulo': ['FICAR SOZINHO', 'se aprende'], 'icone': 'casa'}],
  'virada': ('O {C} não era destruidor. Pra ele, cada saída era um abandono. Ninguém tinha ensinado ele a ficar sozinho.', ['ELE NÃO ERA'], 'DESTRUIDOR', 'SÓ TINHA MEDO', 'abandono'),
  'solucao': [H(cenario='sala', quando='DIA 1 · 15 MIN', fala='Saídas curtinhas. Um minuto, depois cinco, depois dez. Sem festa na volta, sem drama na saída.', elenco=[{'quem': 'T', 'x': 300, 'humor': 'normal', 'pose': 'acena'}], cao={'mascote': 'normal', 'x': 750, 'acao': 'senta'},
     dialogo=[{'quem': 'T', 'texto': 'Já volto, {C}. Fica.'}])],
  'final': [H(cenario='sala', quando='SEMANAS DEPOIS', fala='Semanas depois, a porta abriu e a casa estava assim.', elenco=[{'quem': 'T', 'x': 300, 'humor': 'radiante', 'pose': 'comemora'}], cao={'mascote': 'dorminhoco', 'x': 760, 'acao': 'dorme'},
     dialogo=[{'quem': 'T', 'texto': 'Tudo no lugar… e você dormindo?!'}])]},
 'chamado': {
  'tema': 'chamado', 'hashtags': '#cachorro #adestramento #historiadecachorro #cachorrofugiu #obediencia',
  'quiz': ('Quando você chama, ele…', ['Finge que não ouve', 'Sai correndo', 'Vem na hora'], 'CÃO SURDO SELETIVO'),
  'ganchos': [
   ('O portão ficou aberto dois segundos. Foi o suficiente.', ['DOIS', 'SEGUNDOS', 'DE PORTÃO'], 1, 'porta', 'O portão ficou aberto 2 segundos e o {C} sumiu 😱'),
   ('{T} gritava o nome do {C}. Ele olhava… e corria pro outro lado.', ['ELE OLHAVA', 'E CORRIA', 'PRO OUTRO LADO'], 1, 'megafone', 'O {C} olhava… e corria pro outro lado 🏃'),
   ('Vinte minutos correndo atrás do próprio cachorro na praça.', ['20 MINUTOS', 'CORRENDO', 'ATRÁS DELE'], 0, 'relogio', '20 minutos correndo atrás do {C} na praça 😮‍💨')],
  'problema': [
   H(cenario='rua', quando='DOMINGO, 10H', fala='Domingo, na praça. Era só soltar um pouquinho.', elenco=[{'quem': 'T', 'x': 300, 'humor': 'preocupado', 'pose': 'aponta'}], cao={'mascote': 'feliz', 'x': 760, 'acao': 'corre'},
     dialogo=[{'quem': 'T', 'texto': '{C}! Vem! {C}, VEM AQUI!', 'grito': True}])],
  'consequencia': [
   H(cenario='rua', quando='NA RUA', fala='Ele atravessou a rua. Um carro freou em cima.', elenco=[{'quem': 'T', 'x': 280, 'humor': 'surpreso', 'pose': 'maos_cabeca'}, {'quem': 'pedro', 'x': 860, 'humor': 'bravo', 'pose': 'aponta', 'dir': -1}], cao={'mascote': 'feliz', 'x': 620, 'acao': 'corre'},
     dialogo=[{'quem': 'pedro', 'texto': 'Ô! Quase que eu pego ele!'}, {'quem': 'T', 'texto': 'Desculpa! Ele não me obedece!', 'humor': 'vergonha'}], camera={'foco': 'T', 'z': 1.45, 'em': 0.4}),
   H(cenario='noite', relogio='22:15', quando='À NOITE', fala='Em casa, o susto virou culpa.', elenco=[{'quem': 'T', 'x': 330, 'humor': 'triste', 'pose': 'maos_rosto'}], cao={'mascote': 'dorminhoco', 'x': 790, 'acao': 'dorme'},
     dialogo=[{'quem': 'T', 'texto': 'E se tivesse acontecido alguma coisa?', 'pensa': True}])],
  'curiosidade': [{'tipo': 'curiosidade', 'tag': 'VOCÊ SABIA?', 'fala': 'Você sabia? Se o nome do cão aparece junto com bronca, ele aprende que ser chamado é ruim. E aí, claro, não vem.', 'numero': None, 'rotulo': ['NOME COM BRONCA', 'ensina a fugir'], 'icone': 'megafone'}],
  'virada': ('O {C} não era desobediente. Toda vez que vinha, levava bronca. Ninguém tinha ensinado que vir é a melhor coisa do mundo.', ['ELE NÃO ERA'], 'DESOBEDIENTE', 'VIR É BOM', 'ensinado'),
  'solucao': [H(cenario='sala', quando='DIA 1 · 15 MIN', fala='Dentro de casa primeiro. Chamou, veio, festa e petisco. Nunca mais nome com bronca.', elenco=[{'quem': 'T', 'x': 300, 'humor': 'feliz', 'pose': 'petisco'}], cao={'mascote': 'normal', 'x': 740, 'acao': 'feliz'},
     dialogo=[{'quem': 'T', 'texto': '{C}, vem! Isso! Muito bem!'}])],
  'final': [H(cenario='rua', quando='SEMANAS DEPOIS', fala='Semanas depois, na mesma praça.', elenco=[{'quem': 'T', 'x': 320, 'humor': 'radiante', 'pose': 'comemora'}, {'quem': 'pedro', 'x': 860, 'humor': 'surpreso', 'pose': 'parado', 'dir': -1}], cao={'mascote': 'feliz', 'x': 600, 'acao': 'feliz'},
     dialogo=[{'quem': 'pedro', 'texto': 'Ele voltou só de você chamar?'}, {'quem': 'T', 'texto': 'Agora ele sabe que vale a pena!'}])]},
 'mesa': {
  'tema': 'comida', 'hashtags': '#cachorro #adestramento #historiadecachorro #cachorropidao #cachorroladrao',
  'quiz': ('Na hora da comida, seu cão…', ['Rouba da mesa', 'Fica pedindo', 'Espera tranquilo'], 'CÃO LADRÃO'),
  'ganchos': [
   ('O frango do almoço de domingo sumiu. Em três segundos.', ['O FRANGO', 'SUMIU EM', '3 SEGUNDOS'], 1, 'osso', 'O frango do almoço sumiu em 3 segundos… culpa do {C} 🍗'),
   ('Ninguém conseguia comer em paz naquela casa.', ['NINGUÉM', 'COMIA', 'EM PAZ'], 1, 'osso', 'Ninguém comia em paz na casa d{a} {T} 😅'),
   ('O bolo de aniversário… o {C} provou primeiro.', ['O BOLO DE', 'ANIVERSÁRIO', 'JÁ ERA'], 1, 'coracao', 'O {C} provou o bolo de aniversário antes de todo mundo 🎂')],
  'problema': [
   H(cenario='cozinha', quando='DOMINGO, 12H', fala='Domingo, meio-dia. Bastou virar as costas.', elenco=[{'quem': 'T', 'x': 300, 'humor': 'surpreso', 'pose': 'maos_cabeca'}], cao={'mascote': 'feliz', 'x': 780, 'acao': 'feliz'}, objetos=[{'nome': 'petisco', 'x': 820, 'y': 1300, 'em': 0.3, 'frente': True}],
     dialogo=[{'quem': 'T', 'texto': '{C}! Isso era o almoço!', 'grito': True}])],
  'consequencia': [
   H(cenario='sala', quando='NA VISITA', fala='Com visita em casa, foi pior. Ele pedia, chorava, pulava no colo de todo mundo.', elenco=[{'quem': 'T', 'x': 280, 'humor': 'vergonha', 'pose': 'maos_rosto'}, {'quem': 'vizinho', 'x': 820, 'humor': 'bravo', 'pose': 'bracos_cruzados', 'dir': -1}], cao={'mascote': 'feliz', 'x': 560, 'acao': 'pula'},
     dialogo=[{'quem': 'vizinho', 'texto': 'Ele sempre fica assim na hora de comer?'}, {'quem': 'T', 'texto': 'Sempre… desculpa.'}])],
  'curiosidade': [{'tipo': 'curiosidade', 'tag': 'VOCÊ SABIA?', 'fala': 'Você sabia? Se de vez em quando ele ganha um pedaço da mesa, ele aprende a insistir. Ganhar às vezes vicia mais que ganhar sempre.', 'numero': None, 'rotulo': ['GANHAR ÀS VEZES', 'vicia mais'], 'icone': 'cerebro'}],
  'virada': ('O {C} não era mal-educado. Ele aprendeu que insistir funciona. E ninguém tinha ensinado o que fazer na hora da comida.', ['ELE NÃO ERA'], 'MAL-EDUCADO', 'APRENDEU ERRADO', 'insistir'),
  'solucao': [H(cenario='cozinha', quando='DIA 1 · 15 MIN', fala='Hora da comida virou hora do cantinho. Ficou deitado? Ganha o petisco dele, não o do prato.', elenco=[{'quem': 'T', 'x': 300, 'humor': 'normal', 'pose': 'petisco'}], cao={'mascote': 'normal', 'x': 760, 'acao': 'senta'},
     dialogo=[{'quem': 'T', 'texto': 'Cantinho, {C}. Isso!'}])],
  'final': [H(cenario='sala', quando='HOJE', fala='Hoje o almoço de domingo é só almoço.', elenco=[{'quem': 'T', 'x': 280, 'humor': 'radiante', 'pose': 'parado'}, {'quem': 'vizinho', 'x': 820, 'humor': 'surpreso', 'pose': 'parado', 'dir': -1}], cao={'mascote': 'dorminhoco', 'x': 560, 'acao': 'dorme'},
     dialogo=[{'quem': 'vizinho', 'texto': 'Ele nem se mexeu com o churrasco!'}, {'quem': 'T', 'texto': 'Ele sabe o lugar dele agora.'}])]},
}


TAGS_EXTRA = {
 'campainha': ['#cachorrolatindo', '#latido', '#campainha', '#vizinhos', '#condominio', '#apartamento', '#caoansioso', '#pet'],
 'xixi': ['#xixinolugarcerto', '#xixi', '#filhote', '#tapetehigienico', '#cachorrofilhote', '#apartamento', '#limpeza', '#pet'],
 'visita': ['#cachorropulando', '#visita', '#cachorroagitado', '#cachorrofeliz', '#sogra', '#familia', '#caoeducado', '#pet'],
 'guia': ['#passeio', '#cachorropuxandoguia', '#guia', '#passeiocomcachorro', '#caminhada', '#rua', '#caoeducado', '#pet'],
 'sozinho': ['#ansiedadedeseparacao', '#cachorrodestruidor', '#cachorrosozinho', '#cachorrochorando', '#trabalho', '#apartamento', '#caoansioso', '#pet'],
 'chamado': ['#cachorrofugiu', '#obediencia', '#comandos', '#praca', '#cachorroteimoso', '#caoeducado', '#adestramentopositivo', '#pet'],
 'mesa': ['#cachorropidao', '#cachorroladrao', '#comida', '#almoco', '#churrasco', '#cachorrocomilao', '#caoeducado', '#pet'],
}
BASE_TAGS = ['#cachorro', '#adestramento', '#historiadecachorro']


def _pesos():
    try:
        return json.loads((RAIZ / 'dados' / 'tiktok_pesos.json').read_text(encoding='utf-8'))
    except Exception:
        return {}


def _escolher(rnd, opcoes, pesos_de, explorar=.25):
    """Usa mais o que deu certo (pesos aprendidos) e reserva uma parte para testar o novo."""
    import math
    if rnd.random() < explorar or not pesos_de:
        return rnd.choice(opcoes)
    ws = [math.exp(3 * pesos_de.get(str(o), 0)) for o in opcoes]
    return rnd.choices(opcoes, weights=ws, k=1)[0]


def _fmt(o, sub):
    if isinstance(o, str):
        for k, v in sub.items(): o = o.replace('{' + k + '}', v)
        return o
    if isinstance(o, list): return [_fmt(x, sub) for x in o]
    if isinstance(o, dict):
        return {k: (sub['_quem'] if k in ('quem', 'foco') and v == 'T' else _fmt(v, sub)) for k, v in o.items()}
    return o


def montar(dor, seed):
    rnd = random.Random(seed)
    D = DORES[dor]
    tid = rnd.choice([t for t in TUTORES if not (dor in ('visita', 'sozinho') and t == 'bia') and not (dor in ('guia', 'visita') and t == 'joao') and not (dor == 'chamado' and t == 'pedro')])
    nome, g = TUTORES[tid]
    cao = rnd.choice(CAES)
    sub = {'T': nome, 'C': cao, '_quem': tid, 'ela': 'ela' if g == 'f' else 'ele', 'a': 'a' if g == 'f' else 'o'}
    P = _pesos()
    gi = _escolher(rnd, list(range(len(D['ganchos']))), {k.split('-')[-1]: v for k, v in P.get('gancho', {}).items() if k.startswith(dor + '-')})
    gf, gl, gd, gic, gleg = D['ganchos'][gi]
    cenas = [{'tipo': 'gancho', 'fala': gf, 'linhas': gl, 'destaque': gd, 'parte': 1, 'mascote': 'bravo', 'icone': gic}]
    cenas.append(rnd.choice(D['problema']))
    cons = D['consequencia'][:]; rnd.shuffle(cons)
    cenas += cons
    vf, vt, vde, vpara, vpal = D['virada']
    cenas.append({'tipo': 'virada', 'fala': vf, 'topo': vt, 'de': vde, 'para': vpara, 'para_palavra': vpal})
    pc = P.get('curiosidade', {}); quer_cur = (pc.get('sim', 0) >= pc.get('nao', 0)) if pc and rnd.random() > .25 else rnd.random() < .85
    if quer_cur:
        cenas.append(rnd.choice(D['curiosidade']))
    cenas.append(rnd.choice(D['solucao']))
    cenas.append(rnd.choice(D['final']))
    pt = P.get('hashtag', {}); pool = TAGS_EXTRA.get(dor, [])[:]
    extras = []
    for _ in range(3):
        extras.append(_escolher(rnd, [x for x in pool if x not in extras], pt))
    tags = BASE_TAGS + extras
    perg, ops, res = D['quiz']
    cenas.append({'tipo': 'cta_quiz', 'fala': 'E o seu cão?' + FIM_FALA, 'pergunta': perg, 'opcoes': ops, 'escolha': 0, 'resultado': res, 'seguir': True})
    cenas = _fmt(json.loads(json.dumps(cenas)), sub)
    return {'formato': 'tiktok-historia', 'gancho_tipo': 'historia', 'tema': D['tema'], 'estilo': 'sol', 'reserva': True,
            'legenda': _fmt(gleg, sub) + TAG, 'hashtags': ' '.join(tags), 'cenas': cenas, '_assin': f'{dor}-{gi}-{tid}-{cao}',
            'componentes': {'dor': dor, 'gancho': f'{dor}-{gi}', 'curiosidade': quer_cur, 'tutor': tid, 'tags': tags}}


def gerar(n):
    reg = json.loads(REG.read_text(encoding='utf-8')) if REG.exists() else []
    feitos = set(reg)
    nums = [int(p.stem[2:6]) for p in BANCO.glob('hr*.json') if p.stem[2:6].isdigit()]
    prox = max(nums, default=0) + 1
    criados, tent, dores = [], 0, list(DORES)
    while len(criados) < n and tent < n * 40:
        tent += 1
        rnd = random.Random(prox * 7919 + tent)
        dor = _escolher(rnd, dores, _pesos().get('dor', {}), explorar=.3)
        r = montar(dor, seed=prox * 1000 + tent)
        if r['_assin'] in feitos: continue
        feitos.add(r['_assin']); reg.append(r.pop('_assin'))
        r = {'id': f'hr{prox:04d}-{dor}', **r}
        (BANCO / f"{r['id']}.json").write_text(json.dumps(r, ensure_ascii=False, indent=1), encoding='utf-8')
        criados.append(r['id']); prox += 1
    REG.parent.mkdir(exist_ok=True); REG.write_text(json.dumps(reg, ensure_ascii=False), encoding='utf-8')
    print('Reserva criada:', ', '.join(criados))
    return criados


if __name__ == '__main__':
    gerar(int(sys.argv[1]) if len(sys.argv) > 1 else 9)
