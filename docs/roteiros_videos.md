# Roteiros dos vídeos técnicos

Roteiros para gravação, não evidências de execução. Ajustar a fala ao estado real dos componentes e ensaiar com cronômetro.

# RPA até três minutos

## 0min00s a 0min25s Processo

Mostrar nome do projeto e objetivo: consolidar o progresso agregado do banco local sem cadastro nominal e sem envio externo. Explicar que o fluxo usa Python, leitura SQL e arquivos de saída. Mostrar PDD e BPMN quando preparados pelo módulo RPA.

## 0min25s a 0min55s Entradas e condições

Mostrar o banco de demonstração criado pelo MVP, sem revelar identificadores de sessões. Explicar as entradas: banco SQLite existente e pasta de saída. Indicar que o acesso é de leitura e que a pasta precisa permitir gravação. Identificar os dados como sintéticos.

## 0min55s a 1min30s Atividade no app e sucesso

Com o MVP aberto (`python -B -m app.server`), mostrar o painel "Acompanhamento automático" ainda sem relatório. Responder as cinco lições corretamente. Executar, na raiz do projeto:

`python -B -m rpa.robot --db data/acolhe.db --output rpa/output`

Mostrar código de saída 0, `progress.md` com a decisão `progresso_adequado` e `robot.log` com `report_started`, `decision` e `report_completed`. Clicar em "Atualizar painel": os totais aparecem no MVP. Explicar que sessão não é pessoa e que taxa de acerto não comprova aprendizagem.

## 1min30s a 2min00s Decisão

Em outra sessão (ES), errar três vezes a lição "Caminho seguro". Rodar o robô de novo. Mostrar a decisão `reforco_recomendado` com `mobilidade` para revisão no log, em `progress.md` e no painel ("Revisar: mobilidade"). Explicar a regra: menos de 60% de acerto com pelo menos 3 tentativas.

## 2min00s a 2min30s Falha controlada

Executar com `--db nao_existe.db`. Mostrar a mensagem `RPA failed`, o código de saída 1 e `report_failed` no log, e que nenhum banco foi criado. O painel continua com o último relatório válido. Explicar como o operador corrige o caminho.

## 2min30s a 2min50s Agendamento e encerramento

Mostrar `python -B -m rpa.robot --every 3600` como agendamento embutido e o comando `schtasks` documentado no README. Mostrar o BPMN no bpmn.io. Não alegar envio por e-mail: o fluxo gera arquivos locais e alimenta o MVP. Alternativa sem gravar a tela do app: `python -B -m rpa.demo_e2e --evidence rpa/evidence` executa os três cenários de uma vez.

## Evidências para guardar

Comando e versão, log completo, arquivos produzidos, cenário de falha, roteiro do processo e vídeo. Confirmar acesso ao link antes da entrega.

# Maker até seis minutos

## 0min00s a 0min35s Objetivo

Apresentar o robô tutor como apoio a atividades do Acolhe. Explicar que a reação ao erro deve ser uma dica ou incentivo. Não prometer acompanhamento autônomo de crianças.

## 0min35s a 1min20s Hardware

Mostrar os componentes físicos realmente montados: controlador, fonte/baterias, ponte H, motores e sensor adicional. Nomear o DHT11 (temperatura em graus Celsius e umidade relativa em porcentagem), LCD QAPASS I2C, Uno USB, L298N e dois motores TT. Nao ha buzzer. Explicar alimentação e limites. Motores e servos são atuadores, não sensores.

Montagem atual de17/11: ENA/ENB com jumpers instalados, sem fiosD5/D6 e sem PWM; jumper do reguladorATIVA5V retirado, lógica5V externa e GNDcomum. Mostrar duração/sentido no painel e explicar acionamento total e freioLOW/LOW. Não usar o diagrama antigo com resistoresENA/ENB como se fosse a montagem atual.

Se o sensor ainda não estiver montado, esta parte não está concluída. Uma imagem de circuito ou um simulador não satisfaz a demonstração física.

## 1min20s a 2min15s Sensor real

Mostrar a leitura real do DHT11 no LCD e no painel /robo.html, mudando com uma condição controlada e segura. Nao usar chama, liquidos ou ar quente intenso. Mostrar tambem o estado indisponivel com o sensor desconectado de forma eletricamente segura. Manter visíveis o componente e a leitura correspondente. Registrar unidade, limiar e tratamento de leitura inválida. Não movimentar o robô perto de crianças durante testes de bancada.

## 2min15s a 3min25s Integração com IA

No painel Acolhe, clicar para falar e perguntar como esta a sala. Mostrar transcricao Whisper, resposta do Qwen3 4B com leitura valida e reproducao Piper. Explicar que numeros vem da telemetria validada e texto educativo vem do modelo local. Mostrar a oferta de atividade de calor (regra didatica de tres leituras >=30 C, rearme abaixo de28 C, intervalo120 s) se a condicao ocorrer realmente; fixtures so podem ser mostradas como testes de software, nunca como medicao fisica. Distinguir regra programada, recuperação de conteúdo e inferência de modelo. Se a IA não estiver ligada ao hardware, registrar isso como pendência, sem narrar a simulação como integração real.

## 3min25s a 4min35s Ação e retorno

Com calibracao supervisionada confirmada nos dois motores, executar um caso de acerto (braco esquerdo) e um caso de erro (braco direito). Confirmar movimento visivel e parametros de bancada. Demonstrar tambem a mudanca de estado no LCD I2C. Mostrar uma ação segura e um incentivo apropriado. Explicar como o mediador pode interromper. Evitar movimentos bruscos, força excessiva ou reação punitiva.

## 4min35s a 5min20s Falha e segurança

Demonstrar perda de comunicação ou leitura inválida em condição controlada. Mostrar parada ou estado seguro. Explicar heartbeat de0,5s, parada por perda de comunicacao apos2s, pulsos ate150ms, intervalo2s e bloqueio de motores no boot/parada. Registrar limites mecanicos e supervisao. O botao Parar e uma parada por software; mostrar acesso ao corte de alimentacao dos motores. Nunca retirar proteção elétrica para encenar uma falha.

## 5min20s a 5min45s Conclusão

Recapitular sensor, decisão e ação efetivamente demonstrados. Exibir pendências restantes. Encerrar até 5min45s para margem.

## Evidências para guardar

Fotos da montagem, diagrama conferido, lista de componentes reais, versão do firmware, leituras com data/hora, eventos da aplicação, casos de segurança e vídeo. Não usar imagens de pessoas sem autorização. Não afirmar hardware concluído com base em testes do simulador.

### Sequência curta para a atividade com gestos
Dizer “Vamos praticar”. Acolhe pergunta como se diz hola: responder “olá” para mostrar acerto e gesto do braço esquerdo. Na pergunta silla, responder “livro” para demonstrar dica e gesto do braço direito; em seguida “cadeira” e “garrafa” para concluir. Registrar previamente os dois motores na calibração supervisionada. Esperar ao menos dois segundos entre gestos. Dizer “não sei” demonstra dica sem gesto; “Encerrar atividade” termina. Explicar que essa avaliação é regra curada e que as outras perguntas usam Qwen3; não chamar a regra de geração de IA.