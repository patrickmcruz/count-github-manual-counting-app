@echo off
chcp 65001 >nul
title Gerador de Executavel Windows - Contagem de Multidoes

echo ============================================================================
echo      GERADOR DE EXECUTAVEL WINDOWS (.EXE) - CONTAGEM DE MULTIDOES
echo ============================================================================
echo.

set "PYTHON_CMD="
if exist ".venv\Scripts\python.exe" goto PYTHON_VENV_FOUND
where python >nul 2>&1
if not errorlevel 1 goto PYTHON_COMMAND_FOUND
where py >nul 2>&1
if not errorlevel 1 goto PYTHON_LAUNCHER_FOUND
goto PYTHON_NOT_FOUND

:PYTHON_VENV_FOUND
set "PYTHON_CMD=.venv\Scripts\python.exe"
goto PYTHON_READY

:PYTHON_COMMAND_FOUND
set "PYTHON_CMD=python"
goto PYTHON_READY

:PYTHON_LAUNCHER_FOUND
set "PYTHON_CMD=py"
goto PYTHON_READY

:PYTHON_NOT_FOUND
echo [ERRO] Python nao foi encontrado neste computador.
echo Instale Python 3.9 a 3.13 e marque "Add python.exe to PATH".
pause
exit /b 1

:PYTHON_READY
if exist ".venv\Scripts\python.exe" goto VENV_READY
echo [*] Criando ambiente virtual local (.venv)...
%PYTHON_CMD% -m venv .venv
if errorlevel 1 goto VENV_ERROR
set "PYTHON_CMD=.venv\Scripts\python.exe"
goto VENV_READY

:VENV_ERROR
echo [ERRO] Falha ao criar ambiente virtual.
pause
exit /b 1

:VENV_READY
echo [*] Verificando dependencias (OpenCV, NumPy, Pandas, PyInstaller)...
%PYTHON_CMD% -m pip install --upgrade pip --quiet
%PYTHON_CMD% -m pip install -r requirements.txt pyinstaller --quiet
if errorlevel 1 goto DEPENDENCY_ERROR
echo [OK] Ambiente de compilacao pronto!
echo.

echo Escolha o formato de executavel desejado:
echo   [1] Arquivo Unico (.exe portatil de ~60MB - mais facil de compartilhar)
echo   [2] Pasta Portatil (abertura instantanea)
echo   [3] Compilar Ambos
echo.
set /p OPCAO="Digite a opcao [1, 2 ou 3] (Padrao: 1): "
if "%OPCAO%"=="" set "OPCAO=1"

echo.
echo [*] Iniciando compilacao com PyInstaller...
echo.
if "%OPCAO%"=="1" goto BUILD_ONEFILE
if "%OPCAO%"=="2" goto BUILD_ONEDIR
if "%OPCAO%"=="3" goto BUILD_AMBOS
goto BUILD_ONEFILE

:BUILD_ONEFILE
echo [1/1] Gerando Arquivo Unico (dist\ContagemMultidoes.exe)...
%PYTHON_CMD% -m PyInstaller --noconfirm --clean --onefile --name "ContagemMultidoes" app.py
if errorlevel 1 goto ERRO_BUILD
goto FINALIZAR_ESTRUTURA_ONEFILE

:BUILD_ONEDIR
echo [1/1] Gerando Pasta Portatil (dist\ContagemMultidoes\)...
%PYTHON_CMD% -m PyInstaller --noconfirm --clean --onedir --name "ContagemMultidoes" app.py
if errorlevel 1 goto ERRO_BUILD
goto FINALIZAR_ESTRUTURA_ONEDIR

:BUILD_AMBOS
echo [1/2] Gerando Pasta Portatil (dist\ContagemMultidoes_Pasta\)...
%PYTHON_CMD% -m PyInstaller --noconfirm --clean --onedir --name "ContagemMultidoes_Pasta" app.py
if errorlevel 1 goto ERRO_BUILD
echo [2/2] Gerando Arquivo Unico (dist\ContagemMultidoes.exe)...
%PYTHON_CMD% -m PyInstaller --noconfirm --clean --onefile --name "ContagemMultidoes" app.py
if errorlevel 1 goto ERRO_BUILD
goto FINALIZAR_ESTRUTURA_AMBOS

:FINALIZAR_ESTRUTURA_ONEFILE
echo [*] Criando estrutura de pastas de dados em dist\...
if exist "dist\data\ground_truth" rmdir /s /q "dist\data\ground_truth"
if not exist "dist\data\ground_truth" mkdir "dist\data\ground_truth"
> "dist\COMO_USAR.txt" echo INSTRUCOES DE USO DO APLICATIVO
>> "dist\COMO_USAR.txt" echo ==============================
>> "dist\COMO_USAR.txt" echo 1. Execute ContagemMultidoes.exe.
>> "dist\COMO_USAR.txt" echo 2. Clique no botão para selecionar suas fotos JPG ou PNG.
>> "dist\COMO_USAR.txt" echo 3. Clique na cabeça de cada pessoa encontrada, se não tiver cabeça clique na parte visível.
>> "dist\COMO_USAR.txt" echo 4. Salve regularmente a contagem no botão "Salvar".
>> "dist\COMO_USAR.txt" echo 5. Os relatorios serao gerados em data\ground_truth.
goto SUCESSO

:FINALIZAR_ESTRUTURA_ONEDIR
echo [*] Criando estrutura de pastas de dados em dist\ContagemMultidoes\...
if exist "dist\ContagemMultidoes\data\ground_truth" rmdir /s /q "dist\ContagemMultidoes\data\ground_truth"
if not exist "dist\ContagemMultidoes\data\ground_truth" mkdir "dist\ContagemMultidoes\data\ground_truth"
> "dist\ContagemMultidoes\COMO_USAR.txt" echo INSTRUCOES DE USO DO APLICATIVO
>> "dist\ContagemMultidoes\COMO_USAR.txt" echo ==============================
>> "dist\ContagemMultidoes\COMO_USAR.txt" echo 1. Execute ContagemMultidoes.exe.
>> "dist\ContagemMultidoes\COMO_USAR.txt" echo 2. Clique no botão para selecionar suas fotos JPG ou PNG.
>> "dist\ContagemMultidoes\COMO_USAR.txt" echo 3. Clique na cabeça de cada pessoa encontrada, se não tiver cabeça clique na parte visível.
>> "dist\ContagemMultidoes\COMO_USAR.txt" echo 4. Salve regularmente a contagem no botão "Salvar".
>> "dist\ContagemMultidoes\COMO_USAR.txt" echo 5. Os relatorios serao gerados em data\ground_truth.
goto SUCESSO

:FINALIZAR_ESTRUTURA_AMBOS
if exist "dist\data\ground_truth" rmdir /s /q "dist\data\ground_truth"
if exist "dist\ContagemMultidoes_Pasta\data\ground_truth" rmdir /s /q "dist\ContagemMultidoes_Pasta\data\ground_truth"
if not exist "dist\data\ground_truth" mkdir "dist\data\ground_truth"
if not exist "dist\ContagemMultidoes_Pasta\data\ground_truth" mkdir "dist\ContagemMultidoes_Pasta\data\ground_truth"
> "dist\COMO_USAR.txt" echo INSTRUCOES DE USO DO APLICATIVO
>> "dist\COMO_USAR.txt" echo ==============================
>> "dist\COMO_USAR.txt" echo 1. Execute ContagemMultidoes.exe.
>> "dist\COMO_USAR.txt" echo 2. Clique no botão para selecionar suas fotos JPG ou PNG.
>> "dist\COMO_USAR.txt" echo 3. Clique na cabeça de cada pessoa encontrada, se não tiver cabeça clique na parte visível.
>> "dist\COMO_USAR.txt" echo 4. Salve regularmente a contagem no botão "Salvar".
>> "dist\COMO_USAR.txt" echo 5. Os relatorios serao gerados em data\ground_truth.
copy /y "dist\COMO_USAR.txt" "dist\ContagemMultidoes_Pasta\COMO_USAR.txt" >nul
goto SUCESSO

:DEPENDENCY_ERROR
echo [ERRO] Falha ao instalar as dependencias de compilacao.
pause
exit /b 1

:SUCESSO
echo.
echo ============================================================================
echo   [OK] EXECUTAVEL GERADO COM SUCESSO NA PASTA dist\
echo ============================================================================
echo.
echo O usuario final nao precisara ter Python instalado.
pause
exit /b 0

:ERRO_BUILD
echo.
echo [ERRO] Ocorreu uma falha durante o empacotamento com o PyInstaller.
pause
exit /b 1
