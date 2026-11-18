# Roteiro de gravação

Use [COMO_USAR_E_GRAVAR.md](COMO_USAR_E_GRAVAR.md) ou [TESTAR_AMANHA.md](TESTAR_AMANHA.md): abrir na porta livre, testar frases e enviar as duas fotos locais.

GenAI: Qwen2.5 3B local com RAG, fontes, recusa e comparação com agente. Vision ativo: YOLO26m customizado, treino com 91 fotos, inferência 960 e confiança 0,25. No teste básico reservado de 13 fotos: precisão 71,2% e recall 72,2%, atingindo a meta 70%/70% nesse lote pequeno. Na regressão exposta de 23 fotos: precisão 68,3% e recall 62,1%. Não descrever esse diagnóstico como teste cego novo nem generalizar a meta para qualquer imagem.

Mostre respostas e fontes do GenAI e a recusa sobre previsão de chuva. Em Vision, abra **Para educadores → Objetos que ensinam**, selecione as fotos na pasta abaixo e clique em **Reconhecer objetos** após cada seleção:

```text
D:\GS2026\Acolhe---GS8\vision\examples
```

1. **01-onibus.jpg**: mostrar **ônibus / autobús**.
2. **02-mesa-garfo-tigela.jpg**: mostrar **garfo / tenedor**, **tigela / cuenco** e **colher / cuchara**.

Esses são resultados esperados, confirmados na última verificação local; apresente o resultado real da gravação. **03-copo-cadeira.jpg** é uma cena opcional mais difícil. As três imagens acompanham o clone em vision/examples. Créditos para publicação: ônibus — Znns, CC BY 4.0; mesa — jules, CC BY 2.0; cadeiras — liz west, CC BY 2.0. Fontes, licenças e hashes em vision/examples/credits.json.

Diga que o protótipo ainda erra. Vídeos, revisão de imagem/voz/créditos, publicação e URLs reais continuam pendentes.

Resultado final adicional: no13básico reservado, oM91ativo atingiu precisão71,2% e recall72,2%. A comparação117não justificou trocar os pesos. O23complexo mantém68,3%/62,1%; não atribuir a diferença entre conjuntos a melhora causada por novo treino.
