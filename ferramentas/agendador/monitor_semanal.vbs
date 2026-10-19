' Monitor semanal de preço do hall (Etapa 4 / F4).
' Roda `python monitor_semanal.py` OCULTO e espera terminar (MAQUINA.md: job lançado pelo Agendador
' com WScript.Shell.Run(cmd, 0, True); janela visível que alguém fecha = morte do job).
' Argumento 0: caminho do python.exe (gravado pelo instalar_tarefa.ps1).
' Saída em ferramentas\monitor\ultimo.log; o código de saída vira o LastTaskResult da tarefa.
' AUD-37: código ≠ 0 abre um aviso NA TELA (20 = dado velho, 21 = exceção, outro = python nem rodou). A tarefa
' é "Interativa" de propósito: sem sessão aberta o aviso não aparece e a falha volta a ser silenciosa.
' O aviso some sozinho em 50 min (a tarefa tem limite de 1 h). Texto sem acento: o WSH lê este arquivo como ANSI.
Option Explicit
Dim fso, sh, ferramentas, py, cmd, rc, msg
Set fso = CreateObject("Scripting.FileSystemObject")
Set sh = CreateObject("WScript.Shell")
ferramentas = fso.GetParentFolderName(fso.GetParentFolderName(WScript.ScriptFullName))
py = "python"
If WScript.Arguments.Count > 0 Then py = WScript.Arguments(0)
If Not fso.FolderExists(ferramentas & "\monitor") Then fso.CreateFolder(ferramentas & "\monitor")
sh.CurrentDirectory = ferramentas
cmd = "cmd /c ""set PYTHONIOENCODING=utf-8&& """ & py & """ monitor_semanal.py > monitor\ultimo.log 2>&1"""
rc = sh.Run(cmd, 0, True)
' Temporada (19/10/2026): detecta ITR novo toda sexta; sem --gravar so escreve boletim; sai 0 sem ITR novo.
' O codigo dela nao muda o rc do monitor; log em monitor\temporada.log.
sh.Run "cmd /c ""set PYTHONIOENCODING=utf-8&& """ & py & """ temporada.py > monitor\temporada.log 2>&1""", 0, True
If rc <> 0 Then
    If rc = 20 Then
        msg = "Monitor semanal: DADO VELHO - o ultimo pregao tem mais de 7 dias (o download da B3 falhou?)."
    ElseIf rc = 21 Then
        msg = "Monitor semanal FALHOU - o boletim de hoje em BOLETINS\ comeca com 'MONITOR FALHOU' e traz o erro."
    Else
        msg = "Monitor semanal FALHOU antes de rodar (codigo " & rc & ") - nenhum boletim novo foi escrito."
    End If
    msg = msg & vbCrLf & vbCrLf & "Log: " & ferramentas & "\monitor\ultimo.log" & vbCrLf & _
          "Rodar de novo: cd ferramentas && python monitor_semanal.py"
    sh.Popup msg, 3000, "Value Investing - monitor semanal", 48
End If
WScript.Quit rc
