' Tarefas locais fora do horario (check-up de 21/10/2026, D4). Roda OCULTO e espera terminar (MAQUINA.md).
' Argumento 0: caminho do python.exe; argumento 1: "temporada" (deteccao diaria do ITR, sem --gravar) ou "backup".
' Log em ferramentas\monitor\<modo>.log. Codigo <> 0 abre um aviso na tela (some em 30 min; tarefa interativa de proposito).
' Texto sem acento: o WSH le este arquivo como ANSI.
Option Explicit
Dim fso, sh, ferramentas, py, modo, script, rc
Set fso = CreateObject("Scripting.FileSystemObject")
Set sh = CreateObject("WScript.Shell")
ferramentas = fso.GetParentFolderName(fso.GetParentFolderName(WScript.ScriptFullName))
If WScript.Arguments.Count < 2 Then WScript.Quit 2
py = WScript.Arguments(0)
modo = WScript.Arguments(1)
If modo = "temporada" Then
    script = "temporada.py"
ElseIf modo = "backup" Then
    script = "backup_dados.py"
Else
    WScript.Quit 2
End If
If Not fso.FolderExists(ferramentas & "\monitor") Then fso.CreateFolder(ferramentas & "\monitor")
sh.CurrentDirectory = ferramentas
rc = sh.Run("cmd /c ""set PYTHONIOENCODING=utf-8&& """ & py & """ " & script & " > monitor\" & modo & ".log 2>&1""", 0, True)
If rc <> 0 Then
    sh.Popup "Value Investing - " & modo & " FALHOU (codigo " & rc & ")." & vbCrLf & vbCrLf & _
             "Log: " & ferramentas & "\monitor\" & modo & ".log" & vbCrLf & _
             "Rodar de novo: cd ferramentas && python " & script, 1800, "Value Investing - " & modo, 48
End If
WScript.Quit rc
