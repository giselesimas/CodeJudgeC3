# CodeJudgeC3

Sistema para aplicação e correção automática de exercícios de programação em Python, desenvolvido para uso acadêmico no **C3/FURG**.

## Instalação

```bash
git clone https://github.com/giselesimas/CodeJudgeC3
cd CodeJudgeC3
sh scripts/install.sh
```

## Execução

```bash
sh scripts/rodar.sh <ARQUIVO_DE_PROVA>
```

Exemplo:

```bash
sh scripts/rodar.sh testes_parte3.enc
```

## Estrutura

```text
CodeJudgeC3/
├── app.py
├── juiz_core.py
├── provas/
├── scripts/
│   ├── install.sh
│   └── rodar.sh
├── solucoes/
├── .streamlit/
├── requirements.txt
└── README.md
```

