# Conferência da entrega Maker Lab — Acolhe

Revisão em 17/11/2026. Configuração atual: Arduino Uno USB, DHT11, LCD QAPASS I²C e dois motores TT pela L298N, sem buzzer e sem PWM. O computador executa Whisper, Qwen3 4B/Ollama e Piper. Este documento não certifica uma nota nem substitui a demonstração real.

## Entregáveis obrigatórios

| Requisito | Situação e referência |
| --- | --- |
| Repositório GitHub com código-fonte | Código local preparado; remoto configurado: https://github.com/TomazVC/Acolhe---GS8. O commit precisa de push e revisão da branch entregue para que esta versão apareça no GitHub. |
| Nomes de todos os integrantes | Quatro nomes e RMs presentes no README principal e em `robot/README.md`. Um integrante envia o link oficial do grupo. |
| Instalação e execução reproduzíveis | Guia do [robô](../robot/README.md), seção de preparação em outro computador, dependências fixadas e firmware Uno. Os modelos locais são obtidos separadamente, não incluídos no Git. Reprodução completa em um segundo computador ainda não foi comprovada. |
| Componentes, montagem e circuito | Tabela de ligações, Mermaid, alimentação, jumpers, pinos e calibração no guia. Falta registrar a quantidade/tensão exata do pack AA e fotos da montagem final. |
| Integração sensor/IA/atuação | Firmware envia DHT11; backend valida e expira leituras; conversa incorpora medidas e material educativo; LCD exibe estados; acertos/novas tentativas acionam gestos calibrados por regra. Saída livre do LLM não vira comando de motor. |
| Vídeo de até seis minutos | **Pendente.** Gravar, conferir duração e acesso, e inserir link real no README principal e no README do robô. [Roteiro](roteiros_videos.md), com margem até 5min45s. |
| Documentação oficial no GitHub | READMEs e este documento são navegáveis no repositório. PDF/ZIP não substituem a entrega. O PDF de enunciado é apenas referência local. |

## Critérios e limites da comprovação

| Critério | Implementação e evidência que falta |
| --- | --- |
| Autonomia e decisão | Regra de três leituras ≥30 °C oferece automaticamente uma atividade no painel; rearma abaixo de 28 °C, com intervalo mínimo de 120 s. **A oferta visual é automática; iniciar a conversa sobre ela exige clique/pergunta.** Não há voz ou motor autônomo provocado pelo calor. Mostrar a mudança real e distinguir essa regra da geração IA. |
| Acabamento | Montagem física existe e movimentos foram confirmados pelo operador. Fotos/vídeo precisam mostrar fixação, organização dos fios, alimentação e acesso ao corte dos motores. |
| Testes e demonstração | Testes automatizados cobrem telemetria inválida/expirada, cancelamento, comandos permitidos, calibração e fluxo HTTP/voz. Registrar também USB desconectado, sensor indisponível, Ollama parado e parada durante gesto na montagem real. |
| Criatividade e inovação | Acolhimento linguístico PT/ES, conversa com voz local, contexto ambiental e treino de palavras com gestos. Explicar a contribuição concreta para aprendizagem e adaptação ao idioma. |
| Sensor adicional | DHT11 físico enviou temperatura/umidade válidas ao backend. Demonstrar a leitura, uma variação real e sua utilização na resposta; não apresentar fixtures como medições físicas. |
| Implementação IA | Qwen3 4B local com recuperação de conteúdo e medidas validadas, transcrição Whisper e síntese Piper. Existem evidências HTTP/Qwen3/Piper reais; falta registrar cinco conversas completas com microfone e reprodução audível. Treino e correção de palavras são regras curadas, identificadas separadamente. |
| Integração hardware/software | Handshake ACOLHE_V2 recebido; DHT11 válido e interface LCD detectada; operador confirmou cabeça, braço e gestos do treino. O sistema não mede ângulo nem comprova movimento por ACK. Falta registro audiovisual do LCD e de toda a cadeia. |
| CitizenTech | Problema: barreira linguística no acolhimento de pessoas em adaptação ao português. Solução acadêmica educativa com mediação de adulto; não há validação com público real nem diagnóstico de saúde/conforto pelo sensor. |

## Evidências disponíveis

- [Conversa e atividade por HTTP, com Qwen3 e Piper reais](evidencias/maker-conversa-atividades-20261117.json): entrada por texto, sem serial, microfone ou reprodução audível; sensor explicitamente indisponível nesse teste.
- [Retomada da IA e observação dos motores](evidencias/maker-motores-ia-20261117.json): registro técnico e confirmação humana, sem vídeo.
- [Compilação Uno sem PWM](evidencias/maker-uno-sem-pwm-20261117.json): 14.800 bytes de flash e 870 bytes de RAM; não é evidência de movimento.
- [Histórico de implementação](maker-implementacao.md). Arquivos de evidência ESP32/11 de novembro são históricos e não validam a montagem Uno atual.

## Antes de enviar

1. Medir e documentar pack AA, fotografar a montagem e conferir o LCD real.
2. Registrar sensor → resposta contextualizada da IA → voz, gestos e pelo menos uma falha controlada. Demonstrar a oferta automática de atividade apenas se a condição física ocorrer; não forçar aquecimento perigoso nem usar simulação como prova física.
3. Gravar vídeo de até seis minutos e colocar o link nos READMEs. Testar o acesso em janela anônima.
4. Publicar a revisão do código e documentação no GitHub e conferir a branch/link que será enviado. Commit local sozinho não publica.
5. Um integrante envia o link GitHub; manter os quatro nomes/RMs no README.
