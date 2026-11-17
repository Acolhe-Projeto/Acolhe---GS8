# Acolhe Maker — execução de 11/11/2026

Plano autorizado: Uno USB, DHT11 de três pinos, LCD I2C, L298N e dois motores TT; voz local e painel integrado. Sem buzzer.

## Registro de execução

- Base: branch `feat/acolhe-maker-voz`, criada no checkout existente. Alterações anteriores de logo/manual preservadas; não mover o ambiente para outra pasta, pois os modelos locais e o IDE já estão disponíveis neste computador.
- Testes iniciais RED: módulos `robot.hardware` e `robot.voice` ainda inexistentes, conforme esperado.
- Interfaces: uma conexão serial por servidor; telemetria validada antes de chegar à IA; comandos de atuação definidos pelo código, nunca pelo texto gerado. Histórico em memória, no máximo três interações.
- Decisão de implementação: calibrar cada motor em sessão local, com pulso de teste supervisionado e confirmação humana separada de movimento observado. Nenhuma confirmação serial é tratada como evidência física.
- Critério de conclusão: software e firmware verificáveis separadamente; o MVP físico somente estará validado depois dos testes de bancada, microfone e saída audível com o usuário.

## Andamento

- [x] Adaptador serial, expiração, atividade ambiental e testes.
- [x] Voz local, IA contextualizada e testes reais dos modelos.
- [x] Firmware DHT11/I2C e compilação Uno.
- [x] API local e painel integrado com microfone.
- [x] Regressão, revisão e documentação/evidências de software.

Os resultados finais serão registrados abaixo. Não incluir conversas ou gravações pessoais nas evidências.

## Marco intermediário

- Compilação Uno inicial: 14.940 bytes de flash (46%) e 877 bytes RAM (42%); sem gravação no dispositivo.
- Regressão intermediária: 95 testes Python e 13 testes Node aprovados (inclui testes HTTP herdados repetidos, a ajustar na contagem final).
- Piper gerou WAV real. Primeiro teste Qwen falhou por JSON incompleto; reproduzido e corrigido com JSON Schema e `/no_think`, mantendo `think:false`. A primeira interação completa com áudio sintético passou; demais casos em execução.
- Verificação visual interrompida pela ferramenta CUA: host de navegador indisponível e recusa de acesso ao Brave por não confirmar URL. Não contornar por outra automação. UI visual, microfone real e reprodução audível continuam pendentes.

## Revisão independente e correções

- Requisições remotas a atividades preservam o salvamento educacional, mas não acionam hardware; aplicado o mesmo controle local do painel.
- Reenvio de `request_id` não repete gesto. O Store oferece metadado opcional de criação dentro da transação, sem alterar os retornos dos chamadores anteriores.
- O contexto sensorial é consultado depois da transcrição e novamente após o modelo, antes de formatar as medidas.
- Parar mostra “Interrompendo” e mantém os controles bloqueados até a tarefa anterior liberar o backend; geração em streaming também verifica cancelamento a cada evento. STT e síntese em andamento podem levar alguns segundos para encerrar.
- Os cinco fluxos reais de áudio sintético passaram; revisão semântica humana permanece pendente. Meta10s não garantida em todos os casos. Não declarar validade física ou pedagógica com base nesse resultado.

## Verificação final de software

- 88 testes Python e 19 testes Node passaram. Três verificações de sintaxe JavaScript e `git diff --check` também passaram.
- Firmware Uno compilado: 14.978 bytes de programa (46%) e 878 bytes RAM (42%). Sem upload.
- Cinco casos de áudio sintetizado concluídos: quatro com geração real Qwen3 4B e um com recusa de escopo explicitamente identificada. O modelo não é chamado na recusa. Preparação de respostas entre 2,33 e 15,26 segundos no registro final; latência acima da meta preservada na evidência.
- A restrição de padrão textual complexo no JSON Schema foi removida depois de reproduzir geração instável. Mantido esquema de objeto e validação no código: medidas numéricas geradas só são aceitas se corresponderem ao valor e à unidade da leitura atual. Sem sensor, medidas numéricas são rejeitadas.
- Respostas são limitadas a duas frases no retorno; contexto ambiental recebe medição formatada pelo código e uma frase do modelo. Revisão humana ainda necessária: o modelo produziu termos imperfeitos e respostas redundantes durante a avaliação, registrados sem mascarar como qualidade aprovada.
- Teste HTTP real no servidor final: identidade Acolhe, Qwen3:4b, WAV RIFF válido de182.944bytes, sem erros; resposta preparada em6,42s. Nenhuma porta serial disponível.
- Painel deixado em `http://127.0.0.1:8080/robo.html`, com modelos preparados neste computador. Sem commit, push ou deploy.
- Evidências: `docs/evidencias/maker-verificacao-software.json` e `docs/evidencias/maker-modelos-locais.json`; hashes dos módulos conferidos.

## Ainda depende de bancada

Identificar e medir pack AA; conferir pinagem/jumpers, gravar o firmware, testar LCD/DHT11 e observar/calibrar os dois motores. Testar microfone e reprodução audível no navegador, rever respostas, medir cinco conversas reais, demonstrar falhas e gravar o vídeo. A ferramenta CUA bloqueou a inspeção visual; não alegar revisão visual concluída. O MVP físico completo continua pendente dessas evidências.

## Adaptação ESP32 — após teste serial confirmado pelo usuário

- Usuário gravou o sketch mínimo e confirmou mensagens legíveis naCOM4. Log identifica ESP32-D0WD-V3; esse teste não valida os periféricos.
- O mesmo `acolhe.ino` agora detecta Uno/ESP32 clássico. No ESP32: ENA25/IN1=26/IN2=27; ENB33/IN3=18/IN4=19; DHT11DATA23. PWM LEDC5kHz/8bits explícito no core3.3.12. Falha na configuração PWM bloqueia configuração/atuação.
- LCD desativado por padrão no ESP32 até conferir níveis de SDA/SCL; ao habilitar, I2C21/22 e timeout25ms. Uno preserva LCD por padrão. Backend/painel distinguem LCD desativado de não detectado.
- Compilação ESP32 sem LCD:326.335bytes flash/23.864RAM. ESP32 com LCD:329.875flash/23.920RAM. Uno:15.144flash/882RAM. Todos compilaram; agente não gravou placa.
- Testes relevantes:24Python,7Node, sintaxeJS e diffcheck passaram. Evidência em `docs/evidencias/maker-esp32-compilacao.json`.
- A primeira compilação simultânea dos dois alvos colidiu no cache padrão do CLI; repetida com build-paths distintos, sem apagar arquivos do usuário.
- Documentação atualizada com pinagem, passos no IDE, leitura JSON e teste pelo painel. ResistoresENA/ENB e alimentação/níveis ainda precisam ser conferidos fisicamente. Código não garante níveis seguros em GPIO antes da execução; não substituir resistores por software.

## Teste de motores por comando explícito

- Após o usuário relatar apenas ruído no teste inicial e pedir prosseguir sem mais perguntas de montagem, adicionados comandos fechados `Acolhe, mova o braço` e `Acolhe, mova a cabeça`, por texto ou transcrição. O usuário autoriza cada teste pelo próprio pedido explícito; não é inferência de intenção a partir da resposta do LLM.
- Perfil do comando:100ms/PWM120/sentido1, limitado pelo firmware existente150ms/PWM160, cooldown2s e heartbeat. Envia TEST; não marca `wiring_confirmed` nem `observed` como verdadeiros e não habilita gestos automáticos das atividades. Não aumenta tensão nem modifica firmware.
- Parser exige frase inteira. Negação, pergunta sobre como mover, ambos os motores ou conteúdo da resposta do LLM não acionam. Erro de porta/cooldown é reportado como componente hardware; confirmação fala apenas que o pulso foi enviado.
- Botões rápidos no painel e indicador “Teste por comando disponível”. LCD permanece desativado. Perguntas comuns não movem motores; lições continuam acerto→braço/nova tentativa→cabeça apenas após calibração.
- RED/GREEN e regressão final:97Python+19Node passaram, sintaxeJS e diffcheck aprovados. Testes de atuação usaram serial simulada; nenhum novo pulso físico foi enviado pelo agente. Servo/ângulo/posição não são presumidos.
- Servidor reiniciado após STOP e desconexão ordenados. Usuário deve atualizar a página e conectarCOM4 novamente. Movimento real e alimentação exata permanecem não confirmados.
- Revisão independente corrigiu uma corrida entre comando enfileirado e STOP: o token de cancelamento é verificado dentro do mesmo lock serial da parada, antes do envio. Teste com thread e serial simulada garante que só STOP seja enviado quando o comando foi cancelado. Parser também preserva palavras e interrogação, rejeitando `Como teste de cabeça?` e `Teste de cabeça`.

## Ajuste do pulso após novo relato de apito

- Usuário pediu maior rotação após os testes emitirem apenas som. Perfil de comandos e valores iniciais do formulário ajustados de100ms/PWM120 para150ms/PWM160 (o formulário antigo ainda iniciava35ms/PWM80). Esse é o teto do firmware existente, que não foi alterado nem regravado. Tensão de alimentação não modificada.
- Painel agora mostra duração/PWM retornados pelo backend no resultado do comando. TesteNode verifica essa indicação e mantém a mensagem de movimento não confirmado.
- RED/GREEN dos dois testes de despacho;36 testesPython relevantes e8Node passaram, além de sintaxeJS/diffcheck. Nenhum novo pulso físico enviado pelo agente. Servidor reiniciado após STOP/desconexão para carregar perfil; portaCOM4 restaurada apenas para comunicação.
- Sem rotação observada neste teto, é necessário conferir alimentação, ligações e motor; não ampliar limites nem atribuir o problema a potência sem medições. Movimento real e segurança mecânica permanecem não verificados.
- Durante a reconexão, a abertura serial ficou sem receber dados e o software antigo apresentou incorretamente “firmware incompatível”. Um diagnóstico enviando apenas HELLO/STOP confirmou que liberar DTR e pulsar RTS restaurava boot normal, handshake ACOLHE_V1 e DHT válido, sem gravação. O adaptador agora repete HELLO e realiza uma única recuperação RTS após1,5s de silêncio; distingue ausência de resposta de versão incompatível. TesteRED/GREEN cobre essa recuperação. Foram37Python e8Node relevantes aprovados após essa correção.

## Montagem Uno sem controle de enable — 17/11/2026

- Usuário mudou para Uno com LCDI2C, DHT11 e L298N, ENA/ENB nos jumpers sem fiosD5/D6 ou resistoresENA/ENB. Apenas jumper do reguladorATIVA5V retirado, lógica pelo5V do Uno e potência pelo pack. O texto explícito substitui a imagem antiga enviada, que ainda mostra EN por GPIO e três jumpers removidos.
- Firmware atual exclusivoUno: IN1D2/IN2D3, IN3D4/IN4D7, DHTD8, LCDI2C A4/A5 com endereço detectado. Sem analogWrite/LEDC ou controle de EN. LOW/LOW freia com EN alto; reset/gravação não têm garantia de software e exigem potência dos motores desligada. README explica quatro pull-downs em IN1–IN4 caso seja necessário definir entradas também no reset.
- Protocolo novoACOLHE_V2/direction_only. TEST eCONFIG recebem motor/duração/sentido, sem velocidade. Backend rejeita firmwareV1 e requisições antigas com campoPWM antes de atuar; painel remove o campo e informa acionamento total. Perfil inicial100ms por comando, máximo150ms, intervalo2s/heartbeat2s mantidos. Calibração observada ainda exigida para gestos automáticos, sem confundir envio com movimento.
- RED/GREEN de handshake/perfil/rejeição dePWM e apresentação no painel. Regressão final100Python+20Node passou; sintaxeJS e diffcheck passaram. CompilaçãoUno:14.800bytes flash (45%) e870RAM (42%). Revisão independente sem achados importantes.
- Sem placa serial detectada nesta verificação; nenhum upload, teste de motor ou validação do novo LCD físico pelo agente. Usuário deve gravar o novo arquivo noUno, confirmarACOLHE_V2 noMonitorSerial115200 e conectar a porta atual no painel. EvidênciasESP32/11nov permanecem históricas.

## Movimentos confirmados e IA local retomada — 17/11/2026

- Usuário confirmou teste físico da cabeça e do braço. Backend real: Uno/ACOLHE_V2 conectado naCOM5, motor_controldirection_only, calibrações de100ms/sentido1 paraambos; DHT válido e interfaceLCD detectada. A declaração é do operador; o sistema não mede ângulo/movimento e não houve confirmação visual doLCD pelo agente.
- Pergunta comum falhou porque Ollama não estava executando: sem processo/porta11434 e conexão local recusada. Modelo qwen3:4b já existia. Iniciado somente o serviço instalado `ollama.exe serve`, sem baixar/trocar modelo e sem reiniciar o Acolhe ou perder calibrações.
- Teste real porHTTP da identidadeAcolhe retornou geraçãoQwen3:4b e WAVRIFF válido188.064bytes, sem erros,11,81s. Não acionou motor; microfone/reprodução audível não foram testados pelo agente. Evidência em `docs/evidencias/maker-motores-ia-20261117.json`.
- O Ollama deve continuar executando em segundo plano durante as perguntas; depois de reiniciar o Windows, iniciar o Ollama antes do uso. Não houve mudança de código da IA nessa correção de serviço.

## Conversa educativa e treino com gestos — 17/11/2026

- Novos pedidos exatos: “Acolhe, dê um oi” e “Acolhe, diga sim” pedem pulso do braço; “Acolhe, diga não” pede pulso da cabeça. Mantidos mova/mexa/teste + braço/cabeça. São regras explícitas sobre a fala do usuário; texto gerado pela IA nunca controla motores.
- Treino “Vamos praticar”: hola → olá/oi; silla → cadeira; botella → garrafa. Acerto pede braço; palavra incorreta pede cabeça, apenas com os dois motores calibrados e respeitando intervalo. Dicas/repetição sem gesto. Perguntas e negações não são erros; pare/encerrar atividade termina. Parar cancela o treino pendente; limpar conversa também o zera.
- Conversa com apresentação mais simples, prioridade para a última pergunta e material de agradecimento/pedidos gentis. Painel ganhou botões, instruções e identificação de atividade guiada (regra curada, não geração LLM).
- 108 testes Python e 20 Node passaram; sintaxe JS válida. Revisão independente encontrou negação isolada acionando reação e cancelamento adiantando treino: ambos reproduzidos em testes e corrigidos, revisão final sem problemas importantes.
- Teste HTTP real em servidor temporário sem serial: três perguntas Qwen3 e cinco etapas de treino, todas com WAV Piper válido e sem erros (0,58–2,47s com modelo aquecido). Evidência maker-conversa-atividades-20261117.json. Sem validação de microfone, reprodução audível ou novos movimentos físicos.
- Servidor antigo em 8080 continua executando código anterior. Reinício automático bloqueado pela revisão de permissões, sem razão específica. Usuário precisa encerrar servidor Python PID3964, abrir Iniciar-Acolhe.cmd, atualizar navegador e reconectar COM5. Não foi gravado firmware nem alterada montagem. Última consulta já mostrava calibrações vazias; gestos automáticos precisam ser registrados novamente.
## Entrada da conversa e calibração visível — 17/11/2026
Usuário confirmou treino hola/silla/botella funcionando, mas sem gestos; pulso manual funciona. Consulta real a /api/robot/status: COM5 conectada, sensor válido, motors_enabled:false e calibrations:{}; causa é ausência de registro dos dois motores nesta conexão, não falha da correção das respostas. Não alterada a exigência de calibração nem registradas observações no lugar do usuário.
Página inicial ganhou cartão teal/peach com ícone de microfone, explicação e botão “Começar conversa”, responsivo e com foco existente. Painel do robô ganhou aviso visível com contador 0/2 e atalho “Preparar gestos do treino” que apenas abre a seção. Resposta sem gesto agora explica registro de cabeça/braço, preservando cooldown e parada. Usuário deve testar e clicar “Observei movimento seguro: registrar” para cada motor. Parar/reconectar/recarregar pode limpar a habilitação por segurança.
21 testes JS passaram, incluindo abertura do preparo e confirmação de nenhum comando pulse/calibrate enviado por esse atalho; 34 testes de hardware/voz passaram, sintaxe JS e diffcheck válidos. HTTP confirmou arquivos estáticos novos servidos na8080, sem reinício de backend ou mudança de firmware. Atualizar Ctrl+F5 para carregar. Nenhum novo movimento físico acionado pelo agente e sem inspeção visual de navegador nesta alteração.
## Conferência e preparação do commit — 17/11/2026
Usuário confirmou que os gestos do treino funcionaram. Atualizados README principal e guia do robô com estado real separado de detecção/telemetria e evidência audiovisual. Criada docs/maker-entrega.md com matriz dos entregáveis e critérios, incluindo limites: oferta de atividade ambiental é automática, mas chamada da IA exige interação; vídeo, demonstração real de mudança ambiental/falhas, tensão exata do pack e publicação continuam pendentes.
Guia passou a incluir preparação em clone limpo sem depender do Talos, estrutura Whisper/Piper e comandos oficiais Ollama. Corrigida validação de pacote incompleto antes da cópia; teste reproduziu a falha e passou após a correção. Verificação final:112 Python,21 JavaScript, sintaxe JS, links locais e diffcheck válidos; compilação Uno14.800bytes de flash/870RAM. Revisão independente sem bloqueios para commit local. Nenhum upload ou novo comando físico foi realizado. PDF do enunciado mantido como referência local, fora do commit; pesos, executáveis de modelos e dados de execução ignorados.