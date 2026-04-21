# DF-06 Light-Pass (alle 30 Min, deterministic, kein LLM-Call)
# PowerShell 5.1 + 7 kompatibel (Hashtable + ConvertTo-Json statt Backtick-Escapes)

$DF_DIR = "C:\Users\marti\.claude\skills\archon-roadmap-orchestrator\dark-factory\DF-06"
$SCRIPTS = "C:\Users\marti\.claude\skills\archon-roadmap-orchestrator\scripts"
$AUDIT = "G:\Meine Ablage\Claude-Knowledge-System\branch-hub\audit\dark-factory.jsonl"
$BULLETIN = "G:\Meine Ablage\Claude-Knowledge-System\branch-hub\BULLETIN.md"

# 1. Kill-Switch-Check
if (Test-Path "$DF_DIR\DISABLED") {
    $entry = @{ ts = (Get-Date -Format o); df = "DF-06"; op = "light-pass"; status = "skipped-disabled" } | ConvertTo-Json -Compress
    Add-Content -Path $AUDIT -Value $entry
    exit 0
}

# 2. Fail-Counter-Check
$failCounter = 0
if (Test-Path "$DF_DIR\fail-counter") {
    $failCounter = [int]((Get-Content "$DF_DIR\fail-counter" -Raw).Trim())
}
if ($failCounter -ge 2) {
    $entry = @{ ts = (Get-Date -Format o); df = "DF-06"; op = "light-pass"; status = "halted-fail-cap"; fail_counter = $failCounter } | ConvertTo-Json -Compress
    Add-Content -Path $AUDIT -Value $entry
    Add-Content -Path $BULLETIN -Value "`n[DF-06-ALERT $(Get-Date -Format o)] Fail-Counter bei 2+ - DF-06 gestoppt. Martin-Review noetig.`n"
    New-Item -Path "$DF_DIR\DISABLED" -ItemType File -Force | Out-Null
    exit 1
}

# 3. Light-Pass: Lease-Sweep + State-Rebuild + Conflict-Detect + Dedupe
$runStart = Get-Date -Format o
$exitCode = 0
$errorMsg = ""
try {
    $null = python "$SCRIPTS\ttl_lease_manager.py" sweep 2>&1
    $null = python "$SCRIPTS\collect_roadmap_state.py" 2>&1
    $conflicts = python "$SCRIPTS\detect_roadmap_conflicts.py" 2>&1 | Out-String
    $dedupe = python "$SCRIPTS\semantic_fingerprint_dedup.py" --threshold 0.7 2>&1 | Out-String

    # Shadow-Mode: Outputs in shadow/
    if (Test-Path "$DF_DIR\shadow-mode.flag") {
        $shadowDir = "$DF_DIR\shadow"
        $ts = Get-Date -Format "yyyyMMdd-HHmm"
        $conflicts | Out-File -FilePath "$shadowDir\conflicts-$ts.json" -Encoding utf8
        $dedupe | Out-File -FilePath "$shadowDir\dedupe-$ts.json" -Encoding utf8
    }

    # Reset Fail-Counter on success
    "0" | Out-File -FilePath "$DF_DIR\fail-counter" -Encoding utf8 -NoNewline
} catch {
    $exitCode = 1
    $errorMsg = $_.Exception.Message
    $failCounter += 1
    "$failCounter" | Out-File -FilePath "$DF_DIR\fail-counter" -Encoding utf8 -NoNewline
}

$runEnd = Get-Date -Format o
$status = if ($exitCode -eq 0) { "success" } else { "fail" }
$auditEntry = @{
    ts = $runEnd
    df = "DF-06"
    op = "light-pass"
    status = $status
    fail_counter = $failCounter
    run_start = $runStart
    error = $errorMsg
} | ConvertTo-Json -Compress
Add-Content -Path $AUDIT -Value $auditEntry
exit $exitCode
