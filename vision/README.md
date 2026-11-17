# Vision — objetos e vocabulário PT/ES

## Versão ativa

**YOLO26n customizado,80 épocasCPU, resolução 640 e confiança 0,15.** Substituiu YOLO11n por F1 micro de validação 0,4675 versus0,3488, com o mesmo treino 25/validação 8 aprovados. Foram comparadas três bases leves COCO em CPU antes do treino customizado; veja [pesquisa e decisão](../docs/MODELOS_VISION.md).

Nas23 fotos já examinadas, a regressão da versão ativa teve34TP/22FP/32FN: **recall51,5%, precisão60,7%, F1 de 0,5574**. A versãoYOLO11n 80 teve53,0%/48,6%, F1 de 0,5072. Há ganho de precisão/F1 e pequena perda de recall. **Meta70%/70% ainda não atingida; quality_validated=false.** A regressão não é novo teste independente após seleção de arquitetura. Não ajustamos a configuração depois dessas medições.

[Decisão pela validação](reports/yolo26n-custom-decision.json), [regressão por imagem e cinco erros](reports/yolo26n-regression23.json), [HTTP real](reports/inference-http-yolo26n.json), [PDF](../output/pdf/ACOLHE_VISION.pdf). Pesos anteriores20 épocas e YOLO11n 80 estão preservados localmente. O resultado original29,4% era média nativa por classe; não deve ser confundido com recall operacional da versão atual.

## Usar e gravar

Abra Ollama e execute scripts/iniciar-demo.ps1 na raiz. Acesse http://127.0.0.1:8080 → Para educadores → Objetos que ensinam. Selecione PNG/JPEG até8 MiB e clique Reconhecer objetos. Nomes PT/ES e confiança aparecem; o aplicativo não liga câmera, não grava upload e não decide travessias. [Passos completos e roteiro curto](../docs/entregas/COMO_USAR_E_GRAVAR.md).

Sem checkpoint/manifesto válidos, retorna503 explicitamente. O serviço confere hash/classes e parâmetros de inferência. Checkpoint ativo SHA256:007a199a43a6944699c43d26b23e30e5a2e25933b106181ed56a8243aa3b2e31. A GPUAMD usada pelo Ollama não implica treinoGPU no PyTorch instalado; estes treinos e detecção foramCPU. PicoRAM da nova rodada não foi medido.

## Reproduzir em uma nova clone

Python3.12, ambiente isolado, PyTorch conforme https://pytorch.org/get-started/locally/. Instalar vision/requirements.txt usa a versãoUltralytics 8.4.215 realmente testada. Depois, na raiz:

```powershell
python -m vision.reproduce --output vision/data/reproduzido
python -m vision.audit --dataset vision/data/reproduzido/dataset.yaml --provenance vision/data/reproduzido/provenance.json
python -m vision.train --dataset vision/data/reproduzido/dataset.yaml --provenance vision/data/reproduzido/provenance.json --epochs 80 --device cpu --imgsz 640 --batch 2 --workers 0 --base-model yolo26n.pt --output vision/artifacts
python -m vision.calibrate --artifacts vision/artifacts --dataset vision/data/reproduzido/dataset.yaml --provenance vision/data/reproduzido/provenance.json --output vision/artifacts/calibration.json --evaluate-test --activate
```

Escolha diretórios novos: ferramentas recusam sobrescrever datasets/treinos/relatórios. O primeiro bundle reconstrói as 40 fotos iniciais25/8/7; os 25 treino/8val foram preservados na nova rodada. Fotos e pesos não estão no Git; somente clonar não habilita o detector. Pesos oficiais podem ser baixados pela biblioteca durante a preparação. Respeite AGPL3.0/Enterprise da Ultralytics: https://docs.ultralytics.com/models/yolo26/.

## Novo teste e procedência

O usuário aprovou23 fotos novas exclusivamente para teste local. Dataset final56 fotos:25 treino/8val/23 teste, sem mudança nos pixels/caixas/splits de treino/validação. Não houve IDs/bytes em comum entre as 40 originais e 23 novas. A auditoria não detecta similaridade perceptual. Reconstrução offline foi executada com fingerprint 4b18ed3a…:

```powershell
python -m vision.reproduce --bundle vision/reports/reproduction-newtest23.json --output vision/data/reproduzido-novo
```

As novas23 não foram autorizadas para treino ou publicação de fotos. Metadados públicos contêm URLs, créditos, licenças, hashes e rótulos, sem pixels. Um download de referência encontrouHTTP429 no Commons; respeitamos o limite. Se ocorrer, aguarde liberação e use destino novo, ou cache local autorizado com --cache. Não substitua hashes para aceitar outras fotos.

A avaliação inicial das23 foi congelada paraYOLO11n em independent23-frozen.json. A avaliação posteriorYOLO26 é diagnosticada como regressão em conjunto já visto. Para novos ajustes, amplie treino com variedade e reserve outro teste final. A origemCOCO limita alegações de independência do desenvolvimento dos pesos pré-treinados. Mais dados alinhados ao uso educativo são necessários para perseguir70% nas duas métricas.

## Entrega e testes

PDF contém resumo250/objetivo50 palavras, método, exemplos e limites. Faltam revisão da equipe, gravação/publicação do vídeo e envio no Teams. Testes: python -B -m unittest discover -s vision/tests -v. Testes unitários simulam runtime; métricas eHTTP reais estão nos relatórios acima. Não se apresenta teste de contrato como qualidade de modelo.
