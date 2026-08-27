@echo off
setlocal

cd /d "%~dp0\.."

echo ======================================
echo  CodeJudgeC3 - Instalacao
echo ======================================

where py >nul 2>&1
if not errorlevel 1 (
    set "PYTHON_CMD=py -3"
) else (
    where python >nul 2>&1
    if errorlevel 1 (
        echo.
        echo ERRO: Python 3 nao encontrado.
        echo Instale o Python 3 antes de continuar.
        pause
        exit /b 1
    )
    set "PYTHON_CMD=python"
)

if not exist "venv\Scripts\python.exe" (
    echo.
    echo Criando ambiente virtual...
    %PYTHON_CMD% -m venv venv

    if errorlevel 1 (
        echo ERRO ao criar ambiente virtual.
        pause
        exit /b 1
    )
) else (
    echo Ambiente virtual ja existe.
)

echo.
echo Atualizando pip...
"venv\Scripts\python.exe" -m pip install --upgrade pip

echo.
echo Instalando dependencias...
"venv\Scripts\python.exe" -m pip install -r requirements.txt

if errorlevel 1 (
    echo.
    echo ERRO ao instalar dependencias.
    pause
    exit /b 1
)

echo.
echo ======================================
echo Instalacao concluida com sucesso!
echo ======================================
echo.
echo Para iniciar:
echo    scripts\rodar.bat ARQUIVO_DE_PROVA
echo.
echo Exemplo:
echo    scripts\rodar.bat testes_parte3.enc
echo.

pause