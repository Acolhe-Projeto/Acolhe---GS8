# Checkpoint entregue ao professor

`best.pt` é uma cópia binária exata do YOLO26m91 treinado e avaliado neste projeto. Não é um peso genérico usado no lugar do modelo adaptado. O serviço carrega esta pasta e confere hash, manifesto e ordem das classes antes da inferência.

- Tamanho: 44.036.761 bytes, aproximadamente 44 MB. Incluído no Git comum; não exige Git LFS nem novo treino.
- SHA-256: `3eff4c911170b189d5904b52adde2390f877f0d105a95c092a4b3496653c3bd5`.
- Treino: 91 imagens; cinco épocas concluídas de máximo 12; melhor checkpoint na primeira época.
- Inferência: CPU, imagem 960, confiança 0,25; 12 classes PT/ES.
- Manifesto de distribuição: `model_manifest.json`; a procedência detalhada e os rótulos de reprodução estão em `../reports/reproduction-union91.json`.
- Avaliação: `../reports/finetune117-summary.json`. A continuação com 117 imagens não foi promovida.

Base e implementação: Ultralytics YOLO26m, Ultralytics 8.4.215. O checkpoint derivado é distribuído sob AGPL-3.0, com o texto em `LICENSE-AGPL-3.0.txt`. Código de treino, configuração, fontes dos dados e relatórios estão neste repositório. Fonte e termos do fornecedor: https://www.ultralytics.com/license e https://github.com/ultralytics/ultralytics.

Na nova instalação, siga `../../docs/entregas/COMO_USAR_E_GRAVAR.md`. As três fotos de demonstração estão em `../examples/`; os datasets completos e checkpoints experimentais continuam fora da distribuição.
