# Revisão humana do dataset piloto

Lote v2 aprovado pelo usuário nesta conversa antes do treino, incluindo o ônibus e sua anotação: “Aprovo o lote e o treino, pode treinar na gpu para ser mais rapido”. O registro local reviews.approved.json vincula a aprovação ao hash abaixo. Treino de20 épocas foi concluído em CPU, pois a stack instalada não habilitou a GPUAMD. Evidências finais em vision/reports/ e docs/entregas/VISION_RELATORIO.md. A v1 com bonde foi descartada do treino e preservada como histórico. A autorização cobriu uso local, sem publicação das fotos.

- Pasta local ignorada pelo Git: `vision/data/public-review-pilot-v2-20261116/`.
- Abrir `REVIEW.md` e as quatro folhas `contact-01.jpg` a `contact-04.jpg`.
- Inventário completo: `inventory.csv` e `reviews.json`, com IDs COCO/Commons, autores, URLs, licença e SHA-256 de cada imagem.
- Hash do conjunto exato: `a7f3630698fd57102ea6d1f4f20afabba80c13e35cb96ecf28ac67450b345a71`.
- 40 fotografias reais, 10.278.231 bytes; 25 treino, oito validação e sete teste. As 12 classes têm ao menos uma imagem em cada split.

## Limite do piloto

As quantidades de imagens por classe em treino/validação/teste são:

| Classe | Treino | Validação | Teste |
|---|---:|---:|---:|
| backpack | 3 | 1 | 1 |
| chair | 6 | 2 | 3 |
| book | 2 | 1 | 1 |
| bottle | 6 | 1 | 2 |
| cup | 5 | 3 | 2 |
| spoon | 5 | 2 | 1 |
| fork | 6 | 1 | 1 |
| bowl | 9 | 3 | 2 |
| clock | 3 | 1 | 1 |
| umbrella | 1 | 1 | 1 |
| bus | 1 | 1 | 1 |
| traffic light | 1 | 1 | 1 |

Fotos podem conter mais de uma classe; não somar essas contagens como imagens únicas. Ônibus e guarda-chuva têm somente uma imagem de treino: isso é suficiente para verificar a execução do pipeline, mas **não para afirmar qualidade ou generalização**. O conjunto deve ser ampliado após a revisão e antes da avaliação final da disciplina.

**Correção da ambiguidade da v1:** ID514376 recebia `bus` no COCO, mas o bbox cobria um bonde. A v2 remove essa foto e todas as suas anotações, substituindo-a por [Burlington Trailways bus](https://commons.wikimedia.org/wiki/File:Burlington_Trailways_bus.jpg), autor **Znns**, CC-BY4.0, obtida pela API oficial Commons sem consultar Flickr. É uma fotografia de ônibus completo, sem pessoas/crianças visíveis na inspeção do agente. A foto #004 usa IDlocal900000001. A caixa `[720,1040,3408,1296]` (xywh em pixels originais4496x3000) foi proposta manualmente pelo agente e continua **pendente de revisão humana**; ver `proposed-bus-bbox.jpg`.

A foto antiga era a única com semáforo no teste. Por isso, ID393226 passou de treino para teste antes de qualquer treino/avaliação. A v2 continua com40imagens e as12classes nos3splits, sem duplicar fotografias. O JSON `instances_subset.json` contém39imagens COCO e a nova imagem Commons com bbox de origem explícita. O hash de aprovação vincula agora tanto as fotografias quanto o JSON completo de anotações. A v1 e seu hash `bbeef75d329a72ded4635c22c80c9c2435b5e02a7087bf0374417963f8e6bdb9` estão preservados.

## Origem, licença e revisão

Metadados COCO val2017 foram obtidos via HTTP Range no espelho [fast.ai listado no registro AWS](https://registry.opendata.aws/fast-ai-coco/), transferindo aproximadamente 6,53 MB para o membro de instâncias, em vez do ZIP de 252 MB inteiro. As fotos foram obtidas por HTTPS no bucket de imagens COCO, sem desabilitar TLS. Anotações são CC-BY 4.0; cada fotografia tem direitos próprios conforme os [termos oficiais COCO](https://cocodataset.org/dataset/termsofuse.htm).

As39fotografias COCO restantes tiveram autoria/CC-BY2.0 confirmados nas páginas Flickr antes do limite429. A foto substituta tem autoria/CC-BY4.0 confirmados em `commons-imageinfo.json`, com SHA-1 do original conferido contra a API oficial Commons. Autoria, URL, licença, momento da consulta e hash da página estão no inventário local. Isso registra a evidência consultada; não equivale a parecer jurídico ou licença concedida pelo agente.

A seleção priorizou fotos sem anotação de pessoa e excluiu captions que mencionam crianças. O agente inspecionou as folhas de contato e retirou conservadoramente IDs 328238, 303713, 211825 e 250619 por idade ambígua, público ou privacidade não verificável. Ausência de anotação/caption não prova ausência de pessoa; **o usuário ainda precisa revisar todas as imagens do pacote final**. Nenhum campo `privacy_reviewed` foi alterado para verdadeiro.

A primeira tentativa de adquirir quantidade maior encontrou HTTP 429 do Flickr e não atingiu a meta. A rotina agora interrompe esse código; o pacote final foi fechado somente com os créditos já verificados em cache. Os diretórios de tentativas anteriores são cache, não fazem parte deste conjunto aprovado e não devem ser usados como dataset.

## Aprovação vinculada aos arquivos

Depois de o usuário aprovar explicitamente as quatro folhas deste hash, registrar a autorização concreta:

```powershell
python -m vision.public_review approve --root vision/data/public-review-pilot-v2-20261116 --packet-sha256 a7f3630698fd57102ea6d1f4f20afabba80c13e35cb96ecf28ac67450b345a71 --reviewer "NOME DO REVISOR" --reference "REFERENCIA DA APROVACAO"
```

Esse comando valida o hash do inventário e de cada fotografia, exige identificação/referência e cria `reviews.approved.json` exclusivamente. Não altera o pacote original e não sobrescreve aprovações anteriores. A autorização de baixar um subconjunto não é tratada como aprovação das fotografias.

Só então converter e auditar:

```powershell
python -m vision.prepare --annotations vision/data/public-review-pilot-v2-20261116/instances_subset.json --images vision/data/public-review-pilot-v2-20261116/originals --reviews vision/data/public-review-pilot-v2-20261116/reviews.approved.json --output vision/data/curated-pilot-01
python -m vision.audit --dataset vision/data/curated-pilot-01/dataset.yaml --provenance vision/data/curated-pilot-01/provenance.json
```

O script de aquisição é `python -m vision.public_review build --help`; os limites e a revisão continuam explícitos. Não publicar fotos, dados ou pesos inadvertidamente. O treino real e a análise de qualidade permanecem bloqueados até a revisão aprovada e o experimento executado.


A substituição é reproduzível, sem nova rede, com:

```powershell
python -m vision.replace_review_bus --source vision/data/public-review-pilot-20261116 --target vision/data/NOVO_PACOTE --image vision/data/commons-candidate-20261116/Burlington_Trailways_bus.jpg --commons-metadata vision/data/commons-candidate-20261116/burlington-imageinfo.json
```

A rotina valida origem, licença, dimensões, hash do original, cobertura de classes e cria somente pasta nova. Não aprova imagens nem inicia treinamento.
