#!/bin/bash

set -e

unset PYTHONPATH

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"

cd "$PROJECT_DIR"

echo "======================================"
echo " CodeJudgeC3 - Instalação"
echo "======================================"

if ! command -v python3 >/dev/null 2>&1; then
    echo "❌ Python 3 não encontrado."
    echo "Instale o Python 3 antes de continuar."
    exit 1
fi

if ! python3 -m venv --help >/dev/null 2>&1; then
    echo "📦 Instalando python3-venv..."
    sudo apt-get update
    sudo apt-get install -y python3-venv
fi

if [ ! -d "venv" ]; then
    echo "📂 Criando ambiente virtual..."
    python3 -m venv venv
else
    echo "✅ Ambiente virtual já existe."
fi

echo "📦 Atualizando pip..."
./venv/bin/python3 -m pip install --upgrade pip

echo "📦 Instalando dependências..."
./venv/bin/python3 -m pip install -r requirements.txt

echo ""
echo "======================================"
echo "✅ Instalação concluída com sucesso!"
echo "======================================"
echo ""
echo "Para iniciar:"
echo "   sh scripts/rodar.sh <ARQUIVO_DE_PROVA>"
echo "Exemplo:"
echo "   sh scripts/rodar.sh testes_parte3.enc"