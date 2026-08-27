# CodeJudgeC3

Sistema para aplicação e correção automática de exercícios de programação em Python, desenvolvido para uso acadêmico no **C3/FURG**.

## Instalação

### Linux

```bash
git clone https://github.com/giselesimas/CodeJudgeC3
cd CodeJudgeC3
sh scripts/install.sh
```

### Windows

Abra o **Prompt de Comando (CMD)** e execute:

```bat
git clone https://github.com/giselesimas/CodeJudgeC3
cd CodeJudgeC3
scripts\install.bat
```

## Execução

### Linux

```bash
sh scripts/rodar.sh <ARQUIVO_DE_PROVA>
```

Exemplo:

Abra o **Prompt de Comando (CMD)** e execute:

```bash
sh scripts/rodar.sh testes_parte3.enc
```

### Windows

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

