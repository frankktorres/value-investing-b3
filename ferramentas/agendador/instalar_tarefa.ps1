# Registra (ou atualiza) a tarefa semanal do monitor de preço no Agendador do Windows.
#   powershell -ExecutionPolicy Bypass -File ferramentas\agendador\instalar_tarefa.ps1
# Sexta 08:00: o último pregão é o de quinta, que chega ao agente de notícias das 18h.
# -StartWhenAvailable: se o PC estava desligado no horário, roda ao ligar.
# Logon INTERATIVO de propósito (AUD-37, 08/10/2026): o .vbs abre um aviso na tela quando o monitor falha
# ou o dado está velho, e o agente de notícias das 18h (Claude Desktop) também só roda com a sessão aberta.
# "Executar sem usuário logado" (S4U) rodaria sem sessão e a falha voltaria a ser silenciosa.
# Remover: Unregister-ScheduledTask -TaskName ValueInvesting-MonitorSemanal -Confirm:$false
$ErrorActionPreference = 'Stop'
$nome = 'ValueInvesting-MonitorSemanal'
$vbs = Join-Path $PSScriptRoot 'monitor_semanal.vbs'
$py = (& python -c "import sys; print(sys.executable)").Trim()
if (-not (Test-Path $py)) { throw "python.exe nao encontrado: $py" }
$acao = New-ScheduledTaskAction -Execute 'wscript.exe' -Argument "`"$vbs`" `"$py`""
$gatilho = New-ScheduledTaskTrigger -Weekly -DaysOfWeek Friday -At '08:00'
$ajustes = New-ScheduledTaskSettingsSet -StartWhenAvailable -AllowStartIfOnBatteries `
    -DontStopIfGoingOnBatteries -ExecutionTimeLimit (New-TimeSpan -Hours 1) -RunOnlyIfNetworkAvailable
Register-ScheduledTask -TaskName $nome -Action $acao -Trigger $gatilho -Settings $ajustes -Force `
    -Description 'Value Investing B3: COTAHIST da semana -> BOLETINS\AAAA-MM-DD-monitor.md (Etapa 4 / F4)' | Out-Null
Get-ScheduledTask -TaskName $nome | Get-ScheduledTaskInfo | Select-Object TaskName, NextRunTime, LastRunTime, LastTaskResult
