# Plano de Implementação - Fase 03: Launchers e UX Windows

## 1. Visão Geral
Construir os scripts de inicialização com foco em experiência de usuário "zero-configuração" para os colegas que utilizarão computadores com Windows, eliminando a necessidade de conhecimento prévio de terminal, ambientes virtuais ou comandos Python.

## 2. Requisitos Técnicos
1. **`requirements.txt`:** Especificação exata das dependências estritamente necessárias (`opencv-python`, `numpy`, `pandas`).
2. **`iniciar_windows.bat`:**
   - Detectar executável do Python (`python` ou `py`).
   - Fornecer aviso e instruções caso o Python não esteja instalado ou não esteja no PATH.
   - Criar automaticamente o ambiente virtual isolado `.venv` na primeira execução.
   - Instalar e validar as dependências sem intervenção manual.
   - Executar o `app.py` utilizando o interpretador do ambiente virtual (`.venv\Scripts\python.exe`).
   - Manter a janela aberta com `pause` caso ocorra qualquer erro inesperado.
3. **`iniciar_linux.sh`:**
   - Equivalente em Shell Script com permissão de execução para ambientes Linux/macOS.
