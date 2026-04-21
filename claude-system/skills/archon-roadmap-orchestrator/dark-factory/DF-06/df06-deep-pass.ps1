# DF-06 Deep-Pass (1x taeglich 06:00, Claude-nodes via token_guard, Budget 2 EUR)
# PS 5.1 + 7 kompatibel

$DF_DIR = "C:\Users\marti\.claude\skills\archon-roadmap-orchestrator\dark-factory\DF-06"
$SCRIPTS = "C:\Users\marti\.claude\skills\archon-roadmap-orchestrator\scripts"
$AUDIT = "G:\Meine Ablage\Claude-Knowledge-System\branch-hub\audit\dark-factory.jsonl"
$BULLETIN = "G:\Meine Ablage\Claude-Knowledge-System\branch-hub\BULLETIN.md"
$WF = "df-06-deep-" + (Get-Date -Format "yyyyMMdd")

if (Test-Path "$DF_DIR\DISABLED") { exit 0 }

$failCounter = 0
if (Test-Path "$DF_DIR\fail-counter") { $failCounter = [int]((Get-Content "$DF_DIR\fail-counter" -Raw).Trim()) }
if ($failCounter -ge 2) {
    Add-Content -Path $BULLETIN -Value "`n[DF-06-DEEP-ALERT $(Get-Date -Format o)] Fail-Counter=$failCounter, deep-pass halted.`n"
    exit 1
}

$runStart = Get-Date -Format o
$exitCode = 0
$errorMsg = ""

try {
    # Token-Guard init
    $null = python "$SCRIPTS\token_guard.py" --init --workflow $WF 2>&1

    # Light-Pass-Steps (deterministic)
    $null = python "$SCRIPTS\ttl_lease_manager.py" sweep 2>&1
    $null = python "$SCRIPTS\collect_roadmap_state.py" 2>&1
    $conflicts = python "$SCRIPTS\detect_roadmap_conflicts.py" 2>&1 | Out-String
    $dedupe = python "$SCRIPTS\semantic_fingerprint_dedup.py" --threshold 0.7 2>&1 | Out-String

    # Propagate-Optima (touched DF-configs bei Optima-Change)
    $null = python "$SCRIPTS\propagate_optima.py" --reason "deep-pass-daily" 2>&1

    # Shadow-Mode-Output
    if (Test-Path "$DF_DIR\shadow-mode.flag") {
        $shadowDir = "$DF_DIR\shadow"
        $ts = Get-Date -Format "yyyyMMdd-HHmm"
        $conflicts | Out-File -FilePath "$shadowDir\deep-conflicts-$ts.json" -Encoding utf8
        $dedupe | Out-File -FilePath "$shadowDir\deep-dedupe-$ts.json" -Encoding utf8

        $conflictsCount = 0
        $dedupePairs = 0
        try {
            $cj = $conflicts | ConvertFrom-Json -ErrorAction SilentlyContinue
            if ($cj.conflicts) { $conflictsCount = $cj.conflicts.Count }
            $dj = $dedupe | ConvertFrom-Json -ErrorAction SilentlyContinue
            if ($dj.pairs) { $dedupePairs = $dj.pairs.Count }
        } catch {}

        $review = @{
            ts = $runStart
            workflow = $WF
            type = "deep-pass"
            conflicts_detected = $conflictsCount
            dedupe_pairs = $dedupePairs
            status = "pending-review"
        } | ConvertTo-Json -Compress
        Add-Content -Path "$DF_DIR\review-log.jsonl" -Value $review
    }

    # Token-Guard finalize
    $null = python "$SCRIPTS\token_guard.py" --finalize --workflow $WF 2>&1

    # Reset Fail-Counter
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
    op = "deep-pass"
    status = $status
    workflow = $WF
    run_start = $runStart
    fail_counter = $failCounter
    error = $errorMsg
} | ConvertTo-Json -Compress
Add-Content -Path $AUDIT -Value $auditEntry
exit $exitCode
