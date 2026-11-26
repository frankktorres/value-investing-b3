@echo off
rem Regera "UPLOAD CLAUDE DESKTOP" a partir do repo (so le o repo; so escreve nessa pasta e em _historico\).
cd /d "%~dp0ferramentas"
python -m desktop.atualizar
echo.
echo Pronto. A lista do que subir/trocar/apagar no Claude Desktop esta no fim de "UPLOAD CLAUDE DESKTOP\MANIFESTO.txt".
echo Nao suba o MANIFESTO.txt; o COLAR-NO-CAMPO-INSTRUCOES.txt vai no campo Instrucoes do projeto.
pause
