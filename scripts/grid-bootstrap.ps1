#!/usr/bin/env pwsh
# Idempotenter Grid-Bootstrap fuer Windows.
[CmdletBinding()]
param(
  [Parameter(Mandatory=$true)][ValidateSet('worker','primary','validator','local-inference')] [string]$role,
  [switch]$resume,
  [switch]$dryRun
)
$ErrorActionPreference = 'Stop'

$root = Join-Path $HOME '.kemmer-grid'
$repo = Join-Path $root 'kemmer-grid-infra'
$hostName = $env:COMPUTERNAME
$ts = (Get-Date).ToUniversalTime().ToString('s') + 'Z'
$attestFile = Join-Path $root 'state-attestation.json'
$statusFile = Join-Path $root "$hostName.status.json"
New-Item -ItemType Directory -Path $root -Force | Out-Null

function Add-Attest($Step,$Verdict,$Detail){
  $arr = @()
  if(Test-Path $attestFile){ try { $arr = Get-Content $attestFile -Raw | ConvertFrom-Json } catch { $arr = @() } }
  $arr = @($arr) + [pscustomobject]@{ ts=$ts; step=$Step; verdict=$Verdict; detail=$Detail }
  $arr | ConvertTo-Json -Depth 6 | Set-Content -Path $attestFile -Encoding utf8
}
function Get-VersionLine($cmd){ try { (& $cmd --version 2>$null | Select-Object -First 1) } catch { '' } }
function Get-CmdHash($cmd){ $c = Get-Command $cmd -ErrorAction SilentlyContinue; if($c){ (Get-FileHash $c.Source -Algorithm SHA256).Hash.ToLower() } else { '' } }
function Test-Need($haveVer,$needVer,$haveSha,$needSha){ if(-not $haveVer){ return $true }; if($needVer -and $haveVer -notmatch [regex]::Escape($needVer)){ return $true }; if($needSha -and $haveSha -ne $needSha.ToLower()){ return $true }; return $false }
function Update-Status([double]$score){
  $status = [pscustomobject]@{ host=$hostName; role=$role; ts=$ts; grid_doctor_score=[math]::Round($score,2) }
  $status | ConvertTo-Json -Depth 4 | Set-Content -Path $statusFile -Encoding utf8
  if($script:hub){ $dir = Join-Path $script:hub 'status'; New-Item -ItemType Directory -Path $dir -Force | Out-Null; Copy-Item $statusFile (Join-Path $dir "$hostName.json") -Force }
  if(Test-Path (Join-Path $repo '.git')){
    $dir = Join-Path $repo 'status'; New-Item -ItemType Directory -Path $dir -Force | Out-Null
    Copy-Item $statusFile (Join-Path $dir "$hostName.json") -Force
    git -C $repo add "status/$hostName.json" *> $null
    git -C $repo commit -m "status($hostName): $role @ $ts" *> $null
    git -C $repo push *> $null
  }
}
function Ensure-AdminOnce{
  $isAdmin = ([Security.Principal.WindowsPrincipal][Security.Principal.WindowsIdentity]::GetCurrent()).IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)
  if($isAdmin -or $dryRun){ return }
  if($env:KEMMER_BOOTSTRAP_ELEVATED -eq '1'){ return }
  $argList = @('-NoProfile','-ExecutionPolicy','Bypass','-File',$PSCommandPath,'-role',$role)
  if($resume){ $argList += '--resume' }; if($dryRun){ $argList += '--dryRun' }
  $psi = Start-Process powershell -Verb RunAs -Wait -PassThru -ArgumentList $argList -WorkingDirectory (Get-Location)
  exit $psi.ExitCode
}
function Install-Package($item){
  if($dryRun){ Write-Host "DRY install $($item.name)"; return }
  if($item.winget -and (Get-Command winget -ErrorAction SilentlyContinue)){ winget install --id $item.winget --exact --silent --accept-package-agreements --accept-source-agreements; return }
  if($item.scoop -and (Get-Command scoop -ErrorAction SilentlyContinue)){ scoop install $item.scoop; return }
  if($item.choco -and (Get-Command choco -ErrorAction SilentlyContinue)){ choco install $item.choco -y; return }
  throw "Kein Paketmanager-Eintrag fuer $($item.name)"
}

$script:hub = $null
foreach($p in @($env:BRANCH_HUB,'G:\branch-hub','G:\Meine Ablage\Claude-Knowledge-System\branch-hub')){
  if($p -and (Test-Path (Join-Path $p 'BEACON.md'))){ $script:hub = $p; break }
}
if(-not (Test-Path $repo)){ New-Item -ItemType Directory -Path $repo -Force | Out-Null }
if(Test-Path (Join-Path $repo '.git')){ if(-not $dryRun){ git -C $repo pull --ff-only } }
else { if($dryRun){ Write-Host 'DRY git clone kemmer-grid-infra' } else { git clone https://github.com/meokemmer-jpg/kemmer-grid-infra.git $repo } }

$manifest = $null
$localManifest = if($script:hub){ Join-Path $script:hub "handoffs\manifest-$role.json" } else { $null }
$repoManifest = Join-Path $repo "manifests\manifest-$role.json"
if($localManifest -and (Test-Path $localManifest)){ $manifest = $localManifest }
elseif(Test-Path $repoManifest){ $manifest = $repoManifest }
else { Add-Attest 'manifest' 'FAIL' "manifest-$role.json fehlt"; exit 1 }

$doc = Get-Content $manifest -Raw | ConvertFrom-Json
$items = @($doc.tools + $doc.modules); if($items.Count -eq 0 -and $doc -is [System.Array]){ $items = @($doc) }
Ensure-AdminOnce
Add-Attest 'bootstrap' 'OK' "role=$role;resume=$resume;dry=$dryRun"

$total = 0; $ok = 0
foreach($item in $items){
  $total++
  $haveVer = Get-VersionLine $item.command
  $haveSha = Get-CmdHash $item.command
  if(-not (Test-Need $haveVer $item.version $haveSha $item.sha256)){
    $ok++; Add-Attest $item.name 'OK' 'bereits vorhanden'
  } else {
    Add-Attest $item.name 'APPLY' 'installiere/aktualisiere'
    Install-Package $item
    $haveVer = Get-VersionLine $item.command
    $haveSha = Get-CmdHash $item.command
    if(Test-Need $haveVer $item.version $haveSha $item.sha256){ Add-Attest $item.name 'FAIL' 'assert-after-write fehlgeschlagen'; Update-Status (($ok / $total) * 100); exit 1 }
    $ok++; Add-Attest $item.name 'OK' 'assert-after-write erfolgreich'
  }
  Update-Status (($ok / $total) * 100)
}

$golden = @(
  (Join-Path $repo 'scripts\golden-task-suite.ps1'),
  (Join-Path $repo 'scripts\golden-task-suite.sh'),
  (Join-Path (Get-Location) 'golden-task-suite.ps1')
) | Where-Object { Test-Path $_ } | Select-Object -First 1
if(-not $golden){ Add-Attest 'capability' 'FAIL' 'golden-task-suite fehlt'; exit 1 }
if($dryRun){ Add-Attest 'capability' 'SKIP' $golden }
elseif($golden -like '*.ps1'){ & $golden; Add-Attest 'capability' 'OK' $golden }
else { bash $golden; Add-Attest 'capability' 'OK' $golden }

Update-Status (($ok / [math]::Max($total,1)) * 100)
Add-Attest 'grid-doctor' 'OK' ([math]::Round((($ok / [math]::Max($total,1)) * 100),2))