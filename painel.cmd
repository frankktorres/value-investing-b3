@echo off
rem Tela da Mesa (somente leitura): painel  ->  http://127.0.0.1:8765/   ·   painel --exportar regera os dados antes
pushd "%~dp0ferramentas"
python -m painel %*
set ERRO=%ERRORLEVEL%
popd
exit /b %ERRO%
