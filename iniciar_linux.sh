#!/usr/bin/env bash
set -e

echo "=============================================================="
echo "   CONTAGEM MANUAL DE MULTIDÕES - IPPUC / RGBTCC"
echo "=============================================================="
echo ""

# Identificação do Python
PYTHON_BIN=""
if command -v python3 &>/dev/null; then
    PYTHON_BIN="python3"
elif command -v python &>/dev/null; then
    PYTHON_BIN="python"
else
    echo "[ERRO] Python 3 não foi encontrado no sistema."
    exit 1
fi

# Criação do Ambiente Virtual (.venv) se não existir
if [ ! -f ".venv/bin/python" ]; then
    echo "[*] Criando ambiente virtual (.venv)..."
    "$PYTHON_BIN" -m venv .venv
    echo "[*] Instalando dependências..."
    .venv/bin/python -m pip install --upgrade pip --quiet
    .venv/bin/python -m pip install -r requirements.txt --quiet
    echo "[✓] Ambiente configurado com sucesso!"
fi

echo "[*] Iniciando a Contagem de Multidões..."
.venv/bin/python app.py "$@"
