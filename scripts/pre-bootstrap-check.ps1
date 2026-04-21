#!/usr/bin/env pwsh
# [CRUX-MK] Layer 0 — Script traegt CRUX-Marker (siehe CRUX-MK.md)
# Standalone-Diagnose fuer Windows.
$ErrorActionPreference = 'Stop'

$hostName = $env:COMPUTERNAME
$ts = (Get-Date).ToUniversalTime().ToString('yyyyMMddTHHmmssZ')
$role = if ($env:MACHINE_ROLE) { $env:MACHINE_ROLE } else { 'worker' }
$rows = [System.Collections.Generic.List[object]]::new()
$overall = 0

function Add-Row($Check,$Status,$Detail){ if($Status -ne 'OK'){ $script:overall = 1 }; $script:rows.Add([pscustomobject]@{Check=$Check;Status=$Status;Detail=$Detail}) | Out-Null }
function Test-Cli($Name,$Cmd){
  $gc = Get-Command $Cmd -ErrorAction SilentlyContinue
  if(-not $gc){ Add-Row "CLI:$Name" 'MISSING' 'nicht gefunden'; return }
  $ver = try { (& $Cmd --version 2>$null | Select-Object -First 1) } catch { 'gefunden' }
  $status = 'OK'
  if($Name -eq 'python3'){
    $pv = try { (& $Cmd -c 'import sys; print(".".join(map(str,sys.version_info[:3])))') } catch { '0.0.0' }
    if([version]$pv -lt [version]'3.12.0'){ $status='PARTIAL' }
  }
  if($Name -eq 'node'){
    $nv = try { (& $Cmd -p "process.versions.node") } catch { '0.0.0' }
    $major = [int]($nv.Split('.')[0]); if($major -lt 20 -or ($major % 2) -ne 0){ $status='PARTIAL' }
  }
  Add-Row "CLI:$Name" $status $ver
}

$hub = $null
foreach($p in @($env:BRANCH_HUB,'G:\branch-hub','G:\Meine Ablage\Claude-Knowledge-System\branch-hub')){
  if($p -and (Test-Path (Join-Path $p 'BEACON.md'))){ $hub = $p; break }
}
if(-not $hub){
  $f = Get-ChildItem G:\ -Filter BEACON.md -Recurse -Depth 5 -ErrorAction SilentlyContinue | Where-Object { $_.FullName -match 'branch-hub\\BEACON\.md$' } | Select-Object -First 1
  if($f){ $hub = $f.Directory.FullName }
}
if($hub){ Add-Row 'Drive/Branch-Hub' 'OK' $hub } else { Add-Row 'Drive/Branch-Hub' 'MISSING' 'BEACON.md nicht gefunden' }

'git','gh','python3','node','codex','gemini','uv','ollama' | ForEach-Object { Test-Cli $_ $_ }

'GEMINI_API_KEY','XAI_API_KEY','ANTHROPIC_API_KEY','MACHINE_ROLE' | ForEach-Object {
  if((Get-Item "Env:$_" -ErrorAction SilentlyContinue).Value){ Add-Row "ENV:$_" 'OK' 'gesetzt' } else { Add-Row "ENV:$_" 'MISSING' 'nicht gesetzt' }
}

if(gh auth status *> $null){ Add-Row 'gh auth' 'OK' 'auth aktiv' } else { Add-Row 'gh auth' 'PARTIAL' 'gh nicht eingeloggt' }

$tasks = schtasks /query /fo csv /nh 2>$null | ConvertFrom-Csv | Where-Object { $_.TaskName -match 'DF-|NLM-|Claude-' }
if($role -eq 'primary'){
  $need = @('DF-','NLM-','Claude-')
  $ok = ($need | Where-Object { $tasks.TaskName -match $_ }).Count
  if($ok -eq 3){ Add-Row "Scheduler[$role]" 'OK' 'alle Master-Jobs da' } else { Add-Row "Scheduler[$role]" 'MISSING' 'Master-Jobs unvollstaendig' }
} else {
  if(($tasks | Measure-Object).Count -eq 0){ Add-Row "Scheduler[$role]" 'OK' 'keine Master-Jobs' } else { Add-Row "Scheduler[$role]" 'PARTIAL' 'unerwartete Jobs gefunden' }
}

$rulesDir = Join-Path $HOME '.claude\rules'
$rules = @(Get-ChildItem $rulesDir -Filter *.md -ErrorAction SilentlyContinue)
if($rules.Count -ge 40){ Add-Row 'Rules' 'OK' "$($rules.Count) Dateien" }
elseif($rules.Count -gt 0){ Add-Row 'Rules' 'PARTIAL' "$($rules.Count) Dateien" }
else{ Add-Row 'Rules' 'MISSING' '0 Dateien' }

$ks = Join-Path (Get-Location) 'kill-switch.ps1'
if(Test-Path $ks){ Add-Row 'kill-switch.ps1' 'OK' $ks } else { Add-Row 'kill-switch.ps1' 'MISSING' 'nicht gefunden' }

'| Check | Status | Detail |'
'|---|---|---|'
$rows | ForEach-Object { "| $($_.Check) | $($_.Status) | $($_.Detail) |" }

if($hub){
  $statusDir = Join-Path $hub 'status'
  New-Item -ItemType Directory -Path $statusDir -Force | Out-Null
  $out = Join-Path $statusDir "$hostName-diagnose-$ts.json"
  [pscustomobject]@{host=$hostName;role=$role;ts=$ts;ok=($overall -eq 0);checks=$rows} | ConvertTo-Json -Depth 6 | Set-Content -Path $out -Encoding utf8
}

exit $overall