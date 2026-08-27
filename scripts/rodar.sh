#!/bin/bash

set -e

# Uso:
#   sh scripts/rodar.sh testes_parte3.enc

if [ "$#" -ne 1 ]; then
    echo "❌ Uso: sh scripts/rodar.sh <arquivo_de_testes.enc>"
    echo "   Exemplo: sh scripts/rodar.sh testes_parte3.enc"
    exit 1
fi

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"

cd "$PROJECT_DIR"

ARQUIVO_TESTES="$1"
CAMINHO_TESTES="provas/$ARQUIVO_TESTES"

# Verifica se o arquivo de testes existe
if [ ! -f "$CAMINHO_TESTES" ]; then
    echo "❌ Erro: arquivo '$ARQUIVO_TESTES' não encontrado na pasta provas."
    exit 1
fi

STREAMLIT_BIN="venv/bin/streamlit"

# Verifica se o ambiente virtual existe
if [ ! -f "$STREAMLIT_BIN" ]; then
    echo "❌ Erro: ambiente virtual não encontrado."
    echo "Execute primeiro:"
    echo "   sh scripts/install.sh"
    exit 1
fi

echo "🚀 Iniciando CodeJudgeC3 com '$ARQUIVO_TESTES'..."

"$STREAMLIT_BIN" run app.py -- "$CAMINHO_TESTES"
