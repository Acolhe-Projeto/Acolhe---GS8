# Acolhe - Applied Computer Vision

## Integrantes

- TomÃ¡z Versolato Carballo - RM 551417
- Rony Ken Nagai - RM 551549
- Aksel Viktor Caminha Rae - RM 99011
- Ian Xavier Kuraoka - RM 98860

## Resumo

O Acolhe Ã© um protÃ³tipo acadÃªmico de acolhimento linguÃ­stico que relaciona objetos cotidianos a palavras em portuguÃªs e espanhol. Este trabalho desenvolveu seu mÃ³dulo de visÃ£o computacional: uma pessoa adulta seleciona uma fotografia e recebe nomes, caixas de localizaÃ§Ã£o e confianÃ§a das detecÃ§Ãµes. A implementaÃ§Ã£o utiliza transferÃªncia de aprendizado com YOLO26m, integrada a uma aplicaÃ§Ã£o web local. O modelo entregue foi adaptado com 91 imagens de treinamento, utilizando 27 imagens para validaÃ§Ã£o e um conjunto anterior de 23 imagens para diagnÃ³stico. Foram concluÃ­das cinco Ã©pocas, com seleÃ§Ã£o do checkpoint pela validaÃ§Ã£o. TambÃ©m foram comparadas continuaÃ§Ãµes de checkpoints nano e uma expansÃ£o para 117 imagens de treino. Essa expansÃ£o acrescentou 11 imagens Ã  validaÃ§Ã£o e reservou 13 imagens novas para teste. O candidato ampliado concluiu sete Ã©pocas, mas nÃ£o superou o modelo anterior na mesma validaÃ§Ã£o, que foi mantido. No teste reservado, contendo 72 objetos, o modelo reconheceu corretamente 52, produziu 21 falsos positivos e deixou de detectar 20. A precisÃ£o foi 71,2% e o recall, 72,2%, atendendo Ã  meta local de 70% nesse conjunto bÃ¡sico. Nas 23 imagens anteriores, mais complexas, os resultados foram 68,3% e 62,1%, respectivamente. A diferenÃ§a entre conjuntos nÃ£o representa evoluÃ§Ã£o direta do modelo. O repositÃ³rio inclui o checkpoint avaliado, trÃªs fotografias pÃºblicas creditadas, cÃ³digo e resultados reproduzÃ­veis. A amostra Ã© pequena, algumas classes apresentam falhas e imagens COCO podem ter participado do prÃ©-treinamento. NÃ£o houve avaliaÃ§Ã£o pedagÃ³gica com crianÃ§as. O mÃ³dulo apoia atividades educativas supervisionadas e nÃ£o interpreta imagens como autorizaÃ§Ã£o para atravessar uma rua.

## IntroduÃ§Ã£o

O mÃ³dulo de visÃ£o do Acolhe apresenta vocabulÃ¡rio em portuguÃªs e espanhol a partir de objetos cotidianos. A pessoa adulta envia uma fotografia e acompanha a atividade. O trabalho reÃºne preparaÃ§Ã£o dos dados, treinamento customizado, comparaÃ§Ã£o de ajustes finos e integraÃ§Ã£o do detector Ã  aplicaÃ§Ã£o. A meta local adotada foi alcanÃ§ar pelo menos 70% de precisÃ£o e recall no perfil utilizado pelo produto.

## Objetivo

Desenvolver e avaliar localmente um detector compacto de objetos cotidianos integrado ao Acolhe, apresentando vocabulÃ¡rio em portuguÃªs e espanhol. Preparar dados rastreÃ¡veis, realizar treinamento customizado e medir desempenho em teste separado, preservando privacidade, explicitando limitaÃ§Ãµes e oferecendo uma demonstraÃ§Ã£o reproduzÃ­vel, supervisionada por adultos, sem interpretar imagens como autorizaÃ§Ã£o para travessia.

## Arquitetura e ferramentas

A interface envia JPEG ou PNG de atÃ© 8 MiB Ã  API Python. O serviÃ§o valida o arquivo, o hash do checkpoint, a ordem das classes e os parÃ¢metros de inferÃªncia. O YOLO retorna caixas e confianÃ§a; a aplicaÃ§Ã£o acrescenta os nomes PT/ES. O upload nÃ£o Ã© salvo.

Foi utilizado Ultralytics 8.4.215 com PyTorch 2.15.0+cpu. O checkpoint YOLO26m customizado possui 21.791.392 parÃ¢metros e ocupa 44.036.761 bytes. Treino e inferÃªncia Vision foram executados em CPU. A inferÃªncia usa resoluÃ§Ã£o 960 e confianÃ§a 0,25; o treino foi feito em 640. As 12 classes sÃ£o mochila, cadeira, livro, garrafa, copo, colher, garfo, tigela, relÃ³gio, guarda-chuva, Ã´nibus e semÃ¡foro.

## Dados e separaÃ§Ã£o dos conjuntos

Foram usadas fotografias pÃºblicas do COCO e uma fotografia de Ã´nibus do Wikimedia Commons, com fontes, autores, licenÃ§as e hashes registrados. As anotaÃ§Ãµes foram convertidas para YOLO e auditadas quanto a caixas, classes, integridade e duplicatas. A composiÃ§Ã£o preservou a separaÃ§Ã£o entre treino e validaÃ§Ã£o; o teste reservado final nÃ£o entrou no ajuste fino.

| Conjunto | Treino | ValidaÃ§Ã£o | Teste | Objetos em treino / validaÃ§Ã£o / teste |
|---|---:|---:|---:|---:|
| Base do modelo entregue | 91 | 27 | 23 | 613 / 247 / 66 |
| ExpansÃ£o do experimento | 117 | 38 | 13 | 691 / 291 / 72 |

A expansÃ£o acrescentou 26 fotos ao treino e 11 Ã  validaÃ§Ã£o, reservando 13 fotos novas para teste. IDs e hashes das 23 imagens anteriores nÃ£o aparecem no conjunto ampliado. Cinco duplicatas idÃªnticas foram removidas na uniÃ£o inicial. A triagem perceptual foi heurÃ­stica e nÃ£o garante ausÃªncia de cenas relacionadas. Os pacotes de reproduÃ§Ã£o conservam os metadados e rÃ³tulos necessÃ¡rios Ã  reconstruÃ§Ã£o.

## Treinamento e comparaÃ§Ã£o de checkpoints

A transferÃªncia de aprendizado foi comparada em duas etapas. Primeiro, trÃªs modelos nano partiram de pesos diferentes, usando os mesmos dados e receita. Depois foi adaptado o YOLO26m, seguido de uma continuaÃ§Ã£o com o conjunto ampliado.

| Experimento | Pesos iniciais | Imagens de treino | Ã‰pocas concluÃ­das | Papel na comparaÃ§Ã£o |
|---|---|---:|---:|---|
| Nano A | Checkpoint customizado da execuÃ§Ã£o antiga de 80 Ã©pocas | 91 | 9 | Comparador |
| Nano B | Checkpoint customizado da execuÃ§Ã£o anterior com 70 fotos | 91 | 9 | Comparador |
| Nano C | YOLO26n oficial prÃ©-treinado | 91 | 9 | Controle |
| MÃ©dio M91 | YOLO26m oficial prÃ©-treinado | 91 | 5 | Modelo selecionado |
| MÃ©dio M117 | Checkpoint M91 | 117 | 7 | ContinuaÃ§Ã£o avaliada, sem promoÃ§Ã£o |

Os nanos usaram AdamW com taxa 0,00005, freeze 10, mÃ¡ximo de 30 Ã©pocas e parada apÃ³s oito sem melhora. O M91 usou AdamW 0,00001, freeze 22, mÃ¡ximo de 12 Ã©pocas e patience 4. O checkpoint selecionado do M91 foi o da primeira Ã©poca. A continuaÃ§Ã£o M117 reaproveitou seus pesos, reiniciando o otimizador, com a mesma taxa e mÃ¡ximo de 12 Ã©pocas. As execuÃ§Ãµes usaram batch 2, seed 42, mosaic zero e CPU. O cÃ³digo verifica hash, arquitetura e classes dos pesos iniciais antes do ajuste fino.

A taxa de aprendizado foi definida explicitamente porque optimizer=auto ignorava o valor manual em execuÃ§Ãµes anteriores. Warmup dos vieses foi fixado em zero. Como as fases nano e mÃ©dio utilizaram receitas e capacidades diferentes, seus resultados nÃ£o isolam o efeito do tamanho do modelo.

![HistÃ³rico das Ã©pocas: receitas distintas; mAP nÃ£o Ã© recall operacional](../../vision/reports/ft91-training-history.png)

## SeleÃ§Ã£o do modelo

ResoluÃ§Ã£o e confianÃ§a foram escolhidas pela validaÃ§Ã£o, considerando precisÃ£o, recall, F1 e falhas por classe. O critÃ©rio de equilÃ­brio foi emendado apÃ³s observar desenvolvimento e registrado antes da regressÃ£o das 23 fotos. Essa alteraÃ§Ã£o faz parte do mÃ©todo e nÃ£o Ã© apresentada como prÃ©-registro original.

Na expansÃ£o, ambos os modelos foram comparados nas mesmas 38 fotos de validaÃ§Ã£o. A continuaÃ§Ã£o sÃ³ seria promovida se nÃ£o regredisse precisÃ£o e recall, melhorasse F1 em pelo menos 0,02 e nÃ£o criasse classe com recall zero que antes tinha acertos. O candidato nÃ£o passou essa regra. A decisÃ£o e o perfil do M91 foram congelados antes da primeira inferÃªncia no teste de 13 fotos; nÃ£o houve ajustes apÃ³s seus resultados.

## Resultados

| Modelo na validaÃ§Ã£o de 38 fotos | ResoluÃ§Ã£o / confianÃ§a | PrecisÃ£o | Recall | F1 |
|---|---|---:|---:|---:|
| M91 mantido | 960 / 0,25 | 72,7% | 71,5% | 0,7210 |
| M117, perfil equilibrado | 960 / 0,26 | 71,5% | 71,5% | 0,7148 |

O aumento do conjunto de treino nÃ£o produziu ganho suficiente para trocar os pesos. O modelo entregue continua sendo o M91, treinado nas 91 fotos iniciais.

| AvaliaÃ§Ã£o do modelo entregue | TP | FP | FN | PrecisÃ£o | Recall |
|---|---:|---:|---:|---:|---:|
| Teste bÃ¡sico reservado: 13 fotos, 72 objetos | 52 | 21 | 20 | 71,2% | 72,2% |
| DiagnÃ³stico anterior: 23 fotos, 66 objetos | 41 | 19 | 25 | 68,3% | 62,1% |

Um acerto exige classe correta, IoU de pelo menos 0,5 e associaÃ§Ã£o um a um com a anotaÃ§Ã£o. No teste reservado, F1 foi 0,7172 e macrorecall, 86,0%. A meta de 70% nas duas mÃ©tricas foi observada nesse lote bÃ¡sico. As 23 fotos anteriores sÃ£o mais complexas e jÃ¡ haviam sido examinadas; a diferenÃ§a entre os dois conjuntos nÃ£o demonstra ganho causado pelo novo treino.

Na comparaÃ§Ã£o anterior sobre as mesmas 23 fotos, o nano registrou 34 TP, 22 FP e 32 FN, com precisÃ£o 60,7% e recall 51,5%. O M91 obteve sete acertos adicionais, trÃªs falsos positivos a menos e sete objetos perdidos a menos. Houve, porÃ©m, regressÃµes em algumas classes.

![ValidaÃ§Ã£o e teste reservado sÃ£o conjuntos distintos](../../vision/reports/ft117-final-profile.png)

## Resultados por classe no teste reservado

| Classe | TP | FP | FN | PrecisÃ£o | Recall |
|---|---:|---:|---:|---:|---:|
| mochila | 1 | 0 | 0 | 100,0% | 100,0% |
| cadeira | 2 | 0 | 2 | 100,0% | 50,0% |
| livro | 12 | 6 | 13 | 66,7% | 48,0% |
| garrafa | 2 | 0 | 0 | 100,0% | 100,0% |
| copo | 5 | 4 | 0 | 55,6% | 100,0% |
| colher | 2 | 1 | 1 | 66,7% | 66,7% |
| garfo | 2 | 1 | 0 | 66,7% | 100,0% |
| tigela | 4 | 0 | 0 | 100,0% | 100,0% |
| relÃ³gio | 2 | 2 | 0 | 50,0% | 100,0% |
| guarda-chuva | 1 | 0 | 0 | 100,0% | 100,0% |
| Ã´nibus | 9 | 0 | 1 | 100,0% | 90,0% |
| semÃ¡foro | 10 | 7 | 3 | 58,8% | 76,9% |

Livros tiveram recall de 48,0% e cadeiras, 50,0%; sÃ£o pontos claros de melhoria. Copos e semÃ¡foros tambÃ©m produziram falsos positivos. O resultado agregado nÃ£o elimina essas diferenÃ§as entre classes.

## AnÃ¡lise de cinco erros

A anÃ¡lise abaixo usa prediÃ§Ãµes reais do diagnÃ³stico de 23 fotos. Ela descreve a localizaÃ§Ã£o e a confianÃ§a das candidatas; nÃ£o determina, sozinha, a causa do erro.

| Imagem | Objeto perdido | Maior IoU de candidata da mesma classe | ConfianÃ§a |
|---|---|---:|---:|
| 182417 | copo | 0,1078 | 0,0384 |
| 30213 | garrafa | 0,9550 | 0,2456 |
| 533206 | garfo | 0,8590 | 0,1555 |
| 17182 | livro | 0,6949 | 0,1542 |
| 313130 | cadeira | 0,8464 | 0,0856 |

No primeiro caso, a localizaÃ§Ã£o nÃ£o alcanÃ§ou IoU 0,5. Nos demais, havia candidata prÃ³xima com confianÃ§a inferior ao limiar 0,25; ela tambÃ©m poderia estar associada a outro objeto. O limiar nÃ£o foi reduzido a partir dessas observaÃ§Ãµes. As prediÃ§Ãµes completas estÃ£o em vision/reports/ft91-medium-regression23.json.

## IntegraÃ§Ã£o e reproduÃ§Ã£o

O mesmo checkpoint avaliado estÃ¡ em vision/release/best.pt, acompanhado de manifesto e licenÃ§a AGPL-3.0. Seu SHA-256 Ã© 3eff4c911170b189d5904b52adde2390f877f0d105a95c092a4b3496653c3bd5. A instalaÃ§Ã£o estÃ¡ no README da raiz; nÃ£o Ã© necessÃ¡rio refazer o treinamento para usar a entrega.

As trÃªs fotos de vision/examples reconheceram Ã´nibus, utensÃ­lios e cadeiras no ensaio HTTP. Uma nova clonagem conferiu o checkpoint e os exemplos.

As evidÃªncias principais sÃ£o finetune117-summary.json, finetune117-decision.json, ft117-reserved13.json e reproduction-union91.json, em vision/reports. O pacote reproduction-union117.json reconstrÃ³i os dados do experimento ampliado. O ensaio da aplicaÃ§Ã£o estÃ¡ em docs/evidencias/release-delivery-http.json. Os dados completos e checkpoints experimentais nÃ£o acompanham o clone.

## LimitaÃ§Ãµes e conclusÃ£o

O modelo atende Ã  meta no pequeno teste bÃ¡sico reservado, mas mantÃ©m objetos perdidos e falsos positivos, especialmente em cenas complexas. A fonte COCO pode ter participado do prÃ©-treinamento e a validaÃ§Ã£o teve uso repetido no desenvolvimento; os nÃºmeros nÃ£o caracterizam um benchmark independente. SÃ£o necessÃ¡rios novos cenÃ¡rios de uso e revisÃ£o pedagÃ³gica antes de aplicaÃ§Ã£o com crianÃ§as. O detector apresenta vocabulÃ¡rio, sem identificar rostos ou autorizar travessias.

O resultado da comparaÃ§Ã£o foi manter o M91: mais imagens e Ã©pocas nÃ£o foram suficientes para justificar o candidato M117. A entrega reÃºne treinamento customizado, comparaÃ§Ã£o de ajustes finos, avaliaÃ§Ã£o por objeto e integraÃ§Ã£o reproduzÃ­vel. O vÃ­deo demonstrativo estÃ¡ vinculado abaixo; o envio acadÃªmico permanece pendente.

## ReferÃªncias

- Desafio FIAP GS CitizenTech 4ES: Applied Computer Vision, pÃ¡gina 44; entrega, pÃ¡gina 24.
- Ultralytics YOLO26: https://docs.ultralytics.com/models/yolo26/
- Ajuste fino: https://docs.ultralytics.com/guides/model-fine-tuning/
- COCO e direitos das imagens: https://cocodataset.org/ e https://cocodataset.org/dataset/termsofuse.htm
- RepositÃ³rio: https://github.com/Acolhe-Projeto/Acolhe---GS8/tree/feat/genai-vision

## VÃ­deos de demonstraÃ§Ã£o

- Computer Vision: https://youtu.be/8FPF_BkSh58
