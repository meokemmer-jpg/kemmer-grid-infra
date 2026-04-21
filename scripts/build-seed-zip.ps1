# [CRUX-MK] Layer 0 — Build Seed-Export-ZIP for Worker/Mac-Instances
# Martin-Direktive 2026-04-21 "ich will die anderen PCs und den Mac fertig machen"
#
# Aufruf (als normaler User):
#   powershell -ExecutionPolicy Bypass -File scripts/build-seed-zip.ps1
#
# Output:
#   G:\Meine Ablage\Seed-Exports\kemmer-seed-export-YYYY-MM-DD.zip
#   Enthaelt: ~/.claude/CLAUDE.md + rules/ + skills/ + scripts/
#
# rho-Impact: Martin spart manuelles ZIP-Bauen pro Worker-Sync (~15-30 Min pro Worker)
# K_0: geschuetzt (settings.json EXCLUDED — keine Secret-Exposure)
# Q_0: Worker bekommen immer aktuellsten Kemmer-Stand in 1 Befehl

$ErrorActionPreference = "Stop"

$Source = "$env:USERPROFILE\.claude"
$DestDir = "G:\Meine Ablage\Seed-Exports"
$Date = Get-Date -Format "yyyy-MM-dd"
$Dest = Join-Path $DestDir "kemmer-seed-export-$Date.zip"

Write-Host "[CRUX-MK] Building Seed-Export-ZIP..." -ForegroundColor Cyan

# Ensure destination
if (-not (Test-Path $DestDir)) {
    New-Item -ItemType Directory -Path $DestDir -Force | Out-Null
    Write-Host "  Created: $DestDir" -ForegroundColor Gray
}

# Items to include (settings.json EXCLUDED — contains machine-specific secrets)
$Items = @(
    (Join-Path $Source "CLAUDE.md"),
    (Join-Path $Source "rules"),
    (Join-Path $Source "skills"),
    (Join-Path $Source "scripts")
) | Where-Object { Test-Path $_ }

Write-Host "  Source items: $($Items.Count)" -ForegroundColor Gray
foreach ($item in $Items) {
    Write-Host "    - $(Split-Path $item -Leaf)" -ForegroundColor Gray
}

# Compress (overwrite)
if (Test-Path $Dest) {
    Remove-Item $Dest -Force
    Write-Host "  Removed old ZIP" -ForegroundColor Gray
}

Compress-Archive -Path $Items -DestinationPath $Dest -CompressionLevel Optimal -Force

# Stats
$Size = (Get-Item $Dest).Length / 1MB
$RulesCount = (Get-ChildItem (Join-Path $Source "rules\*.md")).Count
$SkillsCount = (Get-ChildItem (Join-Path $Source "skills") -Directory).Count

Write-Host ""
Write-Host "[CRUX-MK] Seed-Export complete" -ForegroundColor Green
Write-Host ("  ZIP:    {0}" -f $Dest) -ForegroundColor Cyan
Write-Host ("  Size:   {0:N2} MB" -f $Size) -ForegroundColor Cyan
Write-Host ("  Rules:  {0}" -f $RulesCount) -ForegroundColor Cyan
Write-Host ("  Skills: {0} folders" -f $SkillsCount) -ForegroundColor Cyan
Write-Host ""
Write-Host "  Worker/Mac-Install via:" -ForegroundColor Yellow
Write-Host "    Expand-Archive -Path `"$Dest`" -DestinationPath `"`$env:USERPROFILE\.claude`" -Force" -ForegroundColor Yellow
Write-Host ""
Write-Host "  Or: git clone https://github.com/meokemmer-jpg/kemmer-grid-infra.git" -ForegroundColor Yellow

# === P4 Self-Healing: Sync .version fuer rules-verify ===
# (Cross-LLM-HARDENED: signierter Git-Tag ist Authoritative fuer Rules-Hash)
$VersionFile = Join-Path $Source "rules\.version"
$RepoDir = Join-Path $env:USERPROFILE "Projects\kemmer-grid-infra"
if ((Test-Path $RepoDir) -and (Test-Path "$RepoDir\.git")) {
    # Letzter seed-v* Tag ermitteln
    $LatestTag = (git -C $RepoDir tag --list "seed-v*" | Sort-Object | Select-Object -Last 1)
    if ($LatestTag) {
        Set-Content -Path $VersionFile -Value $LatestTag -NoNewline -Encoding utf8
        Write-Host ""
        Write-Host "  .version updated: $VersionFile" -ForegroundColor Cyan
        Write-Host "  Current tag: $LatestTag" -ForegroundColor Cyan
        Write-Host ""
        Write-Host "  Verify rules-hash via:" -ForegroundColor Yellow
        Write-Host "    python $RepoDir\scripts\self-healing\rules-verify.py" -ForegroundColor Yellow
    } else {
        Write-Host ""
        Write-Host "  NOTE: No seed-v* git tag found. Create via:" -ForegroundColor Yellow
        Write-Host "    cd $RepoDir && git tag -a seed-v$Date-a -m 'Seed-Release' && git push origin seed-v$Date-a" -ForegroundColor Yellow
    }
}
