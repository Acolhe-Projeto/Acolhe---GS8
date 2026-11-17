# Demonstrações e envio

Não há vídeo gravado/publicado ainda. Este roteiro usa a solução real disponível localmente; substituir PENDENTE nos relatórios somente por URL real conferida sem login. A equipe escolhe a duração: a página44 não fixa duração de vídeo.

## Preparar

Na raiz, iniciar Ollama, definir ACOLHE_OLLAMA_MODEL=qwen2.5:3b-instruct e ACOLHE_OLLAMA_NUM_GPU=-1, depois python -B -m app.server. Abrir http://127.0.0.1:8080 (ou a porta configurada). Checkpoint Vision local em vision/artifacts/. Usar somente fotos aprovadas locais e perguntas fictícias. Antes de publicar vídeo com uma foto, revisar concretamente enquadramento/crédito/licença e autorizar sua exibição: a aprovação anterior cobriu treino local, não publicação das fotos.

## Vídeo GenAI — fala e sequência

1. Identificar produto e equipe. “O Acolhe apoia acolhimento PT/ES e orientação educativa de mobilidade com um adulto responsável.”
2. Mostrar o diagrama do relatório: pergunta → guardas → busca em oito microlições → Qwen3B → JSON com fonte → interface. Explicar RAG como geração com consulta à base.
3. Fazer pergunta real de travessia em PT; mostrar resposta, fonte e aviso fixo. Trocar para ES e perguntar como pedir ajuda ao se perder. Perguntar detalhe que não consta na base e mostrar recusa efetiva. Se houver erro, explicar o erro, sem editar a gravação para simular sucesso.
4. Abrir placar dev20/holdoutC12 e os rastros do agente. Explicar que o mesmo modelo foi comparado sem contexto, com RAG e com agente retrieve/refuse; não houve LoRA.
5. Mostrar cinco erros reais e limitações. “Os números de conteúdo são uma revisão técnica exploratória, ainda não avaliação humana cega. O modelo pode errar idioma e omitir instruções.”
6. Mostrar repositório/README/comandos/notebooks com outputs e concluir com revisão humana pendente.

## Vídeo Vision — fala e sequência

1. “A câmera/foto serve para identificar nomes de objetos em português/espanhol. O detector não decide atravessar nem identifica rostos.” Upload explícito, sem solicitar câmera.
2. Mostrar12 classes, procedência, aprovação do lote, splits25/8/7, seed42 e treino20 épocas. Explicar transferência YOLO11n; dizer CPU, ~3min, e por que não foi alegada GPU nesta stack.
3. Mostrar status pronto no aplicativo. Com autorização específica para exibição/publicação, carregar a foto de ônibus aprovada; resultado registrado de referência: ônibus/autobús,0,9326. Uma nova execução pode variar.
4. Mostrar matriz, precisão0,7258, recall0,2943, mAP500,3878. “Em40 fotos, esse piloto perde muitos objetos. Não é detector validado para uso real.” Mostrar cinco falhas por classe no relatório.
5. Mostrar ausência de armazenamento pelo serviço e caminho de reprodução. Não apresentar testes com runtime simulado como inferência real.

## Fechamento pela equipe

- Conferir nomes/RMs, adequação do texto e revisão de respostas nas fichas avaliacao/*.review.md; não preencher aprovação automática.
- Gravar, revisar e publicar os dois vídeos em destino da equipe; conferir links em janela sem autenticação e acesso durante correção.
- Inserir URLs reais nos relatórios e rebuildar o PDF Vision com docs/entregas/build_vision_pdf.py; conferir visualmente o PDF alterado.
- GenAI: entregar link da branch, relatório, base/, avaliacao/, notebooks com saídas, README/API e vídeo.
- Vision: entregar PDF final, link da branch e vídeo demonstrando o detector customizado funcionando.
- Um integrante envia no Teams de cada disciplina até19/11/2026 às23h55, conferindo o horário mostrado pelo ambiente. Guardar comprovante de envio.

O sistema não pode certificar nota, aprovação pedagógica nem submissão no Teams enquanto essas ações não ocorrerem.
