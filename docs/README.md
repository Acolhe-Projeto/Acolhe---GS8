# Documentação Acolhe

## Arquivos para leitura

- [PRD GenAI/Vision](PRD_GENAI_VISION.md): escopo desta branch, diagramas, lacunas e critérios de aceite.
- [Validação GenAI/Vision](VALIDACAO_GENAI_VISION.md): execução e limites das evidências desta branch.
- [Conhecimento Graphify](knowledge/README.md): mapa de todas as disciplinas, cobertura, consultas e vault Obsidian.
- [Checklist da entrega](ENTREGA_CHECKLIST.md): critérios oficiais e pendências de revisão, vídeos e envio.
- [Usar e gravar](entregas/COMO_USAR_E_GRAVAR.md): preparação após clonar, frases, três fotos incluídas e roteiro curto.
- [Relatório GenAI](entregas/GENAI_RELATORIO.md): Qwen3B, comparação baseline/RAG/agente e limites.
- [Resultados Vision](entregas/VISION_FINETUNING.md): modelo mantido, comparação 91/117 fotos e teste reservado.

- `manual_acolhe.pdf`: manual diagramado com capa, logo original, equipe, sumário navegável, onze capítulos e páginas numeradas.
- `manual_acolhe.md`: fonte editável do conteúdo do manual.
- `registro_testes.md`: modelo de registro de evidências; campos não preenchidos não são resultados.
- `roteiros_videos.md`: roteiros técnicos RPA (até 3 minutos) e Maker (até 6 minutos).
- `../bi/roteiro_pitch.md`: roteiro BI (até 5 minutos) e lacunas de validação do negócio.
- `../bi/indicadores.md`: definições, denominadores e limites dos indicadores.

Os READMEs e as evidências dos módulos registram o estado atual da implementação. O manual descreve operação e critérios de validação; não substitui as evidências específicas exigidas por cada disciplina.

## Atualizar o PDF

Edite `manual_acolhe.md`, preserve a estrutura numerada e execute `python docs/build_pdf.py` a partir da raiz. O gerador usa ReportLab, PyMuPDF e as fontes Arial do Windows. As bibliotecas foram instaladas isoladamente em `docs/.deps`; não mudam as dependências do MVP.

Para recriar o ambiente de documentação em outra máquina Windows:

`python -m pip install --target docs/.deps reportlab pymupdf`

Após gerar, revise visualmente todas as páginas em `docs/qa/`, confira o sumário e os números de página, nomes, RMs e requisitos. Essas imagens são intermediários de controle de qualidade e não precisam ir para a entrega.

O DOCX não foi produzido nesta execução. A fonte editável disponível é Markdown; o PDF foi gerado diretamente e não deve ser descrito como Word editável.

## Publicação e cuidado com os arquivos

Não versionar `docs/.deps/` e `docs/qa/`. O `.gitignore` exclui essas pastas; o `.dockerignore` também as exclui do contexto de build, junto com datasets locais, bancos e pesos experimentais. A entrega tem exceções explícitas para o checkpoint escolhido em vision/release e as três fotos creditadas em vision/examples. Configuração de acesso remoto e cadastro em serviços externos não fazem parte da documentação do projeto e devem ficar fora do clone. Não incluir bancos ou evidências com dados pessoais reais. Antes de publicar, conferir as permissões e os requisitos da disciplina.

O manual é apoio geral. Maker exige documentação oficial pelo GitHub, não substituída pelo PDF. Big Data, Visão e RPA exigem seus relatórios e evidências próprios. O pitch BI exige vídeo no YouTube como não listado, com link testado em janela anônima e MVP na URL pública.
