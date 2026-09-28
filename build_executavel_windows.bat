@echo off
chcp 65001 >nul
title Gerador de Executável Windows - Contagem de Multidões

echo ============================================================================
echo      GERADOR DE EXECUTÁVEL WINDOWS (.EXE) - CONTAGEM DE MULTIDÕES
echo ============================================================================
echo.

:: 1. Verificação do Python
set PYTHON_CMD=
if exist ".venv\Scripts\python.exe" (
    set PYTHON_CMD=.venv\Scripts\python.exe
) else (
    where python >nul 2>nul
    if %errorlevel% equ 0 (
        set PYTHON_CMD=python
    ) else (
        where py >nul 2>nul
        if %errorlevel% equ 0 (
            set PYTHON_CMD=py
        )
    )
)

if "%PYTHON_CMD%"=="" (
    echo [ERRO] O Python não foi encontrado no seu computador!
    echo Instale o Python (3.9 a 3.13) e marque a opção "[X] Add python.exe to PATH".
    pause
    exit /b 1
)

:: 2. Configuração do ambiente virtual se necessário
if not exist ".venv\Scripts\python.exe" (
    echo [*] Criando ambiente virtual local (.venv)...
    %PYTHON_CMD% -m venv .venv
    if errorlevel 1 (
        echo [ERRO] Falha ao criar ambiente virtual.
        pause
        exit /b 1
    )
    set PYTHON_CMD=.venv\Scripts\python.exe
) else (
    set PYTHON_CMD=.venv\Scripts\python.exe
)

:: 3. Instalação do PyInstaller e dependências
echo [*] Verificando dependências (OpenCV, NumPy, Pandas, PyInstaller)...
%PYTHON_CMD% -m pip install --upgrade pip --quiet
%PYTHON_CMD% -m pip install -r requirements.txt pyinstaller --quiet
if errorlevel 1 (
    echo [ERRO] Falha ao instalar dependências de compilação.
    pause
    exit /b 1
)
echo [✓] Ambiente de compilação pronto!
echo.

:: 4. Escolha do formato de compilação
echo Escolha o formato de executável desejado:
echo   [1] Arquivo Único (.exe portátil de ~60MB - mais fácil de compartilhar)
echo   [2] Pasta Portável (Abertura instantânea sem descompactação temporária)
echo   [3] Compilar Ambos
echo.
set /p OPCAO="Digite a opção [1, 2 ou 3] (Padrão: 1): "
if "%OPCAO%"=="" set OPCAO=1

echo.
echo [*] Iniciando compilação com PyInstaller...
echo.

if "%OPCAO%"=="1" goto BUILD_ONEFILE
if "%OPCAO%"=="2" goto BUILD_ONEDIR
if "%OPCAO%"=="3" goto BUILD_AMBOS
goto BUILD_ONEFILE

:BUILD_ONEFILE
echo [1/1] Gerando Arquivo Único (dist\ContagemMultidoes.exe)...
%PYTHON_CMD% -m PyInstaller --noconfirm --clean --onefile --name "ContagemMultidoes" app.py
if errorlevel 1 goto ERRO_BUILD
goto FINALIZAR_ESTRUTURA_ONEFILE

:BUILD_ONEDIR
echo [1/1] Gerando Pasta Portável (dist\ContagemMultidoes\)...
%PYTHON_CMD% -m PyInstaller --noconfirm --clean --onedir --name "ContagemMultidoes" app.py
if errorlevel 1 goto ERRO_BUILD
goto FINALIZAR_ESTRUTURA_ONEDIR

:BUILD_AMBOS
echo [1/2] Gerando Pasta Portável (dist\ContagemMultidoes_Pasta\)...
%PYTHON_CMD% -m PyInstaller --noconfirm --clean --onedir --name "ContagemMultidoes_Pasta" app.py
if errorlevel 1 goto ERRO_BUILD

echo [2/2] Gerando Arquivo Único (dist\ContagemMultidoes.exe)...
%PYTHON_CMD% -m PyInstaller --noconfirm --clean --onefile --name "ContagemMultidoes" app.py
if errorlevel 1 goto ERRO_BUILD
goto FINALIZAR_ESTRUTURA_AMBOS

:FINALIZAR_ESTRUTURA_ONEFILE
echo [*] Criando estrutura de pastas de dados em dist\...
if not exist "dist\data\input" mkdir "dist\data\input"
if not exist "dist\data\ground_truth" mkdir "dist\data\ground_truth"
(
echo INSTRUÇÕES DE USO DO APLICATIVO
echo ==============================
echo 1. Coloque suas fotos aéreas (.JPG ou .PNG) dentro da pasta 'data\input'.
echo 2. Dê duplo clique em 'ContagemMultidoes.exe'.
echo 3. Ao finalizar, seus relatórios e arquivos Ground Truth serão gerados em 'data\ground_truth'.
) > "dist\COMO_USAR.txt"
goto SUCESSO

:FINALIZAR_ESTRUTURA_ONEDIR
echo [*] Criando estrutura de pastas de dados em dist\ContagemMultidoes\...
if not exist "dist\ContagemMultidoes\data\input" mkdir "dist\ContagemMultidoes\data\input"
if not exist "dist\ContagemMultidoes\data\ground_truth" mkdir "dist\ContagemMultidoes\data\ground_truth"
(
echo INSTRUÇÕES DE USO DO APLICATIVO
echo ==============================
echo 1. Coloque suas fotos aéreas (.JPG ou .PNG) dentro da pasta 'data\input'.
echo 2. Dê duplo clique em 'ContagemMultidoes.exe'.
echo 3. Ao finalizar, seus relatórios e arquivos Ground Truth serão gerados em 'data\ground_truth'.
) > "dist\ContagemMultidoes\COMO_USAR.txt"
goto SUCESSO

:FINALIZAR_ESTRUTURA_AMBOS
if not exist "dist\data\input" mkdir "dist\data\input"
if not exist "dist\data\ground_truth" mkdir "dist\data\ground_truth"
if not exist "dist\ContagemMultidoes_Pasta\data\input" mkdir "dist\ContagemMultidoes_Pasta\data\input"
if not exist "dist\ContagemMultidoes_Pasta\data\ground_truth" mkdir "dist\ContagemMultidoes_Pasta\data\ground_truth"
(
echo INSTRUÇÕES DE USO DO APLICATIVO
echo ==============================
echo 1. Coloque suas fotos aéreas (.JPG ou .PNG) dentro da pasta 'data\input'.
echo 2. Dê duplo clique em 'ContagemMultidoes.exe'.
echo 3. Ao finalizar, seus relatórios e arquivos Ground Truth serão gerados em 'data\ground_truth'.
) > "dist\COMO_USAR.txt"
copy /y "dist\COMO_USAR.txt" "dist\ContagemMultidoes_Pasta\COMO_USAR.txt" >nul
goto SUCESSO

:SUCESSO
echo.
echo ============================================================================
echo   [✓ SUCESSO] EXECUTÁVEL GERADO COM SUCESSO NA PASTA 'dist\'!
echo ============================================================================
echo.
echo Para distribuir para seus colegas:
echo  - Se você escolheu 'Arquivo Único': compartilhe a pasta 'dist\' compactada em .zip.
echo  - Se você escolheu 'Pasta Portável': compartilhe a pasta 'dist\ContagemMultidoes\' compactada em .zip.
echo.
echo O usuário final NÃO precisará ter o Python instalado!
echo ============================================================================
echo.
pause
exit /b 0

:ERRO_BUILD
echo.
echo [ERRO] Ocorreu uma falha durante o empacotamento com o PyInstaller.
pause
exit /b 1
