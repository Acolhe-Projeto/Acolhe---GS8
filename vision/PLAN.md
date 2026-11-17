# Vision — plano executado e estado final

17/11/2026. Ativo: YOLO26m91 em CPU, inferência 960 e confiança 0,25. Treino ativo: 91 fotos, cinco épocas concluídas de máximo12, checkpoint escolhido cedo. A continuação com117fotos concluiu7épocas e não foi promovida, pois não superou a referência na mesma validação38. [Plano, pesquisa, diagramas e fases](../docs/entregas/VISION_FINETUNING.md).

| Avaliação | Precisão | Recall | Estado |
|---|---:|---:|---|
| Validação ampliada38 |72,7%|71,5%|Meta observada no desenvolvimento |
| Novo teste básico reservado13/72objetos |71,2%|72,2%|Meta observada nesse piloto |
| Diagnóstico complexo anterior23 |68,3%|62,1%|Conjunto diferente, sem reavaliação final |

## Trabalho concluído

- União e auditoria dos dados aprovados, sem movimentar os23antigos para o novo conjunto. Experimento final:117treino/38validação/13teste,691/291/72objetos.
- Comparação controlada dos nanos antigo, recente e controle oficial:9épocas adicionais cada.
- Pesquisa de capacidade e treino customizado M:5épocas; continuação M117:7épocas. Taxas/AdamW explícitos, hashes e épocas máximas/executadas separados.
- Seleção pela validação e confiança refinada em passos0,01 antes do teste. Decisão congelada, modelo anterior M91 mantido.
- Teste13 executado uma vez:52TP21FP20FN. Referência e selecionado são idênticos; não houve falsa evidência pareada nem retunagem após o teste.
- API, duas fotos do roteiro, GenAI, notebook e latência verificados.122testes passaram; PDF e PRDs atualizados.

## Limites e próximos passos

Não chamar o resultado de ausência de erros. O13é pequeno e básico; fonteCOCO pode sobrepor pré-treino. O23mais complexo continua pior. Livros/cadeiras e falsos positivos ainda precisam de atenção. Há revisão pedagógica e nova avaliação em cenas reais de uso a fazer. Fotos/pesos não foram publicados.

O lote50 já foi aprovado e usado na comparação; não há nova aprovação de dados pendente desta rodada. Restam revisão final da equipe, vídeos reais, URLs e envio no Teams. Não alterar confiança com base no teste já examinado.
