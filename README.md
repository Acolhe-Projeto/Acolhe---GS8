# Acolhe

Protótipo acadêmico de acolhimento linguístico em português e espanhol, com atividades educativas de mobilidade e uso acompanhado por uma pessoa adulta. Global Solution FIAP 2026.2, CitizenTech.

## Equipe

- Tomáz Versolato Carballo — RM 551417
- Rony Ken Nagai — RM 551549
- Aksel Viktor Caminha Rae — RM 99011
- Ian Xavier Kuraoka — RM 98860

**MVP público:** https://acolhe-gs8.ambitiousbeach-2f5aaa39.canadacentral.azurecontainerapps.io (MVP básico: lições, painel, dados e RPA; a LLM local, a visão e o robô rodam na instalação local abaixo).

## Instalação e execução

Pré-requisitos: Windows, Python 3.12 e Ollama instalado e aberto. A primeira preparação usa internet para instalar as dependências e baixar o Qwen2.5 3B, com aproximadamente 1,9 GB de pesos. O checkpoint Vision de 44 MB já acompanha o clone.

```powershell
git clone https://github.com/Acolhe-Projeto/Acolhe---GS8.git
cd Acolhe---GS8
.\scripts\preparar-demo.ps1
.\scripts\iniciar-demo.ps1
```

Abra o endereço exibido no terminal. A porta é escolhida automaticamente a partir de 8080. Depois da preparação, `Iniciar-Acolhe.cmd` abre a demonstração completa; sem o ambiente `.venv`, ele inicia só o MVP básico com `python -m app.server`. Encerre o servidor com Ctrl+C.

A inicialização confere o digest da LLM e o hash, as classes e o perfil do detector. Não é necessário treinar de novo para usar os modelos da entrega.

## Testar GenAI

Em **Caminho seguro**, digite uma pergunta e clique em **Perguntar ao ajudante**. Confira a resposta, a fonte e o aviso de acompanhamento adulto.

| Idioma | Pergunta | Resultado esperado |
|---|---|---|
| Português | Como atravessar a rua com segurança? | Orientação com fonte e acompanhamento adulto |
| Español | ¿Qué hago si estoy perdido? | Orientação em espanhol para buscar ajuda |
| Português | Qual é a previsão de chuva amanhã? | Recusa por informação ausente |

O modelo é Qwen2.5 3B Q4_K_M. A especialização usa recuperação e agente, sem ajuste dos pesos da LLM. Na avaliação técnica D16, baseline teve 7/16 acertos; RAG e agente, 14/16. A interface usa RAG.

## Testar Vision

Em **Para educadores → Objetos que ensinam**, selecione uma foto e clique em **Reconhecer objetos**. As três fotos abaixo acompanham o clone em vision/examples:

| Arquivo | Resultado esperado |
|---|---|
| 01-onibus.jpg | ônibus / autobús |
| 02-mesa-garfo-tigela.jpg | tigela / cuenco; garfo / tenedor; colher / cuchara |
| 03-copo-cadeira.jpg | cadeiras / sillas; cena mais difícil, com possíveis omissões |

O serviço usa o mesmo YOLO26m91 treinado e avaliado, em vision/release/best.pt. O manifesto confere o SHA-256 antes da inferência. No teste básico reservado de 13 fotos, a precisão foi 71,2% e o recall, 72,2%. No conjunto anterior de 23 fotos, os resultados foram 68,3% e 62,1%; conjuntos diferentes não medem evolução direta. O detector ainda erra e não decide se uma travessia é segura. [Créditos das imagens](vision/examples/README.md).

## Maker Lab: robô Acolhe

O robô apoia o acolhimento linguístico com conversa educativa e atividades sobre o ambiente, sempre com mediação de um adulto.

- **Hardware:** Arduino Uno USB, sensor DHT11 adicional, LCD I²C, ponte L298N e dois motores TT (cabeça e braço), sem buzzer e sem PWM.
- **Voz e IA:** microfone → Whisper local → LLM via Ollama com material educativo e telemetria validada → saída de voz no computador. O Uno atualiza o LCD e executa os gestos autorizados.
- **Autonomia:** três leituras válidas de pelo menos 30 °C oferecem uma atividade sobre calor, sem comando manual; rearme abaixo de 28 °C e intervalo mínimo de dois minutos. É regra didática, sem significado clínico.
- **Instalação, componentes, circuito e firmware:** [robot/README.md](robot/README.md). Conferência de requisitos: [docs/maker-entrega.md](docs/maker-entrega.md).
- **Conversa local:** http://127.0.0.1:8080/robo.html. O controle do robô só aceita pedidos deste computador.

## Big Data, RPA e DevSecOps

- **Big Data:** coleta diária no Airflow de duas fontes reais (IBGE e OBMigra) para `chegada/`, lotes de dias diferentes no Volume do Databricks, Bronze incremental com COPY INTO, Prata com MERGE e regras de qualidade com contagem, Ouro dimensional e consultas. [big_data/README.md](big_data/README.md) · [PDF](docs/entregas/GS_BigData_Acolhe.pdf).
- **RPA:** robô em Python que lê o banco do app, aplica regras de consistência e de decisão, registra logs e entrega o resultado ao painel do MVP. [rpa/README.md](rpa/README.md) · [PDF](docs/entregas/GS_RPA_Acolhe.pdf).
- **DevSecOps:** container não root, Terraform no Azure, GitHub Actions com Gitleaks, Semgrep e Trivy a cada push, deploy automático pela `main` via OIDC e registro privado, Grafana com os quatro sinais de ouro. [devsecops/README.md](devsecops/README.md) · [PDF](docs/entregas/GS_DevSecOps_Acolhe.pdf).

## Ficha técnica

- Versão da API: 0.1.0; Python 3.12, biblioteca padrão, SQLite e servidor HTTP.
- Interface: HTML/CSS/JavaScript sem instalação de pacotes; cinco lições PT/ES, síntese de voz do navegador, envio de foto para a visão e service worker.
- Persistência: sessões pseudônimas, tentativas, acertos e idioma por tentativa. Exclusão por sessão; expurgo após sete dias nas operações do banco.
- Integrações: LLM local Qwen2.5 3B com recuperação e agente, detector YOLO treinado, robô físico USB com voz local e simulador, pipeline de dados e RPA.
- Infraestrutura em produção: Azure Container Apps (canadacentral, 0 a 1 réplica, HTTPS, SQLite persistente em Azure Files), criada por Terraform. A imagem Docker (Alpine, usuário não root) passa por GitHub Actions com Gitleaks, Semgrep e Trivy a cada push e vai para um Azure Container Registry privado; o deploy pela `main` é automático, por OIDC. Métricas Prometheus com os quatro sinais de ouro no Grafana. Detalhes em [devsecops/README.md](devsecops/README.md).

## Documentação da entrega

- [Relatório GenAI](docs/entregas/GENAI_RELATORIO.md): modelo, base, comparação, erros e reprodução.
- [Relatório Vision](docs/entregas/VISION_RELATORIO.md) e [PDF](docs/ACOLHE_VISION.pdf): dados, treinamento, comparação de ajustes finos e resultados.
- PDFs de [Big Data](docs/entregas/GS_BigData_Acolhe.pdf), [RPA](docs/entregas/GS_RPA_Acolhe.pdf) e [DevSecOps](docs/entregas/GS_DevSecOps_Acolhe.pdf).
- [Requisitos e diagramas de GenAI e Vision](docs/PRD_GENAI_VISION.md) · [checklist de entregáveis](docs/CHECKLIST_ENTREGAVEIS_GS.md) · [documentação geral](docs/README.md).

## Estrutura do projeto

| Pasta | Conteúdo |
|---|---|
| app | Interface PT/ES, API Python, sessões e atividades em SQLite |
| genai | Base autoral, recuperação, adaptador Ollama, agente e avaliação |
| vision | Treino e inferência, checkpoint entregue, imagens e métricas |
| robot | Robô físico (firmware, DHT11, LCD, gestos), voz local e simulador |
| big_data | DAGs do Airflow, notebooks Databricks, SQL, amostras e evidências |
| rpa | Automação de relatórios, BPMN, logs e evidências |
| devsecops | Terraform, monitoramento, scripts de verificação e evidências |
| bi | Indicadores e proposta de negócio |
| docs | Entregas, roteiros dos vídeos e manuais |

## Verificação técnica

```powershell
.\.venv\Scripts\python.exe -B -m unittest discover -v
node --test tests/frontend.test.cjs tests/robot_frontend.test.cjs
```

Esses testes verificam a implementação; as avaliações dos modelos estão nos relatórios. A mesma suíte roda no GitHub Actions a cada push, junto com os scanners de segurança.

## Operação e limites

Localmente, o servidor escuta em loopback. As atividades usam sessões pseudônimas; o assistente não persiste perguntas e a visão não salva uploads. As lições podem ficar disponíveis offline pelo service worker, mas o assistente e as atividades com API precisam do servidor. Não insira nomes, endereços, fotos de pessoas ou dados de crianças: o protótipo não foi validado para uso autônomo com crianças.

## Vídeos de demonstração

- [GenAI](https://youtu.be/csoYGnIeviM)
- [Computer Vision](https://youtu.be/8FPF_BkSh58)
- Maker, BI e RPA: pendentes.
