# Visão: vocabulário por objetos

O módulo reconhece 12 classes para ensinar vocabulário PT/ES: mochila, cadeira, livro, garrafa, copo, colher, garfo, tigela, relógio, guarda-chuva, ônibus e semáforo. Semáforo é somente o nome do objeto: não determina cor, travessia ou rota segura. Não há reconhecimento facial nem gravação de uploads.

## Estado em 2026-11-16

Implementados: contrato de inferência, tradução, verificação de checkpoint, preparação COCO → YOLO, auditoria do dataset antes do treino, opções de CPU e registro de métricas globais/por classe do teste. O plano e os critérios de aceite estão em [PLAN.md](PLAN.md).

**Não executados: curadoria de fotografias reais, treinamento, inferência YOLO real e métricas de qualidade.** O repositório não contém imagens, anotações COCO ou pesos. Sem checkpoint próprio, o serviço continua indisponível; não apresenta detecções fictícias. Os testes usam imagens sintéticas temporárias e runtime simulado para testar contratos, sem evidência de qualidade de modelo.

## Preparar os dados sem instalar a stack de treino

Na raiz do repositório:

```powershell
python -m venv vision/.venv
vision/.venv/Scripts/python.exe -m pip install -r vision/requirements-data.txt
vision/.venv/Scripts/python.exe -B -m unittest discover -s vision/tests -v
```

As avaliações [COCO](COCO_ASSESSMENT.md) e [Open Images](OPEN_IMAGES_ASSESSMENT.md) são registros históricos de outra máquina; seus arquivos externos e hardware não foram transferidos para este clone. COCO preserva as 12 classes. Uma licença declarada no dataset não substitui a verificação da fotografia original.

1. Obter localmente as anotações COCO e somente as imagens escolhidas, ou produzir fotos próprias autorizadas. A ferramenta não baixa nada.
2. Inspecionar cada imagem; excluir cenas identificáveis de crianças. Registrar imagem original, autor, licença, data da revisão, hash SHA-256 e confirmação de revisão de privacidade. As declarações precisam corresponder a evidências verificáveis guardadas localmente.
3. Definir splits por imagem original antes de recortes/augmentations, por exemplo 70/15/15 com seed 42. Distribuir as 12 classes em **cada** split; não duplicar fotos para preencher classes faltantes. O conversor respeita o split declarado no inventário e não decide licenças nem faz revisão visual automaticamente.
4. Copiar `vision/data/provenance.example.json` para um arquivo local, preencher os campos gerais e criar uma entrada em `images` para cada fotografia. `image_id` é o ID COCO como texto; `split` é `train`, `val` ou `test`. Para o conversor, `file` é preenchido na saída. `real_images` e `privacy_reviewed` só podem ser verdadeiros depois da revisão humana.

```powershell
vision/.venv/Scripts/python.exe -m vision.prepare --annotations vision/data/instances_train2017.json --images vision/data/originals --reviews vision/data/reviews.json --output vision/data/curated-01
vision/.venv/Scripts/python.exe -m vision.audit --dataset vision/data/curated-01/dataset.yaml --provenance vision/data/curated-01/provenance.json
```

O conversor valida dimensões originais e caixas COCO, remapeia classes para 0..11, preserva créditos e separa imagens/labels. Recusa caixas crowd, fotografias sem revisão, classes incompletas e destinos existentes. A saída só aparece quando toda a auditoria passa: `dataset.yaml`, `provenance.json`, `audit.json`, `images/{train,val,test}` e `labels/{train,val,test}`.

A auditoria verifica imagens legíveis, limite de 20 megapixels, inventário exato, hashes, ausência de duplicatas binárias, caixas YOLO normalizadas e todas as classes por split. Também recusa caminhos fora da raiz e diretivas de download. O fingerprint incorpora os bytes de imagens e labels. Não detecta cópias recortadas/recomprimidas nem confirma direitos autorais ou privacidade por si só; essa revisão continua humana. Um único exemplo por classe passa o teste estrutural, mas não basta para avaliar qualidade.

## Treinar um piloto em CPU

Foi mantido **YOLO11n**, a variante nano já prevista na base, para evitar migração desnecessária. Defaults: `device=cpu`, `imgsz=320`, `batch=2`, `workers=0`, sem cache de imagens em RAM. São parâmetros de baixo consumo inicial, não garantia de velocidade. Treino em CPU pode demorar; medir tempo/RAM no piloto antes de aumentar o dataset ou épocas. A resolução menor pode prejudicar objetos pequenos, principalmente semáforos.

A stack completa é opcional. Instale a versão CPU do PyTorch indicada no [seletor oficial](https://pytorch.org/get-started/locally/) e depois:

```powershell
vision/.venv/Scripts/python.exe -m pip install -r vision/requirements.txt
vision/.venv/Scripts/python.exe -m vision.train --dataset vision/data/curated-01/dataset.yaml --provenance vision/data/curated-01/provenance.json --epochs 1 --device cpu --imgsz 320 --batch 2 --workers 0 --output vision/artifacts-pilot-01
```

Uma época testa a execução; **não valida qualidade nem cumpre sozinha o treinamento da disciplina**. Depois do piloto, ajustar épocas somente com treino/validação; reservar o teste final. Ultralytics pode baixar `yolo11n.pt` na primeira execução. Revisar a [licença AGPL/Enterprise](https://www.ultralytics.com/license) antes de distribuição; uso acadêmico não implica isenção automática.

O script audita antes de importar Ultralytics e obter pesos. Salva `best.pt`, `model_manifest.json`, YAML com raiz absoluta e checklist `error_analysis.md`, sem reutilizar artefatos existentes. A avaliação usa `split=test`, gera plots/JSON na pasta indicada em `evaluation_directory` e registra precisão, recall, mAP50/mAP50-95 por classe e globais. Os resultados são calculados pelo runtime real, nunca preenchidos por testes. Guarde a pasta completa de avaliação para a matriz de confusão e revisão das predições.

## Usar no serviço

`status()` verifica manifesto, treino real declarado, ordem das classes, hash do checkpoint, dependências e carregamento YOLO. `quality_validated` permanece falso: carregar pesos não comprova qualidade. `predict(bytes)` limita upload a 8 MiB/20 megapixels, usa CPU/resolução 320/confiança 0,5, retorna classes/caixas/traduções e não salva imagens. Imagens inválidas geram `ValueError`; checkpoint ausente/inválido gera `ModelUnavailable`.

A PWA oferece seleção de imagem e resultado PT/ES. `POST /api/vision/predict` recebe os bytes da imagem PNG/JPEG diretamente no corpo HTTP, até 8 MiB, e retorna JSON. Sem checkpoint, responde HTTP 503; não é inferência simulada. `GET /api/vision/status` informa a disponibilidade. O envio não usa multipart nem base64 e não persiste a imagem.

O destino padrão de treino é `vision/artifacts`, lido pelo serviço. Para experimentar sem alterar o modelo servido, use `--output vision/artifacts-pilot-01`. Promover o resultado ao caminho padrão exige revisão humana de métricas e de erros; não trate um piloto como aprovado. Use somente checkpoints locais próprios e confiáveis.

## Evidências para a entrega

- Inventário de imagens/caixas por classe e split, créditos, hashes, método de separação e limites da curadoria.
- Comando, ambiente, versões, seed, duração/RAM e checkpoint com hash.
- Curvas, matriz de confusão e precisão/recall/mAP por classe sobre teste reservado.
- Pelo menos cinco erros reais, se ocorrerem: image_id, classe esperada/predita, condição (luz, oclusão, tamanho), hipótese e ação. Se não houver cinco, registrar quantos foram encontrados; não inventar erros.
- Demonstração PT/ES, ausência de modelo, arquivo inválido e nenhum objeto encontrado. Revisão de segurança e pedagógica antes de qualquer uso real.

Validação nesta alteração: 21 testes de visão passaram em ambiente isolado com Pillow/PyYAML, sem torch/YOLO instalado e sem downloads de pesos/dataset. Referências técnicas: [treino e parâmetros](https://docs.ultralytics.com/modes/train/), [validação](https://docs.ultralytics.com/modes/val/), [formato YOLO](https://docs.ultralytics.com/datasets/detect/) e [YOLO11](https://docs.ultralytics.com/models/yolo11/).
