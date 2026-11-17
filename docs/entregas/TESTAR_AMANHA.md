# Testar o Acolhe

1. Abra o aplicativo **Ollama**. No PowerShell, execute:

```powershell
cd D:\GS2026\Acolhe---GS8
.\scripts\iniciar-demo.ps1
```

2. Deixe o terminal aberto e entre no endereço que ele mostrar depois de **Acolhe:**. O script escolhe uma porta livre automaticamente. Aguarde a primeira resposta, que pode demorar mais para carregar o modelo.

3. Em **Caminho seguro**, cole uma frase por vez e clique em **Perguntar ao ajudante**:

| Idioma no seletor | Frase para colar | O que conferir |
|---|---|---|
| Português | Como atravessar a rua com segurança? | Orientação, fonte e acompanhamento por adulto |
| Português | Como digo silla? | A palavra cadeira |
| Português | Como devo esperar para embarcar no ônibus? | Esperar longe da borda e embarcar com responsável |
| Español | Necesito ayuda, estoy perdido | Lugar seguro, ayuda y fuente |
| Português | Qual é a previsão de chuva amanhã? | Recusa: não consta no material |

4. Volte o idioma para **Português**. Clique em **Para educadores**, vá até **Objetos que ensinam** e clique em selecionar foto. Abra esta pasta:

```text
D:\GS2026\Acolhe---GS8\docs\qa\testar
```

5. Selecione **01-onibus.jpg** e clique em **Reconhecer objetos**. Confira o nome ônibus/autobús e a confiança:

![Foto de ônibus para testar](../qa/testar/01-onibus.jpg)

6. Repita com **02-mesa-garfo-tigela.jpg**. Confira os objetos encontrados e os nomes em português/espanhol:

![Mesa com tigela, colher e garfo](../qa/testar/02-mesa-garfo-tigela.jpg)

7. Para gravar rapidamente o GenAI, mostre a pergunta de travessia, a fonte, a troca para espanhol e a pergunta sobre chuva. Diga: “O Acolhe usa uma IA local com uma base de conhecimento. A interface mostra a fonte e recusa informações que não constam. O protótipo ainda pode errar.”

8. Para gravar Vision, envie as duas fotos e mostre os nomes PT/ES. Diga: “O detector recebeu treinamento customizado para reconhecer objetos. Os resultados têm erros documentados e não autorizam decisões de travessia.”

As fotos de ensaio estão somente nesta máquina. Os créditos estão em docs/qa/testar/CREDITOS_E_RESULTADOS.json. Antes de publicar um vídeo que as exiba, confira os créditos/licenças e a exibição autorizada. Para encerrar o servidor, volte ao terminal e pressione Ctrl+C.
