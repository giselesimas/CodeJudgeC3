@echo off
setlocal

cd /d "%~dp0\.."

if "%~1"=="" goto uso

if not "%~2"=="" goto uso

set "ARQUIVO_TESTES=%~1"
set "CAMINHO_TESTES=provas\%ARQUIVO_TESTES%"

if not exist "%CAMINHO_TESTES%" (
    echo.
    echo ERRO: arquivo "%ARQUIVO_TESTES%" nao encontrado na pasta provas.
    echo.
    pause
    exit /b 1
)

if not exist "venv\Scripts\python.exe" (
    echo.
    echo ERRO: ambiente virtual nao encontrado.
    echo Execute primeiro:
    echo.
    echo    scripts\install.bat
    echo.
    pause
    exit /b 1
)

echo.
echo Iniciando CodeJudgeC3 com "%ARQUIVO_TESTES%"...
echo.

"venv\Scripts\python.exe" -m streamlit run app.py -- "%CAMINHO_TESTES%"

exit /b %errorlevel%

:uso
echo.
echo Uso:
echo    scripts\rodar.bat ARQUIVO_DE_PROVA
echo.
echo Exemplo:
echo    scripts\rodar.bat testes_parte3.enc
echo.
pause
exit /b 1