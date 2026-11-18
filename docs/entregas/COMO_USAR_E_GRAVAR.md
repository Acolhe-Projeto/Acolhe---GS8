# Abrir, usar e gravar o Acolhe

## Nesta máquina: abrir os dois módulos

1. Abra o aplicativo Ollama e aguarde iniciar.
2. Abra o PowerShell e execute:

```powershell
cd D:\GS2026\Acolhe---GS8
.\scripts\iniciar-demo.ps1
```

3. Mantenha o terminal aberto e copie o endereço **Acolhe:** impresso nele. O script usa a primeira porta livre a partir de 8080; a verificação atual nesta máquina usou http://127.0.0.1:8084.
4. Para escolher outra faixa, rode `.\scripts\iniciar-demo.ps1 -Porta 8090`. Ele verifica11portas a partir da indicada; use o endereço que o terminal imprimir. Duas instâncias não podem mais compartilhar a mesma porta no Windows.

Esse comando habilita Qwen3B local com offload automático de GPU e memória aquecida por dois minutos. O detector usa CPU. A primeira pergunta pode demorar mais. Encerrar o servidor não encerra o aplicativo Ollama.

## Usar GenAI

1. Clique em **Caminho seguro** no menu ou vá até **Uma dúvida no caminho?**.
2. Digite **Como atravessar a rua com segurança?** e clique em **Perguntar ao ajudante**.
3. Mostre resposta, fonte e aviso fixo sobre acompanhamento de adulto. O aviso é uma política fixa do aplicativo, separado da resposta do modelo.
4. No seletor de idioma do topo, escolha **Español**. Pergunte **¿Qué hago si estoy perdido?**.
5. Volte a Português e pergunte **Qual é a previsão de chuva amanhã?**. Essa informação não está na base: o sistema deve recusar. Essa recusa é uma guarda do aplicativo, não uma previsão feita pelo modelo.

Se aparecer **retrieval_only**, o servidor foi iniciado sem a variável do modelo: encerre e use o script acima. Se houver recusa por indisponibilidade, confira se Ollama está aberto e rode `.\.venv\Scripts\python.exe -B -m genai.local`. Não apresente texto curado como geração por LLM.

## Roteiro GenAI: aproximadamente 90 segundos

| Na tela | Fala curta |
|---|---|
| Página inicial | “Este é o Acolhe. Usamos uma IA local para apoiar português e espanhol e orientações educativas de mobilidade.” |
| Pergunta de travessia e resposta | “O Qwen de três bilhões de parâmetros consulta nossa base. A interface mostra a fonte e um aviso fixo para procurar um adulto.” |
| Trocar para espanhol e perguntar sobre estar perdido | “A mesma aplicação também responde em espanhol.” |
| Perguntar sobre chuva | “Quando a informação não existe na base ou está fora do escopo, o aplicativo recusa.” |
| Abrir GENAI_RELATORIO.md no GitHub, no placar atual v6/D16 | “Comparamos o mesmo modelo sem contexto, com RAG e com agente. Na revisão técnica dos dezesseis casos atuais, tivemos sete, quatorze e quatorze acertos. Ainda existem duas falhas de recuperação; a revisão humana está pendente.” |

RAG significa gerar uma resposta consultando documentos. Não diga que está tudo correto: ainda existem erros de idioma, intenção e omissão. Não houve LoRA; o critério permite agente. Não precisa mostrar treinamento ou código inteiro na gravação.

## Usar Vision

1. Clique em **Para educadores** e procure **Objetos que ensinam**.
2. Confira se o modelo está pronto. O diagnóstico técnico também está em /api/vision/status no mesmo endereço/porta indicado pelo terminal.
3. Clique para selecionar uma foto e cole este caminho na barra de endereço da janela de arquivos:

```text
D:\GS2026\Acolhe---GS8\vision\examples
```

4. Selecione **01-onibus.jpg** e clique em **Reconhecer objetos**. O resultado esperado é **ônibus / autobús**.
5. Repita com **02-mesa-garfo-tigela.jpg**. O resultado esperado é **garfo / tenedor**, **tigela / cuenco** e **colher / cuchara**.
6. Mostre os nomes PT/ES, caixas e confiança. As duas fotos tiveram detecções confirmadas na última verificação local; são exemplos de demonstração. O número de confiança não é garantia de acerto. Se houver falha, mostre e explique a limitação.

Opcional: use **03-copo-cadeira.jpg**, na mesma pasta, para experimentar uma cena mais difícil; cadeiras / sillas foram detectadas no ensaio da entrega. Não prometa detectar todos os objetos dessa cena. Também é possível enviar uma foto própria PNG/JPEG, até 8 MiB, sem pessoas ou dados pessoais. A câmera não é ligada e o servidor não salva o upload.

As três fotos acompanham o clone em `vision/examples/`. Em outra máquina, use a pasta equivalente dentro do clone, sem depender de D:\GS2026. Créditos e licenças: ônibus — Znns, CC BY 4.0; mesa — jules, CC BY 2.0; cena de cadeiras — liz west, CC BY 2.0. Fontes e hashes estão em `vision/examples/credits.json`; preserve a atribuição na gravação.

## Roteiro Vision: aproximadamente um minuto

1. “Aqui identificamos objetos e mostramos o nome em português e espanhol.” Selecione **01-onibus.jpg**, na pasta indicada acima, e clique em **Reconhecer objetos**. Mostre **ônibus / autobús** no resultado real.
2. Envie **02-mesa-garfo-tigela.jpg** e mostre as detecções reais de garfo, tigela e colher. “Este detector YOLO26m recebeu treinamento customizado com imagens públicas revisadas, usando transferência de aprendizado.”
3. Abra o relatório Vision e mostre a tabela da versão ativa. “O YOLO26m foi adaptado com 91 fotos de treino e selecionado pela validação. Nas 23 fotos já examinadas, o diagnóstico teve recall de 62,1% e precisão de 68,3%. No novo lote básico de 13 fotos reservado, tivemos precisão de 71,2% e recall de 72,2%. É um conjunto diferente e pequeno; o modelo ainda erra.” Não apresente esse diagnóstico posterior como novo teste cego.
4. “É um piloto pequeno, com erros documentados. Não identifica rostos nem decide se uma travessia é segura.”

Os PRDs e relatórios explicam os dados, arquitetura, teste e falhas. O roteiro curto demonstra funcionamento; os documentos fornecem o restante da evidência solicitada pelo PDF.

## Em outra máquina: preparação inicial

```powershell
git clone --branch feat/genai-vision https://github.com/Acolhe-Projeto/Acolhe---GS8.git
cd Acolhe---GS8
.\scripts\preparar-demo.ps1
.\scripts\iniciar-demo.ps1
```

Pré-requisitos: Python 3.12 e Ollama instalado e aberto. A preparação cria .venv, instala dependências Vision e baixa o Qwen3B (~1,9 GB) uma vez; requer internet nessa etapa. Confere o digest exato da LLM, o SHA-256 do detector e as classes. O mesmo checkpoint Vision já acompanha o clone em vision/release/best.pt, com manifesto e licença; as três fotos estão em vision/examples. Não é necessário treinar para testar. As dependências e o modelo LLM podem ocupar vários GB adicionais. Se a tag upstream mudar, a verificação recusa o digest diferente em vez de substituir silenciosamente a versão avaliada.

## Gravar rapidamente no OBS, se usar essa ferramenta

1. Abra o OBS e mantenha o navegador do Acolhe aberto.
2. Em Fontes, adicione Captura de janela e selecione a janela do navegador. Confira a prévia e evite capturar conversas, senhas ou outras abas.
3. Confira se o microfone aparece no medidor de áudio e faça um ensaio curto para ouvir a gravação.
4. Clique em Iniciar gravação, siga o roteiro acima e termine em Parar gravação.
5. Abra o arquivo gravado para conferir voz, resposta/fonte e imagem legíveis antes de publicar. Não precisa mostrar webcam.

Guia oficial do OBS: https://obsproject.com/kb/quick-start-guide. Gravação é local; iniciar OBS não publica o vídeo automaticamente.

## Depois da gravação

Publique os vídeos em destino da equipe, confira acesso sem login e insira URLs reais nos relatórios. Regenere o PDF se alterar seu conteúdo. Um integrante envia na disciplina correta no Teams até19/11 às23h55, conferindo o horário do ambiente FIAP. Não há envio ou publicação automática de vídeos por este script.
