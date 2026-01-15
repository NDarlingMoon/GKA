@echo off
title Iniciar Script GKA
cd /d "%~dp0"

echo [SISTEMA] Iniciando processamento do GKA...
echo [SISTEMA] Verificando ambiente e executando celulas...
echo.

jupyter nbconvert --to notebook --execute script_gka.ipynb --inplace

if %errorlevel% neq 0 (
    echo.
    echo [ERRO] Ocorreu uma falha durante a execucao do Notebook.
    echo Verifique se os arquivos de entrada estao no caminho correto.
) else (
    echo.
    echo [SUCESSO] Relatorio gerado e Notebook atualizado!
)

echo.
pause