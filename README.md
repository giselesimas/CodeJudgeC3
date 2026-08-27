# CodeJudgeC3

Sistema para aplicação e correção automática de exercícios de programação em Python, desenvolvido para uso acadêmico no **C3/FURG**.

## Instalação

```bash
git clone <URL_DO_REPOSITORIO>
cd CodeJudgeC3
sh scripts/install.sh
```

## Execução

```bash
sh scripts/rodar.sh testes_parte1_2.enc
```

ou

```bash
sh scripts/rodar.sh testes_parte3.enc
```

O sistema será iniciado em:

```text
http://localhost:8501
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

