# Acolhe

Protótipo acadêmico de acolhimento linguístico em português e espanhol, com atividades educativas de mobilidade e uso acompanhado por uma pessoa adulta. Global Solution FIAP 2026.2, CitizenTech.

## Equipe

- Tomáz Versolato Carballo — RM 551417
- Rony Ken Nagai — RM 551549
- Aksel Viktor Caminha Rae — RM 99011
- Ian Xavier Kuraoka — RM 98860

**Repositório:** https://github.com/Acolhe-Projeto/Acolhe---GS8

**MVP público:** https://acolhe-gs8.ambitiousbeach-2f5aaa39.canadacentral.azurecontainerapps.io

Acesso DNS/HTTPS sem login conferido em 19/11/2026: página inicial e APIs de saúde, lições e resumo retornaram HTTP 200. [Evidência da verificação](docs/evidencias/dominio-publico-20261119.json).

**Pitch:** [PowerPoint com resumo Maker incorporado](Acolhe_Pitch.pptx) e [pesquisa, custos e orientações de gravação](Acolhe_Pesquisa_Pitch.md).

O ambiente público disponibiliza o MVP básico: lições, painel, dados e RPA. A LLM local, a visão e o robô funcionam na instalação local descrita abaixo.

## Instalação e execução

### Demonstração geral: GenAI e Vision

Pré-requisitos: Windows, Python 3.12 e Ollama instalado e aberto. A primeira preparação usa internet para instalar as dependências e baixar o Qwen2.5 3B, com aproximadamente 1,9 GB de pesos. O checkpoint Vision de 44 MB acompanha o clone.

```powershell
git clone https://github.com/Acolhe-Projeto/Acolhe---GS8.git
cd Acolhe---GS8
.\scripts\preparar-demo.ps1
.\scripts\iniciar-demo.ps1
```

Abra o endereço exibido no terminal. A porta é escolhida automaticamente a partir de 8080. Para iniciar novamente a demonstração geral, execute `scripts/iniciar-demo.ps1`. Encerre o servidor com Ctrl+C.

A preparação e a inicialização da demonstração geral conferem o digest da LLM e o hash, as classes e o perfil do detector. Não é necessário treinar novamente para usar os modelos da entrega.

### Robô Maker: conversa por voz e hardware

O Maker utiliza Whisper, Qwen3 4B via Ollama e Piper. Sua preparação inclui dependências de voz e comunicação serial, além dos arquivos locais dos modelos.

Consulte [robot/README.md](robot/README.md) para obter os modelos e organizar a pasta de origem. Depois execute, ajustando o caminho:

```powershell
.\Preparar-Robo.cmd --source "C:\Acolhe-modelos"
.\Iniciar-Acolhe.cmd
```

`Iniciar-Acolhe.cmd`:

- Verifica as dependências e os arquivos de voz.
- Inicia o Ollama instalado quando necessário.
- Confere e carrega o modelo configurado, por padrão `qwen3:4b`.
- Valida a geração de voz Piper.
- Abre a conversa no navegador.
- Reutiliza o servidor Acolhe se ele já estiver aberto, preservando a conexão existente do Arduino.

Modelos ausentes geram uma orientação de preparação; o iniciador não faz downloads silenciosos. A seleção da porta USB e a calibração dos motores são realizadas no painel.

A conversa do robô fica disponível em http://127.0.0.1:8080/robo.html na configuração padrão. Mantenha a janela do servidor aberta durante o uso.

### Apenas o servidor básico

Para executar somente o servidor básico, sem iniciar os serviços locais de IA e voz:

```powershell
python -B -m app.server
```

Abra http://127.0.0.1:8080. Não abra `index.html` diretamente, pois a aplicação utiliza a API.

## Testar GenAI

Em **Caminho seguro**, digite uma pergunta e clique em **Perguntar ao ajudante**. Confira a resposta, a fonte e o aviso de acompanhamento adulto.

| Idioma | Pergunta | Resultado esperado |
|---|---|---|
| Português | Como atravessar a rua com segurança? | Orientação com fonte e acompanhamento adulto |
| Español | ¿Qué hago si estoy perdido? | Orientação em espanhol para buscar ajuda |
| Português | Qual é a previsão de chuva amanhã? | Recusa por informação ausente |

O modelo deste módulo é Qwen2.5 3B Q4_K_M. A especialização usa recuperação e agente, sem ajuste dos pesos da LLM. Na avaliação técnica D16, baseline teve 7/16 acertos; RAG e agente, 14/16. A interface usa RAG.

O módulo Maker possui configuração própria de conversa por voz, descrita na seção seguinte.

## Testar Vision

Em **Para educadores → Objetos que ensinam**, selecione uma foto e clique em **Reconhecer objetos**. As três fotos abaixo acompanham o clone em `vision/examples`:

| Arquivo | Resultado esperado |
|---|---|
| 01-onibus.jpg | ônibus / autobús |
| 02-mesa-garfo-tigela.jpg | tigela / cuenco; garfo / tenedor; colher / cuchara |
| 03-copo-cadeira.jpg | cadeiras / sillas; cena mais difícil, com possíveis omissões |

O serviço usa o mesmo YOLO26m91 treinado e avaliado, em `vision/release/best.pt`. O manifesto confere o SHA-256 antes da inferência.

No teste básico reservado de 13 fotos, a precisão foi 71,2% e o recall, 72,2%. No conjunto anterior de 23 fotos, os resultados foram 68,3% e 62,1%; conjuntos diferentes não medem evolução direta.

O detector ainda erra e não decide se uma travessia é segura.

[Créditos das imagens](vision/examples/README.md).

## Maker Lab: robô Acolhe

O robô apoia o acolhimento linguístico com conversa educativa em português e espanhol e atividades sobre o ambiente, sempre com mediação de um adulto.

A proposta CitizenTech utiliza interação por voz, informações ambientais e gestos para apoiar a aprendizagem de pessoas em adaptação ao idioma.

### Componentes

- Arduino Uno conectado ao computador por USB.
- Sensor adicional DHT11 para temperatura e umidade.
- Display QAPASS LCD 16×2 com interface I²C.
- Ponte H L298N.
- Dois motores TT: braço esquerdo e braço direito.
- Protoboard, fios e pack de pilhas AA para os motores.
- Computador com microfone e saída de áudio.

A montagem atual não utiliza buzzer nem controle de velocidade por PWM. Os jumpers ENA e ENB permanecem instalados na ponte; o Arduino controla o sentido e a duração dos pulsos.

### Integração entre sensor, IA e atuação

O fluxo de conversa é:

```text
Microfone
   ↓
Whisper local: transcrição
   ↓
Qwen3 4B via Ollama
   + conteúdo educativo recuperado
   + telemetria validada do DHT11
   ↓
Resposta escrita
   ↓
Piper: síntese de voz no computador
```

O Arduino envia as leituras do DHT11 por USB e atualiza o LCD. O backend valida as medidas e trata leituras inválidas ou expiradas como indisponíveis.

Os valores apresentados vêm da telemetria validada. O sensor não detecta presença nem qualidade do ar, e as medidas não são utilizadas para diagnóstico de saúde.

No treino de palavras, a correção das respostas e a escolha dos gestos seguem regras programadas. O texto livre produzido pela LLM não é interpretado como comando de motor.

### Autonomia

Três leituras válidas consecutivas de pelo menos 30 °C oferecem automaticamente uma atividade sobre calor no painel. A regra rearma abaixo de 28 °C e respeita um intervalo mínimo de dois minutos entre ofertas.

A oferta visual é automática; iniciar a conversa sobre a atividade exige clique ou pergunta. Esses limiares são didáticos, sem significado clínico.

### Movimentos e calibração

| Situação ou comando | Movimento |
|---|---|
| Acerto no treino | Braço esquerdo |
| Nova tentativa após palavra incorreta | Braço direito |
| “Acolhe, mova o braço esquerdo” | Pulso no braço esquerdo |
| “Acolhe, mova o braço direito” | Pulso no braço direito |
| “Acolhe, dê um oi” ou “Acolhe, diga sim” | Pulso no braço esquerdo |
| “Acolhe, diga não” | Pulso no braço direito |

Os identificadores internos permanecem `arm` para braço esquerdo e `head` para braço direito.

Para habilitar os gestos do treino, teste e registre o movimento observado dos dois motores em **Preparar gestos do treino**. O teste manual de pulso não registra automaticamente a calibração.

Os motores TT não possuem encoder: não há garantia de ângulo ou retorno à posição inicial. Os pulsos têm duração limitada a 150 ms e intervalo mínimo de dois segundos. Parar ou reconectar limpa a habilitação dos gestos.

### Como demonstrar

1. Execute `Iniciar-Acolhe.cmd`.
2. Abra a conversa e conecte a porta do Arduino.
3. Confira as leituras do DHT11 e o LCD.
4. Teste e registre os dois motores.
5. Pergunte por voz: “Qual é a temperatura e a umidade da sala?”.
6. Diga “Vamos praticar”.
7. Responda “oi” ou “olá” para `hola`, “cadeira” para `silla` e “garrafa” para `botella`.

“Não sei” e “Repita a pergunta” oferecem ajuda sem gesto. “Encerrar atividade” encerra o treino.

### Documentação e vídeo

- [Instalação, componentes, circuito Mermaid, firmware e calibração](robot/README.md).
- [Conferência dos requisitos e evidências](docs/maker-entrega.md).
- [Roteiro dos vídeos](docs/roteiros_videos.md).
- **[Vídeo demonstrativo Maker — 4min13s](https://youtu.be/Bm3uaAx4McE)**.

O vídeo está dentro do limite de seis minutos e apresenta a proposta, a conversa com leitura ambiental, o treino, o LCD e a montagem. Acesso sem login conferido em 19/11/2026.

A demonstração de falhas e da oferta automática por calor não foi identificada nesse vídeo; esses limites permanecem registrados na documentação.

Para Maker, a documentação oficial é o repositório GitHub. ZIP ou PDF não substituem código, instruções e vídeo. Apenas um integrante realiza a entrega, mantendo os nomes e RMs de todo o grupo no README.

## Big Data, RPA e DevSecOps

- **Big Data:** coleta diária no Airflow de duas fontes reais, IBGE e OBMigra, para `chegada/`; lotes de dias diferentes no Volume do Databricks; Bronze incremental com `COPY INTO`; Prata com `MERGE` e regras de qualidade com contagem; Ouro dimensional e consultas. [Guia](big_data/README.md) · [PDF](docs/entregas/GS_BigData_Acolhe.pdf).

- **RPA:** robô em Python que lê o banco do app, aplica regras de consistência e decisão, registra logs e entrega o resultado ao painel do MVP. [Guia](rpa/README.md) · [PDF](docs/entregas/GS_RPA_Acolhe.pdf).

- **DevSecOps:** container não root, Terraform no Azure, GitHub Actions com Gitleaks, Semgrep e Trivy a cada push, deploy automático pela `main` via OIDC e registro privado, Grafana com os quatro sinais de ouro. [Guia](devsecops/README.md) · [PDF](docs/entregas/GS_DevSecOps_Acolhe.pdf).

## Ficha técnica

- **API:** versão 0.1.0; Python 3.12, SQLite e servidor HTTP.
- **Interface:** HTML/CSS/JavaScript; cinco lições PT/ES, síntese de voz do navegador nas atividades, envio de foto para a visão e service worker.
- **Persistência:** sessões pseudônimas, tentativas, acertos e idioma por tentativa. Exclusão por sessão e expurgo após sete dias nas operações do banco.
- **GenAI:** Qwen2.5 3B com recuperação e agente; a interface utiliza RAG.
- **Vision:** detector YOLO treinado, com checkpoint e manifesto de verificação.
- **Maker:** Arduino Uno USB, DHT11, LCD, dois braços, Whisper, Qwen3 4B/Ollama e Piper. Simulador disponível separadamente.
- **Demais integrações:** pipeline de dados, RPA e indicadores.
- **Infraestrutura:** Azure Container Apps em `canadacentral`, de zero a uma réplica, HTTPS e SQLite persistente em Azure Files, criada por Terraform.
- **CI/CD:** imagem Docker Alpine com usuário não root, scanners Gitleaks, Semgrep e Trivy, Azure Container Registry privado e deploy automático da `main` por OIDC.
- **Monitoramento:** métricas Prometheus e os quatro sinais de ouro no Grafana.

Detalhes de infraestrutura em [devsecops/README.md](devsecops/README.md).

## Documentação da entrega

- [Relatório GenAI](docs/entregas/GENAI_RELATORIO.md): modelo, base, comparação, erros e reprodução.
- [Relatório Vision](docs/entregas/VISION_RELATORIO.md) e [PDF](docs/ACOLHE_VISION.pdf): dados, treinamento, comparação de ajustes finos e resultados.
- [Guia Maker](robot/README.md) e [conferência da entrega](docs/maker-entrega.md): instalação, componentes, integração, firmware, testes e evidências.
- PDFs de [Big Data](docs/entregas/GS_BigData_Acolhe.pdf), [RPA](docs/entregas/GS_RPA_Acolhe.pdf) e [DevSecOps](docs/entregas/GS_DevSecOps_Acolhe.pdf).
- [Requisitos e diagramas de GenAI e Vision](docs/PRD_GENAI_VISION.md).
- [Checklist de entregáveis](docs/CHECKLIST_ENTREGAVEIS_GS.md).
- [Documentação geral](docs/README.md).

Os formatos oficiais de entrega variam por disciplina. Para Maker, utilize a documentação navegável no GitHub e o vídeo vinculado ao README.

## Estrutura do projeto

| Pasta | Conteúdo |
|---|---|
| app | Interface PT/ES, API Python, inicialização, sessões e atividades em SQLite |
| genai | Base autoral, recuperação, adaptador Ollama, agente e avaliação |
| vision | Treino e inferência, checkpoint entregue, imagens e métricas |
| robot | Firmware, DHT11, LCD, gestos dos braços, voz local e simulador |
| big_data | DAGs do Airflow, notebooks Databricks, SQL, amostras e evidências |
| rpa | Automação de relatórios, BPMN, logs e evidências |
| devsecops | Terraform, monitoramento, scripts de verificação e evidências |
| bi | Indicadores e proposta de negócio |
| docs | Entregas, roteiros dos vídeos, manuais e evidências |

## Verificação técnica

```powershell
.\.venv\Scripts\python.exe -B -m unittest discover -v
node --test tests/frontend.test.cjs tests/robot_frontend.test.cjs
```

Para verificar a inicialização local do Maker:

```powershell
.\.venv\Scripts\python.exe -m app.launcher --check
```

Essa verificação confere os serviços de IA e voz sem abrir um novo servidor, iniciar captura de microfone ou acionar motores.

Os testes verificam a implementação; as avaliações dos modelos estão nos relatórios. A suíte automatizada também é executada no GitHub Actions, junto com os scanners de segurança.

Testes de software, compilação e confirmação serial não substituem observação do hardware nem evidências audiovisuais.

## Operação e limites

Localmente, o servidor escuta em loopback por padrão. O controle físico do robô aceita apenas pedidos deste computador.

As atividades usam sessões pseudônimas. O assistente não persiste perguntas e a visão não salva uploads. A conversa do Maker mantém apenas as últimas três interações em memória e não grava as falas do usuário em disco.

As lições podem ficar disponíveis offline pelo service worker, mas o assistente e as atividades com API precisam do servidor.

Não insira nomes, endereços, fotos de pessoas ou dados de crianças. O protótipo não foi validado para uso autônomo com crianças e deve ser utilizado com acompanhamento de uma pessoa adulta.

## Vídeos de demonstração

- [GenAI](https://youtu.be/csoYGnIeviM).
- [Computer Vision](https://youtu.be/8FPF_BkSh58).
- [Maker Lab — Acolhe, 4min13s](https://youtu.be/Bm3uaAx4McE).
- [BI e RPA](https://youtu.be/9Vxrja0XkZk).
