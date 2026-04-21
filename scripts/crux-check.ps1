#!/usr/bin/env pwsh
# [CRUX-MK] Layer 0
# Windows-Portierung von crux-check.sh. Gleiche Argumente, gleiche Exit-Codes.
# rho-Impact:       Infrastruktur-Erhalt, verhindert Grid-Drift
# K_0/Q_0/I_min:    Aktive Durchsetzung aller drei Nebenbedingungen
# Wargame-Status:   alignment_passed (Martin-Direktive 2026-04-21)

param(
  [string]$Action = "",
  [string]$EstimatedRho = "",
  [string]$K0Risk = "unknown",
  [string]$Q0Risk = "unknown",
  [string]$IMin = "unknown",
  [string]$LMartin = "unknown",
  [string]$Wargame = "none",
  [string]$Stage = "",
  [switch]$DryRun,
  [switch]$Verbose,
  [switch]$Help
)

if ($Help) {
  @"
crux-check.ps1 [CRUX-MK] Layer 0
Usage:
  crux-check.ps1 -Action "install ollama" -EstimatedRho "+10-30 EUR/M" `
    -K0Risk low -Q0Risk none -IMin positive -LMartin positive `
    -Wargame adversarial_passed

Parameter analog zu crux-check.sh. Exit: 0=PASS, 1=REJECT, 2=WARN.
"@
  exit 0
}

$ErrorActionPreference = 'Stop'
$CruxLogDir = Join-Path $HOME '.kemmer-grid'
$CruxLogFile = Join-Path $CruxLogDir 'crux-events.jsonl'
$CruxVersion = 'v1.0'
New-Item -ItemType Directory -Path $CruxLogDir -Force | Out-Null

# Pflicht-Felder
if (-not $Action) { Write-Error "[CRUX-MK] --Action ist Pflicht"; exit 2 }
if (-not $EstimatedRho) { Write-Error "[CRUX-MK] --EstimatedRho ist Pflicht (keine Aktion ohne rho-Schaetzung)"; exit 2 }

# Kill-Switch-Check
$KillFlag = Join-Path $CruxLogDir 'killed.flag'
if (Test-Path $KillFlag) {
  Write-Host "[CRUX-MK] Kill-Switch aktiv. Alle Aktionen gestoppt."
  exit 1
}

# Nebenbedingungs-Checks
$Verdict = 'PASS'
$Reasons = @()

if ($K0Risk -eq 'high') {
  $Verdict = 'REJECT'
  $Reasons += 'K_0 high risk: Kapital-Substanzverzehr moeglich'
}
if ($Q0Risk -eq 'high') {
  $Verdict = 'REJECT'
  $Reasons += 'Q_0 high risk: Qualitaet/Familie-Degradation moeglich'
}
if ($IMin -eq 'negative') {
  $Verdict = 'REJECT'
  $Reasons += 'I_min negative: Ordnungsminimum unterschritten'
}

if ($EstimatedRho -match 'unclear|unknown|n/a') {
  if ($Verdict -eq 'PASS') {
    $Verdict = 'WARN'
    $Reasons += 'rho unklar - Martin-Review empfohlen'
  }
}

if ($Wargame -eq 'none' -and ($K0Risk -eq 'medium' -or $Q0Risk -eq 'medium')) {
  if ($Verdict -eq 'PASS') {
    $Verdict = 'WARN'
    $Reasons += 'Substantielle Aktion ohne Wargame-Haertung'
  }
}

# Output
$Ts = (Get-Date).ToUniversalTime().ToString('yyyy-MM-ddTHH:mm:ssZ')
$Hostname = $env:COMPUTERNAME
Write-Host "[CRUX-MK] Layer-0-Check $CruxVersion"
Write-Host "  Action:           $Action"
Write-Host "  rho-Estimate:     $EstimatedRho"
Write-Host "  K_0-Risk:         $K0Risk"
Write-Host "  Q_0-Risk:         $Q0Risk"
Write-Host "  I_min-Impact:     $IMin"
Write-Host "  L_Martin-Impact:  $LMartin"
Write-Host "  Wargame-Status:   $Wargame"
if ($Stage) { Write-Host "  Stage:            $Stage" }
Write-Host ""
Write-Host "VERDICT: $Verdict"

if ($Reasons.Count -gt 0) {
  Write-Host "Reasons:"
  foreach ($r in $Reasons) { Write-Host "  - $r" }
}

# Logging
if (-not $DryRun) {
  $Entry = @{
    ts = $Ts; host = $Hostname; version = $CruxVersion
    action = $Action; rho_estimate = $EstimatedRho
    k0_risk = $K0Risk; q0_risk = $Q0Risk
    i_min_impact = $IMin; l_martin_impact = $LMartin
    wargame_status = $Wargame; stage = $Stage
    verdict = $Verdict; reasons = ($Reasons -join '; ')
  } | ConvertTo-Json -Compress
  Add-Content -Path $CruxLogFile -Value $Entry -Encoding utf8
}

switch ($Verdict) {
  'PASS'   { exit 0 }
  'WARN'   { exit 2 }
  'REJECT' { exit 1 }
  default  { exit 2 }
}
