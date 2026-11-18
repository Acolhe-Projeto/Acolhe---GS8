# Acolhe

Protótipo acadêmico de acolhimento linguístico em português e espanhol, com atividades educativas de mobilidade e uso acompanhado por uma pessoa adulta.

Equipe: Tomáz Versolato Carballo - RM 551417; Rony Ken Nagai - RM 551549; Aksel Viktor Caminha Rae - RM 99011; Ian Xavier Kuraoka - RM 98860.

## Instalação e execução

Pré-requisitos: Windows, Python 3.12 e Ollama instalado e aberto. A primeira preparação usa internet para instalar as dependências e baixar o Qwen2.5 3B, com aproximadamente 1,9 GB de pesos. O checkpoint Vision de 44 MB já acompanha o clone.

```powershell
git clone --branch feat/genai-vision https://github.com/Acolhe-Projeto/Acolhe---GS8.git
cd Acolhe---GS8
.\scripts\preparar-demo.ps1
.\scripts\iniciar-demo.ps1
```

Abra o endereço exibido no terminal. A porta é escolhida automaticamente a partir de 8080. Após a preparação, também é possível abrir Iniciar-Acolhe.cmd. Encerre o servidor com Ctrl+C.

A inicialização confere o digest da LLM e o hash, as classes e o perfil do detector. Não é necessário treinar novamente para usar os modelos da entrega.

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

O serviço usa o mesmo YOLO26m91 treinado e avaliado, em vision/release/best.pt. O manifesto confere o SHA-256 antes da inferência. No teste básico reservado de 13 fotos, precisão foi 71,2% e recall, 72,2%. No conjunto anterior de 23 fotos, os resultados foram 68,3% e 62,1%; conjuntos diferentes não medem evolução direta. O detector ainda erra e não decide se uma travessia é segura. [Créditos das imagens](vision/examples/README.md).

## Documentação da entrega

- [Relatório GenAI](docs/entregas/GENAI_RELATORIO.md): modelo, base, comparação, erros e reprodução.
- [Relatório Vision](docs/entregas/VISION_RELATORIO.md) e [PDF](output/pdf/ACOLHE_VISION.pdf): dados, treinamento, comparação de ajustes finos e resultados.
- [Requisitos e diagramas](docs/PRD_GENAI_VISION.md): escopo e arquitetura dos dois módulos.
- [Documentação geral](docs/README.md): manual e documentos das demais disciplinas.

## Estrutura do projeto

| Pasta | Conteúdo |
|---|---|
| app | Interface PT/ES, API Python, sessões e atividades em SQLite |
| genai | Base autoral, recuperação, adaptador Ollama, agente e avaliação |
| vision | Treino e inferência, checkpoint entregue, imagens e métricas |
| big_data | Pipeline e consultas de dados; execução externa tem requisitos próprios |
| bi | Indicadores e proposta de negócio |
| rpa | Relatório agregado e automação local |
| robot | Simulador e firmware de referência |
| devsecops | CI, infraestrutura e observabilidade |

## Verificação técnica

```powershell
.\.venv\Scripts\python.exe -B -m unittest discover -v
node --test tests/frontend.test.cjs
```

A última verificação passou em 124 testes Python e 14 Node. Esses testes verificam a implementação; as avaliações dos modelos estão nos relatórios. O ensaio HTTP com os modelos reais está em docs/evidencias/release-delivery-http.json. O clone novo foi conferido com o mesmo checkpoint e as três imagens.

## Operação e limites

O servidor escuta em loopback. O fluxo das atividades usa sessões pseudônimas; o serviço do assistente não persiste perguntas e Vision não salva uploads. O modo de demonstração usa um banco local em docs/qa. As lições podem ser preparadas para leitura offline pelo service worker, mas o assistente e as atividades com API precisam do servidor.

Docker/Compose e o comando python -m app.server executam o MVP básico; as dependências e a configuração das IAs são preparadas pelo fluxo Windows acima. Implantação pública, validação pedagógica, vídeos e envio acadêmico têm etapas próprias. O protótipo não foi validado para uso autônomo com crianças.
