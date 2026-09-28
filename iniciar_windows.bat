@echo off
chcp 65001 >nul
title Contagem de Multidões (Ground Truth)

echo ==============================================================
echo    CONTAGEM MANUAL DE MULTIDÕES - IPPUC / RGBTCC
echo ==============================================================
echo.

:: 1. Verificação do Python no sistema
set PYTHON_CMD=
where python >nul 2>nul
if %errorlevel% equ 0 (
    set PYTHON_CMD=python
) else (
    where py >nul 2>nul
    if %errorlevel% equ 0 (
        set PYTHON_CMD=py
    )
)

if "%PYTHON_CMD%"=="" (
    echo [ERRO] O Python não foi encontrado no seu computador!
    echo.
    echo Para instalar:
    echo 1. Baixe o instalador em: https://www.python.org/downloads/
    echo 2. IMPORTANTE: Na primeira tela do instalador, marque a opção:
    echo    "[X] Add python.exe to PATH"
    echo 3. Conclua a instalação e clique duas vezes neste arquivo novamente.
    echo.
    pause
    exit /b 1
)

:: 2. Criação do Ambiente Virtual (.venv) se não existir
if not exist ".venv\Scripts\python.exe" (
    echo [*] Configurando ambiente local pela primeira vez (.venv)...
    %PYTHON_CMD% -m venv .venv
    if errorlevel 1 (
        echo [ERRO] Falha ao criar o ambiente virtual.
        pause
        exit /b 1
    )
    echo [✓] Ambiente virtual criado com sucesso!
    echo.
    echo [*] Instalando dependências (OpenCV, NumPy, Pandas)...
    .venv\Scripts\python.exe -m pip install --upgrade pip --quiet
    .venv\Scripts\python.exe -m pip install -r requirements.txt --quiet
    if errorlevel 1 (
        echo [ERRO] Falha ao instalar as dependências. Verifique sua conexão à internet.
        pause
        exit /b 1
    )
    echo [✓] Dependências instaladas com sucesso!
    echo.
)

:: 3. Execução do Aplicativo
echo [*] Iniciando a Contagem de Multidões...
.venv\Scripts\python.exe app.py %*

if errorlevel 1 (
    echo.
    echo [AVISO] O aplicativo encerrou com aviso ou erro.
    pause
)
