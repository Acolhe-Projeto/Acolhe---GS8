# Vision — vocabulário por objetos

Reconhece 12 classes para apoiar vocabulário PT/ES: mochila, cadeira, livro, garrafa, copo, colher, garfo, tigela, relógio, guarda-chuva, ônibus e semáforo. É uma atividade supervisionada de acolhimento: nomear objetos do cotidiano e do trajeto escolar. Não reconhece rostos, cor do semáforo ou permissão para atravessar. Uploads não são gravados.

## Versão ativa após melhoria

YOLO11n treinado por **80 épocas em CPU, resolução 640**, confiança **0,10** escolhida pela validação. Modelo anterior preservado. No teste histórico: **22TP/21FP/20FN**, recall **52,4%**, precisão **51,2%**; o baseline também calibrado teve recall de 26,2% e precisão de 39,3%. Recall nativo médio por classe54,65% e mAP50 de 62,12% são outra agregação. A meta de 70%/70% ainda não foi atingida.

[Comparação completa](reports/improvement-20261116.json), [calibração](reports/calibration-improved-640-80.json) e [HTTP real: ônibus0,9522](reports/inference-http-improved.json). O novo lote23fotos foi aprovado e avaliado somente como teste local; recall53,0%, precisão48,6%. Nenhuma foto nova entrou no treino.

Para abrir e gravar rapidamente: [guia com comandos e roteiro](../docs/entregas/COMO_USAR_E_GRAVAR.md).

## Teste novo aprovado e congelado

23 fotos novas,66 objetos, autorização explícita do usuário para teste local, sem treino/publicação das fotos. A versão ativa encontrou35 objetos, perdeu31 e gerou37 falsos positivos: recall53,0%, precisão48,6%. Baseline calibrado: recall45,5%, precisão61,2%. Recall melhorou, mas F1/precisão pioraram; a meta principal70%/70% ainda não foi atingida. Mantivemos a configuração escolhida ANTES desse teste. [Saídas e erros por imagem](reports/independent23-frozen.json).

```powershell
python -m vision.reproduce --bundle vision/reports/reproduction-newtest23.json --output vision/data/reproduzido-novo
```

Esse bundle conserva25treino/8validação e substitui somente o teste; não autoriza usar as23 fotos como treino. Reconstrução offline foi executada e auditada. O teste é separado do fine-tuning local, sem alegar independência de todo pré-treinoCOCO. Depois de observá-lo, novos ajustes exigem outro teste final.

## Piloto inicial — histórico

O usuário aprovou o lote v2 de 40 fotos e anotação do ônibus antes do treino. YOLO11n customizado por transferência, 20 épocas, CPU, imgsz320, batch 2, workers 0, seed 42. 25 imagens treino, 8 validação, 7 teste, todas as classes em cada split. Treino ~180s; pico RSS ~737MiB. A stack instalada torch2.15.0+cpu não habilitou a RX6750XT: não alegamos treino GPU nem alteramos drivers. GenAI utilizou GPU por outra stack.

Teste nativo: precisão 0,7258; recall 0,2943; mAP50 0,3878; mAP50-95 0,2964. São medidas de um piloto minúsculo, com classes raras e baixa detecção; quality_validated=false. O avaliador COCO opcional não foi instalado (venv sem pip), mas as métricas nativas foram concluídas. Não confundir as duas avaliações.

[Relatório completo](../docs/entregas/VISION_RELATORIO.md), [PDF final](../output/pdf/ACOLHE_VISION.pdf), [métricas/ambiente](reports/training-20261116.json), [HTTP real: ônibus 0,9326](reports/inference-http-20261116.json), [cinco erros reais](reports/ERROR_ANALYSIS.md).

## Reprodução na raiz

Use Python 3.12 e ambiente isolado. Instale PyTorch conforme o seletor oficial https://pytorch.org/get-started/locally/ e depois vision/requirements.txt. Nesta execução foi usado PyTorch CPU; suporte AMD depende de modelo, sistema e distribuição, não somente VRAM.

```powershell
python -m pip install -r vision/requirements.txt
python -m vision.reproduce --output vision/data/reproduzido
python -m vision.audit --dataset vision/data/reproduzido/dataset.yaml --provenance vision/data/reproduzido/provenance.json
python -m vision.train --dataset vision/data/reproduzido/dataset.yaml --provenance vision/data/reproduzido/provenance.json --epochs 80 --device cpu --imgsz 640 --batch 2 --workers 0 --output vision/artifacts
python -m vision.calibrate --artifacts vision/artifacts --dataset vision/data/reproduzido/dataset.yaml --provenance vision/data/reproduzido/provenance.json --output vision/artifacts/calibration.json --evaluate-test --activate
```

reports/reproduction.json publica URLs, créditos, licenças, hashes, labels e splits, sem bytes das fotografias. O script recusa destinos existentes, fontes não permitidas e hashes diferentes. Reconstrução offline com --cache vision/data/curated-pilot-01 foi executada e produziu fingerprint idêntico. A tentativa de rede parou diante de HTTP429 no Commons; não contornamos a limitação. Se isso ocorrer, aguarde a liberação da fonte e use um destino novo, ou cache local autorizado.

As 39 fotos COCO têm origem/licença individual registrada; o ônibus vem de Wikimedia Commons, Znns, CC-BY4.0. Uma anotação proposta com marcador histórico pending_human permanece no inventário original; a aprovação real posterior do usuário inclui o ônibus e sua caixa, conforme registro exportado. Metadados não substituem a revisão visual de novos lotes.

## Produto

O checkpoint local já está em vision/artifacts/best.pt. Em outro treino, consulte app/server.py e vision/service.py para usar o diretório de artefatos esperado. Inicialize python -B -m app.server, acesse http://127.0.0.1:8080 e selecione PNG/JPEG até8MiB no painel de objetos. POST /api/vision/predict valida upload e não grava imagem. Sem checkpoint próprio válido retorna503; não simula objetos.

Checkpoint ativo SHA256: 5935a4aae2c40282be3f5c41ff9796202d4d6ad4d09333d3e335f709a8936879. O hash b441e149… corresponde ao piloto inicial. Fotografias/pesos permanecem locais e ignorados pelo Git, como combinado na revisão. Curvas/matriz públicas não contêm fotos. A nova clone requer reconstrução e treino para habilitar Vision. Confira licença Ultralytics AGPL/Enterprise antes de distribuir pesos: https://www.ultralytics.com/license.

Testes: python -B -m unittest discover -s vision/tests -v. Testes unitários usam simulações declaradas; a evidência do modelo real está nos relatórios. Faltam vídeo publicado, revisão da equipe e envio no Teams. Mais dados e nova avaliação independente são necessários para qualidade além deste piloto.
