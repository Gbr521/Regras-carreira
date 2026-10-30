#!/usr/bin/env bash
# Script para inicializar o Sistema Especialista em Carreiras TI

cd "$(dirname "$0")"

if [ -d ".venv" ]; then
    echo "Iniciando aplicação Streamlit utilizando ambiente virtual .venv..."
    .venv/bin/streamlit run app.py
else
    echo "Ambiente .venv não encontrado, tentando streamlit do sistema..."
    streamlit run app.py
fi
