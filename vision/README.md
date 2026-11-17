# Vision — vocabulário por objetos

Reconhece 12 classes para apoiar vocabulário PT/ES: mochila, cadeira, livro, garrafa, copo, colher, garfo, tigela, relógio, guarda-chuva, ônibus e semáforo. É uma atividade supervisionada de acolhimento: nomear objetos do cotidiano e do trajeto escolar. Não reconhece rostos, cor do semáforo ou permissão para atravessar. Uploads não são gravados.

## Resultado executado

O usuário aprovou o lote v2 de 40 fotos e anotação do ônibus antes do treino. YOLO11n customizado por transferência, 20 épocas, CPU, imgsz320, batch2, workers0, seed42. 25 imagens treino, 8 validação, 7 teste, todas as classes em cada split. Treino ~180s; pico RSS ~737MiB. A stack instalada torch2.15.0+cpu não habilitou a RX6750XT: não alegamos treino GPU nem alteramos drivers. GenAI utilizou GPU por outra stack.

Teste nativo: precisão 0,7258; recall 0,2943; mAP50 0,3878; mAP50-95 0,2964. São medidas de um piloto minúsculo, com classes raras e baixa detecção; quality_validated=false. O avaliador COCO opcional não foi instalado (venv sem pip), mas as métricas nativas foram concluídas. Não confundir as duas avaliações.

[Relatório completo](../docs/entregas/VISION_RELATORIO.md), [PDF final](../output/pdf/ACOLHE_VISION.pdf), [métricas/ambiente](reports/training-20261116.json), [HTTP real: ônibus 0,9326](reports/inference-http-20261116.json), [cinco erros reais](reports/ERROR_ANALYSIS.md).

## Reprodução na raiz

Use Python 3.12 e ambiente isolado. Instale PyTorch conforme o seletor oficial https://pytorch.org/get-started/locally/ e depois vision/requirements.txt. Nesta execução foi usado PyTorch CPU; suporte AMD depende de modelo, sistema e distribuição, não somente VRAM.

```powershell
python -m pip install -r vision/requirements.txt
python -m vision.reproduce --output vision/data/reproduzido
python -m vision.audit --dataset vision/data/reproduzido/dataset.yaml --provenance vision/data/reproduzido/provenance.json
python -m vision.train --dataset vision/data/reproduzido/dataset.yaml --provenance vision/data/reproduzido/provenance.json --epochs 20 --device cpu --imgsz 320 --batch 2 --workers 0 --output vision/artifacts
```

reports/reproduction.json publica URLs, créditos, licenças, hashes, labels e splits, sem bytes das fotografias. O script recusa destinos existentes, fontes não permitidas e hashes diferentes. Reconstrução offline com --cache vision/data/curated-pilot-01 foi executada e produziu fingerprint idêntico. A tentativa de rede parou diante de HTTP429 no Commons; não contornamos a limitação. Se isso ocorrer, aguarde a liberação da fonte e use um destino novo, ou cache local autorizado.

As 39 fotos COCO têm origem/licença individual registrada; o ônibus vem de Wikimedia Commons, Znns, CC-BY4.0. Uma anotação proposta com marcador histórico pending_human permanece no inventário original; a aprovação real posterior do usuário inclui o ônibus e sua caixa, conforme registro exportado. Metadados não substituem a revisão visual de novos lotes.

## Produto

O checkpoint local já está em vision/artifacts/best.pt. Em outro treino, consulte app/server.py e vision/service.py para usar o diretório de artefatos esperado. Inicialize python -B -m app.server, acesse http://127.0.0.1:8080 e selecione PNG/JPEG até8MiB no painel de objetos. POST /api/vision/predict valida upload e não grava imagem. Sem checkpoint próprio válido retorna503; não simula objetos.

Checkpoint SHA256: b441e1490d6bbcb0aa173aca4589fc809ed6f42c263ee559c8424466413914a1. Fotografias/pesos permanecem locais e ignorados pelo Git, como combinado na revisão. Curvas/matriz públicas não contêm fotos. A nova clone requer reconstrução e treino para habilitar Vision. Confira licença Ultralytics AGPL/Enterprise antes de distribuir pesos: https://www.ultralytics.com/license.

Testes: python -B -m unittest discover -s vision/tests -v. Testes unitários usam simulações declaradas; a evidência do modelo real está nos relatórios. Faltam vídeo publicado, revisão da equipe e envio no Teams. Mais dados e nova avaliação independente são necessários para qualidade além deste piloto.
