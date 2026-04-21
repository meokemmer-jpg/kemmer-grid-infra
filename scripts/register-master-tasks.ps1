# [CRUX-MK] Layer 0 — Register Master-Infrastructure Scheduled-Tasks
# Martin-Direktive 2026-04-21 (Handoff Prio 4)
#
# Aufruf (als normaler User):
#   powershell -ExecutionPolicy Bypass -File scripts/register-master-tasks.ps1
#
# Registriert:
#   Kemmer-Heartbeat        alle 15 Min  -> kemmer-heartbeat.sh
#   Kemmer-KillSwitch-Watchdog  alle 5 Min -> kill-switch-watchdog.sh
#
# CRUX-Impact: +I_min (Grid-Health-Monitoring) + Kill-Switch-Enforcement
# rho: Praevention von Grid-Drift-Kosten (geschaetzt +5-10k EUR/J)

$ErrorActionPreference = "Stop"

$GitBash = "C:\Program Files\Git\bin\bash.exe"
if (-not (Test-Path $GitBash)) {
    Write-Host "[CRUX-MK] ERROR: Git-Bash not found at $GitBash" -ForegroundColor Red
    Write-Host "  Install Git for Windows or anpassen GitBash-Path" -ForegroundColor Red
    exit 1
}

$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$HeartbeatScript = Join-Path $ScriptDir "kemmer-heartbeat.sh" | ForEach-Object { $_.Replace('\', '/') }
$WatchdogScript = Join-Path $ScriptDir "kill-switch-watchdog.sh" | ForEach-Object { $_.Replace('\', '/') }

# Unify path for bash-exec
$HeartbeatBash = "/c" + $HeartbeatScript.Substring(2)
$WatchdogBash = "/c" + $WatchdogScript.Substring(2)

Write-Host "[CRUX-MK] Registering Master-Infrastructure Scheduled-Tasks..." -ForegroundColor Cyan

# --- Task 1: Heartbeat ---
Write-Host "  Registering Kemmer-Heartbeat (every 15 min)..."
$TaskAction1 = New-ScheduledTaskAction -Execute $GitBash -Argument "-c `"$HeartbeatBash`""
$TaskTrigger1 = New-ScheduledTaskTrigger -Once -At (Get-Date).AddMinutes(1) `
    -RepetitionInterval (New-TimeSpan -Minutes 15)
$TaskSettings1 = New-ScheduledTaskSettingsSet -AllowStartIfOnBatteries -DontStopIfGoingOnBatteries `
    -ExecutionTimeLimit (New-TimeSpan -Minutes 5) -MultipleInstances IgnoreNew
Register-ScheduledTask -TaskName "Kemmer-Heartbeat" -Action $TaskAction1 -Trigger $TaskTrigger1 `
    -Settings $TaskSettings1 -Description "[CRUX-MK] Grid-Health Heartbeat every 15 min" `
    -Force | Out-Null
Write-Host "  [OK] Kemmer-Heartbeat registered" -ForegroundColor Green

# --- Task 2: Kill-Switch-Watchdog ---
Write-Host "  Registering Kemmer-KillSwitch-Watchdog (every 5 min)..."
$TaskAction2 = New-ScheduledTaskAction -Execute $GitBash -Argument "-c `"$WatchdogBash`""
$TaskTrigger2 = New-ScheduledTaskTrigger -Once -At (Get-Date).AddMinutes(1) `
    -RepetitionInterval (New-TimeSpan -Minutes 5)
$TaskSettings2 = New-ScheduledTaskSettingsSet -AllowStartIfOnBatteries -DontStopIfGoingOnBatteries `
    -ExecutionTimeLimit (New-TimeSpan -Minutes 2) -MultipleInstances IgnoreNew
Register-ScheduledTask -TaskName "Kemmer-KillSwitch-Watchdog" -Action $TaskAction2 -Trigger $TaskTrigger2 `
    -Settings $TaskSettings2 -Description "[CRUX-MK] Kill-Switch Watchdog every 5 min" `
    -Force | Out-Null
Write-Host "  [OK] Kemmer-KillSwitch-Watchdog registered" -ForegroundColor Green

Write-Host ""
Write-Host "[CRUX-MK] Registration complete." -ForegroundColor Green
Write-Host "  Verify:  schtasks /query /tn Kemmer-Heartbeat" -ForegroundColor Cyan
Write-Host "  Verify:  schtasks /query /tn Kemmer-KillSwitch-Watchdog" -ForegroundColor Cyan
Write-Host "  Logs:    ~/.kemmer-grid/heartbeat.jsonl + grid-health.json + kill-audit.jsonl" -ForegroundColor Cyan
Write-Host ""
Write-Host "  Remove both:  schtasks /delete /tn Kemmer-Heartbeat /f" -ForegroundColor Yellow
Write-Host "                schtasks /delete /tn Kemmer-KillSwitch-Watchdog /f" -ForegroundColor Yellow
