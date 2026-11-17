# Expansão de Vision — 70 fotos para treino

Pacote local pronto: **70 treino + 20 validação**, cobrindo as mesmas12classes, com mínimo6fotografias por classe no treino e2na validação. Uma foto pode conter várias classes; não são70por classe. Classes comuns ainda têm mais exemplos.

Hash: `29569624253781bd7fb1dd4154efc33df6a8d13656e381d89cc058da77fcf918`.

Revisão com oito folhas: `vision/data/public-review-train70-v2-20261117/REVIEW.md`.85fotos novas e5já aprovadas, preservando seus splits originais. Créditos/licenças/hashes e caixas vinculados ao lote. As fotos ficam locais.

Inspeção técnica removeu cinco cenas inadequadas: colagens, ônibus de brinquedo e cena de avião. Há pessoa distante na foto86, já presente no lote original. Ausência de anotação de pessoa nas demais não certifica privacidade. Revisão humana permanece pendente; nenhum campo foi aprovado pelo agente. Não foram usadas as23fotos de teste para selecionar imagens ou treinar. Sem duplicação binária entre pacote e os30testes históricos, nem dentro do pacote. Similaridade visual ainda exige revisão, além dos hashes.

Após aprovação deste lote concreto:

1. Registrar autorização vinculada ao hash. Preparar dataset com70treino/20validação e as23fotos aprovadas apenas no split de teste. Auditar IDs, hashes, caixas, cobertura e separação antes de treinar. Guardar relatório anterior e pesos ativos.
2. Treinar YOLO26n a partir dos pesos originais,100épocas640, batch2, CPU, workers0, seed42. Não alterar drivers. Escolher confiança apenas na nova validação.
3. Comparar modelo atual e candidato na MESMA nova validação. Promover somente havendo melhora útil; medir precisão e recall juntos, mantendo meta70%/70%, sem promessa de alcance.
4. Congelar candidato antes de medir23. Esse conjunto já foi examinado: resultado é regressão diagnóstica, sem alegação de novo teste cego. Para qualidade final independente, reservar novas fotos ainda não examinadas.
5. Atualizar evidências, PRDs, relatório/PDF e demos com resultados efetivamente medidos.

O treino desse pacote ainda não começou. A rotina de revisão do projeto vincula aprovação às fotos e às anotações específicas; a autorização anterior dos40/23não é atribuída a85novas fotos. Inventário público sem pixels: `vision/reports/expansion70-proposal.json`.

Fontes técnicas: [COCO](https://cocodataset.org/#download) e [Ultralytics](https://docs.ultralytics.com/guides/model-training-tips/). Fonte limitou requisições; a aquisição parou e o lote final foi fechado com o cache de créditos já verificados.
