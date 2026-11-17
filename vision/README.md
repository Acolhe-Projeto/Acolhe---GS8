# Vision — objetos e vocabulário PT/ES

## Versão ativa

**YOLO26m91**, treinado com 91 fotos, cinco épocas concluídas (máximo 12), melhor checkpoint selecionado pela validação. Treino em CPU / 640. **Inferência em 960, confiança 0,25**, cerca de 22 milhões de parâmetros e 44 MB de pesos.

O fine-tuning adicional com 117 fotos concluiu sete épocas, mas não superou o M91 na mesma validação de 38 fotos; não foi promovido. O perfil retido teve P72,7% / R71,5% na validação e **P71,2% / R72,2% no novo teste básico reservado de 13 fotos e 72 objetos**: 52 TP, 21 FP, 20 FN. A meta conjunta foi observada nesse lote pequeno. Não comprova desempenho geral nem independência de todo pré-treino COCO.

Nas 23 fotos mais complexas anteriores, o mesmo M91 teve P68,3% / R62,1%; elas não foram reavaliadas na rodada final. Conjuntos distintos não são evolução direta do modelo. quality_validated=false; ainda há erros e classes fracas. A métrica suplementar de 12/13 imagens com um alvo primário correto não é precisão/recall global.

[Plano completo](../docs/entregas/VISION_FINETUNING.md), [decisão final antes do teste](reports/finetune117-decision.json), [teste reservado com dados brutos](reports/ft117-reserved13.json), [resumo](reports/finetune117-summary.json) e [PDF](../output/pdf/ACOLHE_VISION.pdf). Pesos e fotos permanecem locais. Checkpoint ativo: 3eff4c911170b189d5904b52adde2390f877f0d105a95c092a4b3496653c3bd5. Nano anterior em artifacts-yolo26n-before-ft91; candidato adicional em artifacts-ft117-medium, sem implantação.

## Usar nesta máquina

Abra Ollama e execute scripts/iniciar-demo.ps1 na raiz. Use o endereço que o terminal imprimir, pois a porta é escolhida automaticamente. Em Para educadores → Objetos que ensinam, selecione PNG/JPEG até 8 MiB e clique Reconhecer objetos. O aplicativo não liga câmera, não grava o upload nem decide travessias. As duas fotos do roteiro estão em docs/qa/testar. A demonstração HTTP local teve mediana de 0,955 segundo em cinco repetições do ônibus; não é benchmark geral.

## Reproduzir em uma clone nova

Instale Python 3.12, PyTorch adequado à máquina e vision/requirements.txt. A versão usada foi Ultralytics 8.4.215 e PyTorch 2.15.0+cpu. Na raiz, usando destinos que ainda não existam:

```powershell
python -m vision.reproduce --bundle vision/reports/reproduction-union91.json --output vision/data/reproduzido91
python -m vision.audit --dataset vision/data/reproduzido91/dataset.yaml --provenance vision/data/reproduzido91/provenance.json
python -m vision.train --dataset vision/data/reproduzido91/dataset.yaml --provenance vision/data/reproduzido91/provenance.json --epochs 12 --patience 4 --base-model yolo26m.pt --freeze 22 --learning-rate 0.00001 --mosaic 0 --device cpu --imgsz 640 --batch 2 --workers 0 --skip-test --output vision/artifacts
python -m vision.calibrate --artifacts vision/artifacts --dataset vision/data/reproduzido91/dataset.yaml --provenance vision/data/reproduzido91/provenance.json --imgsz 960 --confidence 0.25 --output vision/reports/NOVO-calibration.json --activate
```

A confiança explícita reproduz o perfil decidido no desenvolvimento, não seleciona pela avaliação de teste. Para uma nova seleção, repita o protocolo com validação e congele a decisão antes do teste. Variações de ambiente podem alterar os resultados; confira versões e hashes. Somente clonar não habilita o detector: os dados precisam ser reconstruídos e os pesos treinados localmente. Respeite AGPL 3.0/Enterprise e licenças individuais das fotos. Se a fonte limitar requisições, aguarde ou use cache autorizado com --cache; não substitua hashes.

## Comparar continuação de checkpoints

```powershell
python -m vision.merge_approved --sources vision/data/curated-pilot-01 vision/data/curated-train70-val20-test23 --heldout vision/data/curated-train70-val20-test23 --output vision/data/NOVA-uniao
python -m vision.train --dataset vision/data/NOVA-uniao/dataset.yaml --provenance vision/data/NOVA-uniao/provenance.json --base-model yolo26n.pt --initial-artifacts vision/artifacts-yolo26n-before-ft91 --epochs 30 --patience 8 --freeze 10 --learning-rate 0.00005 --mosaic 0 --imgsz 640 --batch 2 --workers 0 --device cpu --skip-test --output vision/artifacts-NOVO-finetuning
```

initial-artifacts exige um checkpoint local com hash, classe e modelo conferidos. Inicia nova execução a partir dos pesos, sem retomar o otimizador. optimizer=auto ignorava a taxa manual: agora AdamW, warmup e taxa são explícitos. O modelo novo precisa ser comparado na mesma validação, incluindo resultados por classe; mais épocas não são garantia de ganho. A versão instalada remapeia saídas compatíveis por nome de classe ao transferir os pesos oficiais.

## Dados e limites

União aprovada: 91 treino / 27 validação / 23 teste, com 613 / 247 / 66 objetos. Fingerprint abb33444…; reconstrução offline conferida. Sem duplicatas binárias; triagem perceptual heurística sem candidatos no limite usado. Fotos relacionadas por cena podem escapar da triagem. Não movimentamos teste para treino.

As 23 fotos já foram expostas em rodadas anteriores, e imagens COCO podem ter participado do desenvolvimento dos pesos-base. Esses números não são avaliação independente nem eficácia pedagógica. A emenda que priorizou equilíbrio entre precisão e recall foi feita após resultados de desenvolvimento e antes da regressão; não estava no registro original.

O lote de 50 fotos foi aprovado e incorporado à comparação 117 treino / 38 validação / 13 teste reservado. A coleta respeitou HTTP 429; metas originais não foram alcançadas. O modelo ativo não foi treinado nas 50 novas fotos porque o candidato117 não trouxe ganho suficiente.

Para reproduzir a avaliação final, reconstrua também reproduction-union117.json e avalie o modelo M91 no perfil congelado; não confunda o conjunto experimental117 com os91exemplos de treino dos pesos servidos:

```powershell
python -m vision.reproduce --bundle vision/reports/reproduction-union117.json --output vision/data/reproduzido117
python -m vision.calibrate --artifacts vision/artifacts --dataset vision/data/reproduzido117/dataset.yaml --provenance vision/data/reproduzido117/provenance.json --imgsz 960 --confidence 0.25 --output vision/reports/NOVO-teste13.json --evaluate-test
```

Não reajuste o perfil a partir do teste. A grade densa (--dense-grid) é apenas para escolher confiança na validação antes de congelar uma nova decisão.


Histórico: bundles reproduction.json, reproduction-newtest23.json e reproduction-train70.json; relatórios anteriores preservados no Git. Faltam revisão final da equipe, vídeo publicado, links e envio no Teams.

Testes: python -B -m unittest discover -s vision/tests -v. Testes unitários usam fixtures; métricas reais são os relatórios de inferência e treino citados.
