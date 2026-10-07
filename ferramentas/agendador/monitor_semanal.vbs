' Monitor semanal de preço do hall (Etapa 4 / F4).
' Roda `python monitor_semanal.py` OCULTO e espera terminar (MAQUINA.md: job lançado pelo Agendador
' com WScript.Shell.Run(cmd, 0, True); janela visível que alguém fecha = morte do job).
' Argumento 0: caminho do python.exe (gravado pelo instalar_tarefa.ps1).
' Saída em ferramentas\monitor\ultimo.log; o código de saída vira o LastTaskResult da tarefa.
Option Explicit
Dim fso, sh, ferramentas, py, cmd, rc
Set fso = CreateObject("Scripting.FileSystemObject")
Set sh = CreateObject("WScript.Shell")
ferramentas = fso.GetParentFolderName(fso.GetParentFolderName(WScript.ScriptFullName))
py = "python"
If WScript.Arguments.Count > 0 Then py = WScript.Arguments(0)
If Not fso.FolderExists(ferramentas & "\monitor") Then fso.CreateFolder(ferramentas & "\monitor")
sh.CurrentDirectory = ferramentas
cmd = "cmd /c ""set PYTHONIOENCODING=utf-8&& """ & py & """ monitor_semanal.py > monitor\ultimo.log 2>&1"""
rc = sh.Run(cmd, 0, True)
WScript.Quit rc
