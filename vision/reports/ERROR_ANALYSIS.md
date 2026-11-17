# Erros reais do detector piloto

Revisão técnica do agente sobre predições reais, não revisão humana. Confiança 0,5 e IoU 0,5 fixos; não houve ajuste com o teste.
Contagens: 42 objetos anotados, 4 verdadeiros positivos, 1 falsos positivos e 38 objetos não reconhecidos. Essas contagens não substituem o mAP nativo.

| Imagem | Classe não detectada | Maior IoU mesma classe | Confiança correspondente | Hipótese e próxima ação |
|---|---|---:|---:|---|
| 20553 | bottle | 0.4426 | 0.46433 | Poucos exemplos, tamanho/oclusão ou limiar; ampliar dados de treino/validação e avaliar em NOVO teste, sem otimizar sobre este. |
| 20553 | umbrella | 0.8189 | 0.00116 | Poucos exemplos, tamanho/oclusão ou limiar; ampliar dados de treino/validação e avaliar em NOVO teste, sem otimizar sobre este. |
| 20553 | chair | 0.5075 | 0.00912 | Poucos exemplos, tamanho/oclusão ou limiar; ampliar dados de treino/validação e avaliar em NOVO teste, sem otimizar sobre este. |
| 20553 | cup | 0.3824 | 0.00923 | Poucos exemplos, tamanho/oclusão ou limiar; ampliar dados de treino/validação e avaliar em NOVO teste, sem otimizar sobre este. |
| 248314 | spoon | 0.2362 | 0.00167 | Poucos exemplos, tamanho/oclusão ou limiar; ampliar dados de treino/validação e avaliar em NOVO teste, sem otimizar sobre este. |

IDs referem-se ao inventário de procedência. Fotografias e montagens locais de avaliação não foram copiadas para o repositório. Matrizes e curvas sem fotografias são compartilháveis.
O conjunto possui apenas sete fotos de teste; não sustenta afirmação estatística de generalização.
