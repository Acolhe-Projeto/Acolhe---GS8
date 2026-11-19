# Acolhe — pesquisa e premissas do pitch

Consulta: **19/11/2026**. Apresentação: `Acolhe_Pitch.pptx` (10 slides de apresentação + 2 de apoio). As falas e tempos estão nas notas do apresentador. Os dois slides de apoio ficam ocultos na apresentação normal.

## Valores para preencher o roteiro

> Nosso custo inicial estimado para um piloto com uma instituição é de **R$ 900**, com operação mensal estimada em **R$ 210**. A assinatura proposta para validação é de **R$ 299 por mês por instituição**. Esse cenário reutiliza um computador existente; implantação e kit robótico são cobrados separadamente.

São estimativas de planejamento, não gastos comprovados nem preços aceitos por clientes. Não houve entrevista comercial nesta pesquisa. Preços de lojas podem mudar; disponibilidade, frete, compatibilidade e orçamento final precisam ser conferidos antes de comprar.

## Evidência do problema

O [UNICEF](https://www.unicef.org/brazil/historias/o-primeiro-dia-de-angelica-na-escola-brasileira), em artigo de **26/04/2024**, informa que sua iniciativa ajudou a identificar e matricular **2.300 crianças e adolescentes migrantes em Roraima em 2023**, moradores dos abrigos da Operação Acolhida e fora da escola. O artigo também descreve o contexto de convivência entre português e espanhol.

O número contextualiza o acesso escolar. **Não mede a população de 6–10 anos, o tamanho do mercado, a incidência de barreira linguística ou resultados do Acolhe.** O recorte de 6–10 anos é a escolha do projeto.

## Custo inicial: R$ 900

Referência de reposição de componentes equivalentes, não reprodução exata de marca/modelo da montagem:

| Item | Quantidade | Valor total | Base |
| --- | ---: | ---: | --- |
| Placa compatível com Uno | 1 | R$ 98,90 | Referência BlackBoard UNO R3, RoboCore |
| LCD 16×2 com I²C | 1 | R$ 23,90 | Referência RoboCore |
| Motor DC 3–6 V com redução | 2 | R$ 15,80 | R$ 7,90/unidade, RoboCore |
| DHT11 | 1 | R$ 7,90 | Referência AutoCore |
| Módulo ponte H L298N | 1 | R$ 29,50 | Referência Recicomp |
| Cabos, protoboard, pilhas/pack, estrutura e áudio | conjunto | R$ 120,00 | Verba estimada; composição final a cotar |
| Montagem supervisionada | 2 h × R$ 50 | R$ 100,00 | Premissa interna de trabalho |
| Reserva para frete, variações e reposição | — | R$ 104,00 | Reserva de planejamento |
| **Kit montado — orçamento** | | **R$ 500,00** | Soma acima |
| Implantação e capacitação | 8 h × R$ 50 | R$ 400,00 | Premissa interna de trabalho |
| **Total inicial estimado** | | **R$ 900,00** | Kit + implantação |

Não inclui compra/depreciação de computador, desenvolvimento já realizado, tributos, viagens, certificação, adequação física do robô ao uso infantil ou revisão jurídica/pedagógica completa. O cenário é um piloto supervisionado com computador, conexão e espaço cedidos pelo parceiro. Uma implantação comercial precisa de orçamento próprio.

## Operação mensal: R$ 210

| Item | Valor/mês | Premissa |
| --- | ---: | --- |
| Hospedagem web e API | R$ 60,00 | Arredondamento da referência KVM 1 a R$ 59,99/mês de renovação |
| Suporte | R$ 100,00 | Até 2 h/mês × R$ 50/h |
| Revisão de conteúdo e manutenção | R$ 30,00 | 1 h/mês × R$ 30/h; estimativa interna |
| Reserva operacional | R$ 20,00 | Backup adicional, reposição/consumo e variações; estimativa |
| **Total** | **R$ 210,00** | Uma instituição piloto |

A [Hostinger](https://www.hostinger.com/br/servidor-vps) mostrava KVM 1 a R$ 29,99/mês na contratação promocional de 24 meses (total R$ 719,76) e renovação a R$ 59,99/mês pelo mesmo período. Usamos a renovação como referência, **não uma promessa de contratação mensal avulsa**. O desembolso antecipado desse plano não está nos R$ 900: o total inicial é implantação + kit, e os R$ 210 representam custo mensal equivalente. Se esse plano específico for contratado, prever também seu compromisso de caixa. Não houve contratação ou validação de capacidade. IA e voz continuam no computador local; esse VPS é referência para a aplicação web/API, não para inferência do Qwen3 4B.

## Hipótese comercial

- **Assinatura:** R$ 299/mês/instituição, para validar com compradores, incluindo plataforma, atualizações e até 2 h de suporte.
- **Implantação e capacitação:** R$ 400, uma vez, hipótese para cobrir as 8 h previstas.
- **Kit opcional:** orçamento de R$ 500, separado da assinatura; não há margem de hardware calculada.
- **Diferença mensal simples:** R$ 299 − R$ 210 = **R$ 89**, antes de tributos, aquisição de clientes, amortização do desenvolvimento e custos não incluídos. Não representa lucro líquido nem comprova viabilidade.
- Se o suporte ultrapassar 2 h/mês ou houver aquisição de computador, rever o cenário. Não extrapolar estes custos para escala sem medir uso.

## Entrada no mercado — proposta, ainda não validada

Usuários: crianças hispanofalantes de 6–10 anos com adulto mediador. Possíveis compradores: escolas, organizações de acolhimento e secretarias de educação. Canal inicial proposto: contato direto com coordenação pedagógica e organizações locais que já trabalham com famílias migrantes. Nenhuma instituição está confirmada como cliente ou parceira.

Pedido: **uma instituição parceira, dois mediadores e quatro semanas de piloto**, após revisão pedagógica, de privacidade e das condições físicas de uso. Semana 1: capacitação e atividade inicial; semanas 2–3: uso acompanhado; semana 4: atividade equivalente, entrevistas com mediadores e revisão de custos. Coletar apenas dados necessários e autorizados. Critérios propostos para decisão: adesão dos mediadores, conclusão das atividades, avaliação de adequação por educador, custo observado e interesse de contratação. Metas numéricas dependem de acordo com o parceiro.

## Indicadores e impacto

Disponíveis no protótipo: sessões, tentativas e taxa de acerto (acertos/tentativas × 100; sem tentativas, indicador indisponível). Sessões não equivalem a crianças únicas. Dados exibidos na gravação devem ser de teste. O treino do robô é uma demonstração separada: não presumir que suas interações compõem os agregados do painel.

Propostos: comparação antes/depois com atividades equivalentes e análise de educador; instituições em piloto; conversão (contratos/pilotos concluídos, com janela definida); custo mensal por instituição. Antes/depois exploratório não isola causalidade. Não há aprendizagem ou impacto comprovado.

Relação proposta com [ODS 4 — Educação de qualidade](https://brasil.un.org/pt-br/sdgs/4), especialmente inclusão no acesso à aprendizagem, e [ODS 10 — Redução das desigualdades](https://brasil.un.org/pt-br/sdgs/10), especialmente inclusão social (10.2). Trata-se de alinhamento de propósito, não impacto medido ou certificação da ONU.

## Fontes de preço

1. [RoboCore — lista de materiais com Uno e LCD](https://www.robocore.net/modules.php?addlist=50&name=GR_LojaVirtual): R$ 98,90 e R$ 23,90; lista consultada como referência, sem adicionar itens a carrinho.
2. [RoboCore — materiais do tutorial de motores](https://www.robocore.net/tutoriais/controle-motores-com-rocky): motor DC 3–6 V com eixo duplo, R$ 7,90/unidade.
3. [AutoCore — sensores](https://www.autocorerobotica.com.br/modulos-sensores/sensores): DHT11, R$ 7,90, sem usar desconto Pix.
4. [Recicomp — drivers](https://www.recicomp.com.br/robotica/motor/driver-motor/): módulo ponte H L298N, R$ 29,50.
5. [Hostinger — VPS](https://www.hostinger.com/br/servidor-vps): condições detalhadas acima.

## Gravação e estado real

O roteiro recebido orienta mostrar URL pública. A documentação local consultada confirma execução em `127.0.0.1:8080`; **não foi fornecida nem validada uma URL pública do MVP nesta tarefa**. Não inventar endereço nem apresentar localhost como publicação. Usar o slide de demonstração como transição e mostrar a aplicação real. A publicação do MVP continua uma preparação da equipe, quando exigida pela rubrica.

Robô: Uno, LCD I²C, DHT11, L298N e dois motores TT; voz/IA no computador. Treino de palavras usa regras e respostas esperadas; conversa aberta usa Qwen3 4B local via Ollama. Braço esquerdo no acerto e direito na nova tentativa, após calibração. O sensor fornece temperatura/umidade; não detecta presença nem qualidade do ar. Demonstrar somente funções confirmadas em ensaio. O vídeo Maker existente não substitui a gravação do pitch de negócios.

## Equipe conferida no README

- Tomáz Versolato Carballo — RM 551417
- Rony Ken Nagai — RM 551549
- Aksel Viktor Caminha Rae — RM 99011
- Ian Xavier Kuraoka — RM 98860
