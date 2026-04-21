#!/usr/bin/env pwsh
# [CRUX-MK] Layer 0 — Script traegt CRUX-Marker (siehe CRUX-MK.md)
# Deterministischer Kill-Switch fuer Windows.
$ErrorActionPreference = 'Stop'

$root = Join-Path $HOME '.kemmer-grid'
$flag = Join-Path $root 'killed.flag'
$log  = Join-Path $root 'kill-log.jsonl'
New-Item -ItemType Directory -Path $root -Force | Out-Null
if (Test-Path $flag) { exit 0 }

$arg = if ($args.Count -gt 0) { $args[0] } else { '' }
$reason = ''
$costRate = 0.0
foreach ($f in 'api-usage.jsonl','api-log.jsonl','cost-log.jsonl') {
  $p = Join-Path $root $f
  if (Test-Path $p) {
    Get-Content $p | ForEach-Object {
      try {
        $o = $_ | ConvertFrom-Json
        $v = $o.eur_per_hour; if (-not $v) { $v = $o.cost_eur_per_hour }; if (-not $v) { $v = $o.hourly_eur }
        if ([double]$v -gt $costRate) { $costRate = [double]$v }
      } catch {}
    }
    break
  }
}

if ($arg -eq 'panic') { $reason = 'panic' }
elseif ($arg -eq 'cost') { $reason = 'cost' }
elseif ($arg -eq 'manual') { $reason = 'manual' }
elseif ($env:CLAUDE_KILL -eq '1') { $reason = 'env' }
elseif ($costRate -gt 50) { $reason = 'cost>50' }
if (-not $reason) { exit 0 }

$ts = (Get-Date).ToUniversalTime().ToString('s') + 'Z'
"$ts`t$reason" | Set-Content -Path $flag -Encoding utf8

Get-ChildItem Env: | Where-Object { $_.Name -match '(_API_KEY|TOKEN)$' } | ForEach-Object {
  Remove-Item "Env:$($_.Name)" -ErrorAction SilentlyContinue
}
'GEMINI_API_KEY','XAI_API_KEY','ANTHROPIC_API_KEY','OPENAI_API_KEY','GH_TOKEN','GITHUB_TOKEN' | ForEach-Object {
  Remove-Item "Env:$_" -ErrorAction SilentlyContinue
}

schtasks /query /fo csv /nh 2>$null | ConvertFrom-Csv | Where-Object { $_.TaskName -match '\\kemmer-' } | ForEach-Object {
  schtasks /change /tn $_.TaskName /disable | Out-Null
}

$entry = @{ ts=$ts; reason=$reason; cost_eur_per_hour=$costRate; host=$env:COMPUTERNAME } | ConvertTo-Json -Compress
Add-Content -Path $log -Value $entry -Encoding utf8