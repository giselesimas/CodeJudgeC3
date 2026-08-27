# CodeJudgeC3

Sistema para aplicação e correção automática de exercícios de programação em Python, desenvolvido para uso acadêmico no **C3/FURG**.

## Instalação e Execução

### Linux

1. Faça o download do projeto no GitHub https://github.com/giselesimas/CodeJudgeC3:

   * Clique em **Code**
   * Selecione **Download ZIP**

2. Extraia o arquivo ZIP em uma pasta do computador.

3. Abra o terminal dentro da pasta extraída.

4. Execute:

```bash
sh scripts/install.sh
```

Após a instalação, execute o sistema com:

```bash
sh scripts/rodar.sh <ARQUIVO_DE_PROVA>
```

Exemplo:

```bash
sh scripts/rodar.sh testes_parte3.enc
```


### Windows

1. Faça o download do projeto no GitHub https://github.com/giselesimas/CodeJudgeC3:

   * Clique em **Code**
   * Selecione **Download ZIP**

2. Extraia o arquivo ZIP em uma pasta do computador.

3. Abra o **Prompt de Comando (CMD)** dentro da pasta extraída.

4. Execute:

```bat
scripts\install.bat
```

Após a instalação, execute o sistema com:

```bat
scripts\rodar.bat <ARQUIVO_DE_PROVA>
```

Exemplo:


```bat
scripts\rodar.bat testes_parte3.enc
```

## Estrutura

```text
CodeJudgeC3/
├── app.py
├── juiz_core.py
├── provas/
├── scripts/
│   ├── install.bat
│   ├── install.sh
│   ├── rodar.bat
│   └── rodar.sh
├── solucoes/
├── .streamlit/
├── requirements.txt
├── VERSION
└── README.md
```

