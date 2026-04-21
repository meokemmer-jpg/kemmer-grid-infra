-- wave3-extensions.schema.sql [CRUX-MK]
-- Wave-3-Konsens: Voice-Fingerprint + Versionierung + Scheduling + Context-Capsule
-- Zu laden NACH cross-reference-index.schema.sql + state-machine-extensions.schema.sql

-- =======================================================================
-- §1 Voice-Fingerprint-Tables (W9)
-- =======================================================================

-- Baseline-Vektoren pro Autor x Kategorie x Overlay x Algorithmus
-- Scope: (author, category, overlay) entspricht Wave-3-Regel "niemals global"
CREATE TABLE IF NOT EXISTS voice_baselines (
    author_id        TEXT NOT NULL,
    category         TEXT NOT NULL,     -- K1_narrativ | K2_argumentativ | ...
    overlay          TEXT,              -- co_author | bundle | biografisch | NULL
    algo             TEXT NOT NULL,     -- V1_burrows | V2_syntax | V3_six_pillar | V4_rolling | V5_sbert
    baseline_vector  BLOB,              -- serialisierter numpy array / pickle
    n_samples        INTEGER,           -- wie viele Referenzkapitel flossen ein
    n_words          INTEGER,           -- Gesamt-Wortcount der Referenz
    quality_flag     TEXT DEFAULT 'ok', -- ok | low_n | stale
    computed_at      TEXT DEFAULT (datetime('now')),
    PRIMARY KEY (author_id, category, overlay, algo)
);

-- Scores pro Kapitel x Algorithmus (inkl. Fusion-Score)
CREATE TABLE IF NOT EXISTS voice_scores (
    book_id       TEXT NOT NULL,
    chapter_num   INTEGER NOT NULL,
    revision_id   TEXT,                   -- verknuepft mit book_revisions
    algo          TEXT NOT NULL,          -- V1..V5 | fusion
    score         REAL NOT NULL,          -- 0.0 - 1.0 drift
    severity      TEXT,                   -- ok | gelb | rot
    details_json  TEXT,                   -- Top-Features mit groesster Abweichung
    computed_at   TEXT DEFAULT (datetime('now')),
    PRIMARY KEY (book_id, chapter_num, revision_id, algo)
);

CREATE INDEX IF NOT EXISTS idx_voice_scores_severity ON voice_scores(severity, score DESC);

-- =======================================================================
-- §2 Versionierungs-Tables (W10)
-- =======================================================================

CREATE TABLE IF NOT EXISTS book_revisions (
    revision_id       TEXT PRIMARY KEY,   -- uuid / timestamp-hash
    book_id           TEXT NOT NULL,
    based_on          TEXT,               -- parent revision_id
    masterplan_ref    TEXT,               -- path oder git-ref
    change_set_json   TEXT,               -- additive | constraint_change | structural items
    classification    TEXT,               -- additive | constraint_change | structural
    status            TEXT DEFAULT 'draft',  -- draft | active | rolled_back | superseded
    created_at        TEXT DEFAULT (datetime('now')),
    created_by        TEXT,               -- martin | df-07 | claude
    promoted_at       TEXT,
    notes             TEXT
);

CREATE INDEX IF NOT EXISTS idx_book_revisions_book ON book_revisions(book_id, status);

-- Chapter-Invalidation-Log (Stufe 2 aus W10-FSM)
CREATE TABLE IF NOT EXISTS chapter_invalidations (
    id               INTEGER PRIMARY KEY AUTOINCREMENT,
    book_id          TEXT NOT NULL,
    chapter_num      INTEGER NOT NULL,
    revision_id      TEXT NOT NULL,      -- gegen welche book_revision
    chapter_state    TEXT NOT NULL,      -- clean | stale_review | stale_redraft | blocked
    impact_score     REAL,               -- 0.0 - 1.0
    reasons_json     TEXT,               -- array of reason-strings
    detected_conflicts_json TEXT,
    resolution       TEXT,               -- redrafted | reviewed | noop | manual_edit
    created_at       TEXT DEFAULT (datetime('now')),
    resolved_at      TEXT
);

-- =======================================================================
-- §3 Scheduler-Tables (W11)
-- =======================================================================

CREATE TABLE IF NOT EXISTS scheduler_runs (
    run_id                TEXT PRIMARY KEY,
    week_start            TEXT NOT NULL,     -- ISO date
    r_week_budget_minutes INTEGER NOT NULL,  -- Martin-Review-Budget
    wip_max               INTEGER DEFAULT 3,
    selected_tasks_json   TEXT,              -- [{book, chapter, score, review_minutes}, ...]
    total_review_minutes  INTEGER,
    skipped_tasks_json    TEXT,              -- mit Grund (budget | wip | collision | paused)
    created_at            TEXT DEFAULT (datetime('now')),
    executed_at           TEXT
);

-- Buch-Level Metriken fuer Prioritaets-Funktion
CREATE TABLE IF NOT EXISTS book_metrics (
    book_id              TEXT PRIMARY KEY,
    rho_eur_year         REAL,
    masterplan_progress  REAL,               -- 0.0 - 1.0
    chapter_map_progress REAL,
    draft_coverage       REAL,
    wargame_progress     REAL,
    martin_interest      REAL DEFAULT 1.0,   -- 0.7 - 1.3
    deadline_iso         TEXT,               -- NULL wenn keine Deadline
    last_progress_at     TEXT,
    status               TEXT DEFAULT 'active',  -- active | paused | hibernated
    computed_at          TEXT DEFAULT (datetime('now'))
);

-- =======================================================================
-- §4 Context-Capsule-Tables (W11 Vector-Namespace-Isolation)
-- =======================================================================

-- Pro Buch: Whitelist-Tokens die NICHT gedrifft sein duerfen
CREATE TABLE IF NOT EXISTS context_capsules (
    book_id              TEXT PRIMARY KEY,
    namespace_hash       TEXT,               -- Hash fuer RAG-Isolation
    whitelist_entities_json  TEXT,           -- JSON-Array Entity-IDs die erlaubt sind
    terminology_json     TEXT,               -- JSON-Dict term -> definition
    style_rules_json     TEXT,               -- Kaestner-Cap, Adjektiv-Fasten, forbidden lenses
    negative_list_json   TEXT,               -- was DARF NICHT auftauchen (andere Buecher)
    updated_at           TEXT DEFAULT (datetime('now'))
);

-- Collision-Detection-Log
CREATE TABLE IF NOT EXISTS collision_checks (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    book_id         TEXT NOT NULL,
    chapter_num     INTEGER NOT NULL,
    collision_type  TEXT,                    -- entity_leak | style_leak | terminology_leak
    offending_token TEXT,
    source_book     TEXT,                    -- aus welchem anderen Buch
    severity        TEXT,                    -- warn | block
    action          TEXT,                    -- regenerated | approved_override | skipped
    checked_at      TEXT DEFAULT (datetime('now'))
);

-- =======================================================================
-- §5 Views fuer Wave-3
-- =======================================================================

-- Kapitel mit aktuellem Drift-Alarm
CREATE VIEW IF NOT EXISTS v_voice_drift_alerts AS
SELECT
    vs.book_id, vs.chapter_num, vs.algo, vs.score, vs.severity,
    cc.primary_lens, cc.status
FROM voice_scores vs
LEFT JOIN chapter_contracts cc
    ON vs.book_id = cc.book_id AND vs.chapter_num = cc.chapter_num
WHERE vs.severity IN ('gelb', 'rot')
ORDER BY vs.score DESC;

-- Aktive Scheduler-Plan-View (aktuellste Woche)
CREATE VIEW IF NOT EXISTS v_active_schedule AS
SELECT run_id, week_start, selected_tasks_json, total_review_minutes, r_week_budget_minutes
FROM scheduler_runs
WHERE executed_at IS NULL
ORDER BY week_start DESC
LIMIT 1;

-- Book-Priority-Ranking (fuer Debug/Inspection)
CREATE VIEW IF NOT EXISTS v_book_priority AS
SELECT
    bm.book_id, b.title,
    bm.rho_eur_year,
    (0.4 + 0.6 * (
        0.3*COALESCE(bm.masterplan_progress, 0) +
        0.3*COALESCE(bm.chapter_map_progress, 0) +
        0.3*COALESCE(bm.draft_coverage, 0) +
        0.1*COALESCE(bm.wargame_progress, 0)
    )) AS fortschritt,
    bm.martin_interest,
    bm.status,
    julianday(bm.deadline_iso) - julianday('now') AS days_to_deadline
FROM book_metrics bm
JOIN books b ON bm.book_id = b.book_id
WHERE bm.status != 'hibernated'
ORDER BY bm.rho_eur_year DESC;

-- Kapitel-Invalidation-Status fuer aktuelle Revisions
CREATE VIEW IF NOT EXISTS v_chapter_invalidation_status AS
SELECT
    ci.book_id, ci.chapter_num, ci.revision_id,
    ci.chapter_state, ci.impact_score,
    br.masterplan_ref, br.classification
FROM chapter_invalidations ci
JOIN book_revisions br ON ci.revision_id = br.revision_id
WHERE ci.resolved_at IS NULL
  AND br.status = 'active'
ORDER BY ci.impact_score DESC;

-- [CRUX-MK]
