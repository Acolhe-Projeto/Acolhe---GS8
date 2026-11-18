> Estado atual em 17/11: Vision usa YOLO26m treinado com 91 fotos, em 960/confiança 0,25. O candidato com 117 fotos não foi promovido. No teste básico reservado de 13 fotos, precisão 71,2% e recall 72,2%; a meta foi observada apenas nesse lote pequeno. Este documento preserva a pesquisa histórica das bases nano. Resultados atuais em [VISION_FINETUNING](entregas/VISION_FINETUNING.md).

# Bases leves para Vision — pesquisa e validação local

Revisão17/11/2026. O projeto já fazia transferência de aprendizado a partir do YOLO11n oficial; não treinava do zero. A pergunta agora é se outra base leve oferece vantagem e se a integração/treino cabem nesta máquina.

## Modelos encontrados

- **YOLO11n:** base inicial da pesquisa,2,62 M parâmetros no módulo carregado,5,61 MB de pesos. Mantém a stack existente.
- **YOLOv8n:**3,16 M e 6,55 MB medidos; modelo consolidado, compatível com o mesmo pipeline. Fonte oficial: https://docs.ultralytics.com/models/yolov8/
- **YOLO26n:**2,57 M e 5,54 MB medidos; base recente com suporte a detecção fim a fim e foco em execução leve. Contagens de implantação/fusão dos documentos podem diferir do módulo PyTorch carregado. Fonte oficial: https://docs.ultralytics.com/models/yolo26/
- **RF-DETR Nano:** alternativa com licença permissiva Apache2.0 para código/pesos dessa variante, mas a tabela atual do repositório informa30,5 M parâmetros; não tem o mesmo tamanho dos nanoYOLO. Pesquisado, sem instalação, treino ou benchmark local nesta rodada. Fonte primária: https://github.com/roboflow/rf-detr e https://roboflow.com/model-licenses/rf-detr

Os modelos YOLO examinados têm código/pesos disponibilizados sob AGPL3.0 e opção Enterprise. São utilizáveis como base, mas licença aberta não equivale a ausência de obrigações de redistribuição. Não se presumiu isenção acadêmica: a utilização/distribuição precisa respeitar os termos da licença escolhida. Não foram publicados pesos/fotos nesta etapa.

## Comparação realmente executada

Mesmas8 imagens/48 objetos da validação original, CPU, resolução 640. Pesos COCO originais, filtrando/remapeando pelos nomes das12 classes do Acolhe. Grade de confiança 0,05–0,80; escolher maior F1 micro, desempatar por precisão e maior confiança. Nenhuma das23 fotos de teste foi usada para selecionar essas bases.

| Base oficial | Parâmetros medidos | Pesos MB | Precisão val | Recall val | F1 val | Confiança |
|---|---:|---:|---:|---:|---:|---:|
| yolo11n.pt | 2.62 M | 5.61 | 40.0% | 33.3% | 0.364 | 0.10 |
| yolov8n.pt | 3.16 M | 6.55 | 68.2% | 31.2% | 0.429 | 0.20 |
| yolo26n.pt | 2.57 M | 5.54 | 50.0% | 43.8% | 0.467 | 0.10 |

A precisão/recall é por objeto com correspondência1para1 eIoU≥0,5. As contagens de parâmetros/peso foram medidas localmente. Não usar os tempos brutos para comparar latência: a primeira carga incluiu aquecimento de bibliotecas. As oito imagens são uma amostra muito pequena; a origemCOCO também limita independência em relação ao desenvolvimento das bases.

Evidência completa com hashes e grade: vision/reports/pretrained-bases-validation.json. O benchmark é referência de pesos genéricos; não substitui o treinamento customizado pedido na rubrica.

## Decisão e experimento

YOLO26n teve o maior F1 nessa referência, com tamanho parecido ao YOLO11n e sem nova stack. Foi iniciado treino customizado80 épocas640 sobre as 25 fotos de treino já aprovadas, mantendo as 8 de validação e excluindo todas as 23 fotos novas do treino/seleção. O candidato só substitui o ativo se melhorar a regra de seleção em validação. O modelo YOLO11n 80 épocas fica preservado.

O teste 23 foi congelado e já examinado para o modelo anterior. Ele continua como evidência daquela rodada; qualquer reavaliação posterior será identificada como regressão em conjunto já exposto, sem vendê-la como um novo teste cego. Outro teste final será necessário para uma conclusão nova independente.

A meta atual é70% de recall e 70% de precisão no limiar da aplicação. Nenhuma base alcançou as duas métricas nesta referência de validação. Dados de treino diversos e corretamente anotados continuam sendo o principal ponto a ampliar; trocar a arquitetura não garante atingir a meta.

## Reproduzir a comparação de referência

Com o dataset aprovado preparado e a stack Vision instalada, executar na raiz. O trecho usa somente validação e baixa pesos oficiais pela biblioteca, sem enviar imagens para nuvem:

```powershell
@'
from pathlib import Path
import yaml
from ultralytics import YOLO
from vision.calibrate import collect, score
root = Path("vision/data/curated-pilot-01").resolve()
config = yaml.safe_load((root/"dataset.yaml").read_text())
for base in ["yolo11n.pt", "yolov8n.pt", "yolo26n.pt"]:
    images = collect(YOLO(base), root, config, "val", 640)
    grid = [score(images, c) for c in [.05,.10,.15,.20,.25,.35,.50,.65,.80]]
    chosen = max(grid, key=lambda m: (m["f1"], m["precision"], m["confidence"]))
    print(base, chosen)
'@ | .\.venv\Scripts\python.exe -
```

O novo treino customizado usa vision.train --base-model yolo26n.pt; sua saída fica em diretório novo e separado do detector ativo. Não chamar a comparação acima de treinamento próprio.

## Resultado histórico do treino customizado nano

YOLO26n 80 épocas640 concluído e promovido pela validação: F1 micro de 0,4675 contra 0,3488 do YOLO11n 80 épocas; confiança 0,15 selecionada em validação. O arquivo yolo26n-custom-decision.json registra a decisão antes da regressão.

Nas23 fotos já examinadas, o YOLO26n teve34TP/22FP/32FN: recall51,5%, precisão60,7%, F1 de 0,5574. O YOLO11n 80 tinha recall53,0%, precisão48,6%, F1 de 0,5072. A nova base melhorou precisão/F1 com pequena perda de recall. Isso é regressão diagnóstica em teste exposto, não nova comprovação independente. Não houve ajuste após essa medição. Meta70%/70% ainda não atingida.

A API real carregou o checkpoint 007a199a… e reconheceu o ônibus de demonstração com 0,9479; evidência em vision/reports/inference-http-yolo26n.json. Modelo anterior preservado localmente. O pacote Ultralytics foi fixado na versão 8.4.215, realmente usada, para que uma instalação antiga não aceite o requirements e depois falhe ao carregar YOLO26.
