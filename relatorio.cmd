@echo off
rem Relatorio por empresa (fase 1): relatorio BBSE3  ->  RELATORIOS\BBSE3-<data>.md
pushd "%~dp0ferramentas"
python -m relatorio %*
set ERRO=%ERRORLEVEL%
popd
exit /b %ERRO%
