# Registra (ou atualiza) as tarefas locais fora do horario (check-up de 21/10/2026, D4):
#   ValueInvesting-TemporadaDiaria : todo dia 06:30, de 22/10 a 21/11/2026 — temporada.py SEM --gravar (detecta o ITR 3T26,
#                                    escreve BOLETINS\<dia>-temporada.md so quando alguem publicou; ~6 min medido em 21/10).
#   ValueInvesting-BackupSemanal   : domingo 07:30 — backup_dados.py (OneDrive; dados\privado\ fica de fora).
#   ValueInvesting-ConferirNoite   : todo dia 07:15 (22/10/2026) — conferir_noite.py: suite da rodada da nuvem (ramo claude/*)
#                                    com os dados locais; verde e sem golden/doutrina -> junta no master. ~5 min.
#   powershell -ExecutionPolicy Bypass -File ferramentas\agendador\instalar_tarefas_noite.ps1
# -StartWhenAvailable: PC desligado no horario → roda ao ligar. Logon interativo de proposito (aviso de falha na tela, AUD-37).
# Remover: Unregister-ScheduledTask -TaskName ValueInvesting-TemporadaDiaria -Confirm:$false (idem BackupSemanal)
$ErrorActionPreference = 'Stop'
$vbs = Join-Path $PSScriptRoot 'noite.vbs'
$py = (& python -c "import sys; print(sys.executable)").Trim()
if (-not (Test-Path $py)) { throw "python.exe nao encontrado: $py" }
$ajustes = New-ScheduledTaskSettingsSet -StartWhenAvailable -AllowStartIfOnBatteries `
    -DontStopIfGoingOnBatteries -ExecutionTimeLimit (New-TimeSpan -Hours 1) -RunOnlyIfNetworkAvailable

$diaria = New-ScheduledTaskTrigger -Daily -At '2026-10-22T06:30:00'
$diaria.EndBoundary = '2026-11-21T23:59:59'
Register-ScheduledTask -TaskName 'ValueInvesting-TemporadaDiaria' -Settings $ajustes -Trigger $diaria -Force `
    -Action (New-ScheduledTaskAction -Execute 'wscript.exe' -Argument "`"$vbs`" `"$py`" temporada") `
    -Description 'Value Investing B3: detecta o ITR 3T26 todo dia (sem --gravar) -> BOLETINS\AAAA-MM-DD-temporada.md' | Out-Null

$semanal = New-ScheduledTaskTrigger -Weekly -DaysOfWeek Sunday -At '07:30'
Register-ScheduledTask -TaskName 'ValueInvesting-BackupSemanal' -Settings $ajustes -Trigger $semanal -Force `
    -Action (New-ScheduledTaskAction -Execute 'wscript.exe' -Argument "`"$vbs`" `"$py`" backup") `
    -Description 'Value Investing B3: backup_dados.py (OneDrive + git bundle; sem dados\privado\)' | Out-Null

$manha = New-ScheduledTaskTrigger -Daily -At '07:15'
Register-ScheduledTask -TaskName 'ValueInvesting-ConferirNoite' -Settings $ajustes -Trigger $manha -Force `
    -Action (New-ScheduledTaskAction -Execute 'wscript.exe' -Argument "`"$vbs`" `"$py`" conferir") `
    -Description 'Value Investing B3: testa a rodada da nuvem (claude/*) com os dados locais e junta no master se verde' | Out-Null

Get-ScheduledTask -TaskName 'ValueInvesting-*' | Get-ScheduledTaskInfo | Select-Object TaskName, NextRunTime, LastRunTime, LastTaskResult
