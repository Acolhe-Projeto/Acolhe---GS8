# Vision

Detector de 12 objetos cotidianos, com nomes em português e espanhol. O serviço carrega o YOLO26m91 customizado em release/best.pt, conferindo seu SHA-256, manifesto e classes. Inferência em CPU, resolução 960 e confiança 0,25.

## Usar após clonar

Siga a instalação do README da raiz. O checkpoint e três fotos em examples já acompanham o clone; não é necessário treinar novamente. No portal, abra Para educadores → Objetos que ensinam, selecione JPEG/PNG de até 8 MiB e clique Reconhecer objetos. O upload não é salvo.

O [relatório Vision](../docs/entregas/VISION_RELATORIO.md) reúne o treinamento, a comparação de ajustes finos e os resultados; a [versão PDF](../docs/ACOLHE_VISION.pdf) acompanha a entrega. No teste básico reservado de 13 fotos, precisão foi 71,2% e recall, 72,2%. Nas 23 fotos anteriores, mais complexas, foram 68,3% e 62,1%. A amostra é pequena e a origem COCO limita independência em relação ao pré-treino.

## Arquivos

- release: mesmo checkpoint avaliado, manifesto e licença AGPL-3.0.
- examples: três fotos públicas com fontes, autores, licenças e hashes.
- reports/finetune117-summary.json: decisão e resultados finais.
- reports/ft117-reserved13.json: predições do teste reservado.
- reports/reproduction-union91.json e reproduction-union117.json: metadados e rótulos para reconstruir os conjuntos.
- train.py, calibrate.py e audit.py: treinamento, seleção/avaliação e auditoria.

## Refazer o treinamento

A reprodução do treinamento é opcional. Com as dependências instaladas, executar na raiz usando destinos novos:

```powershell
.\.venv\Scripts\python.exe -m vision.reproduce --bundle vision/reports/reproduction-union91.json --output vision/data/reproduzido91
.\.venv\Scripts\python.exe -m vision.audit --dataset vision/data/reproduzido91/dataset.yaml --provenance vision/data/reproduzido91/provenance.json
.\.venv\Scripts\python.exe -m vision.train --dataset vision/data/reproduzido91/dataset.yaml --provenance vision/data/reproduzido91/provenance.json --epochs 12 --patience 4 --base-model yolo26m.pt --freeze 22 --learning-rate 0.00001 --mosaic 0 --device cpu --imgsz 640 --batch 2 --workers 0 --skip-test --output vision/artifacts-reproducao
```

Esses comandos produzem novos artefatos e não substituem o checkpoint entregue. Para nova seleção, usar somente validação, congelar o perfil e avaliar em teste reservado. O relatório registra receitas, hashes e limitações. Respeite os créditos individuais das imagens; os dados completos e pesos experimentais não acompanham a distribuição.
