-- state-machine-extensions.schema.sql [CRUX-MK]
-- Erweiterungen zu cross-reference-index.schema.sql post Wave-2 Wargames
-- Codex+Gemini 2/2 MODIFY-Konsens auf State-Machine + Claims-Tracking
-- Version: 0.2.0 (2026-04-19 MYZ-Wave-2)

-- ==========================================================================
-- 1. BOOK-STATE-EXTENSIONS (Wave-2 W6)
-- ==========================================================================

-- Ergaenzt existierende books-Tabelle um State-Machine-Felder
-- ALTER TABLE books ADD ... (separate migrations; hier Referenz-Schema)

CREATE TABLE IF NOT EXISTS book_state (
    book_id              TEXT PRIMARY KEY REFERENCES books(book_id),
    current_phase        INTEGER NOT NULL CHECK (current_phase BETWEEN 1 AND 6),
    phase_status         TEXT NOT NULL CHECK (phase_status IN ('queued','running','awaiting_approval','blocked','failed','completed','paused')),
    phase_entered_at     TIMESTAMP NOT NULL,
    current_run_id       TEXT,
    state_version        INTEGER NOT NULL DEFAULT 1,   -- CAS-Schranke (Codex)
    approval_state       TEXT DEFAULT 'none' CHECK (approval_state IN ('none','pending','approved','rejected')),
    canon_branch         TEXT,
    shadow_branch        TEXT,
    canon_head_sha       TEXT,
    shadow_head_sha      TEXT,
    base_canon_sha       TEXT,
    last_checkpoint_event_id INTEGER,
    context_window_hash  TEXT,                         -- Gemini: Halluzinations-Detektion
    retry_count          INTEGER DEFAULT 0,
    last_error_code      TEXT,
    last_error_at        TIMESTAMP,
    updated_at           TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_bookstate_phase ON book_state(current_phase, phase_status);

-- ==========================================================================
-- 2. CHAPTER-STATE (pro Kapitel eigener State)
-- ==========================================================================

CREATE TABLE IF NOT EXISTS chapter_state (
    book_id              TEXT NOT NULL REFERENCES books(book_id),
    chapter_no           INTEGER NOT NULL,
    chapter_status       TEXT NOT NULL DEFAULT 'not_started',
    draft_stage          TEXT CHECK (draft_stage IN ('not_started','complete','v2','v3','final','expanded')),
    review_state         TEXT CHECK (review_state IN ('none','auto_review','martin_review','approved','rejected')),
    current_artifact_id  TEXT,
    started_from_canon_sha TEXT,
    shadow_commit_sha    TEXT,
    last_draft_at        TIMESTAMP,
    retry_count          INTEGER DEFAULT 0,
    last_error_code      TEXT,
    PRIMARY KEY (book_id, chapter_no)
);

CREATE INDEX idx_chapter_state_status ON chapter_state(book_id, chapter_status);

-- ==========================================================================
-- 3. LEASES (exklusive Buch-Locks fuer Race-Condition-Schutz)
-- ==========================================================================

CREATE TABLE IF NOT EXISTS leases (
    book_id              TEXT PRIMARY KEY REFERENCES books(book_id),
    lease_owner          TEXT NOT NULL,                -- worker/process-id
    lease_expires_at     TIMESTAMP NOT NULL,
    heartbeat_at         TIMESTAMP NOT NULL,
    acquired_at          TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- ==========================================================================
-- 4. RUNS / SAGA-PATTERN (Codex-Empfehlung)
-- ==========================================================================

CREATE TABLE IF NOT EXISTS runs (
    run_id               TEXT PRIMARY KEY,
    book_id              TEXT NOT NULL REFERENCES books(book_id),
    chapter_no           INTEGER,
    target_stage         TEXT,                          -- z.B. "v3" oder "final"
    step_marker          TEXT NOT NULL DEFAULT 'claimed'
                         CHECK (step_marker IN (
                             'claimed','generation_done','files_written','git_committed','state_applied',
                             'abandoned','failed'
                         )),
    idempotency_key      TEXT UNIQUE,                   -- z.B. "book:ch07:v2:attempt3"
    input_manifest       TEXT,                          -- JSON: masterplan_ver, playbook_ver, template_ver, base_canon_sha
    temp_artifact_path   TEXT,
    temp_artifact_hash   TEXT,
    git_commit_sha       TEXT,
    cost_eur             REAL DEFAULT 0,
    tokens_input         INTEGER DEFAULT 0,
    tokens_output        INTEGER DEFAULT 0,
    heartbeat_at         TIMESTAMP,
    started_at           TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    completed_at         TIMESTAMP
);

CREATE INDEX idx_runs_book_chapter ON runs(book_id, chapter_no);
CREATE INDEX idx_runs_step ON runs(step_marker);
CREATE INDEX idx_runs_heartbeat ON runs(heartbeat_at);

-- ==========================================================================
-- 5. STATE-TRANSITION-LOG (FSM-Audit, Gemini)
-- ==========================================================================

CREATE TABLE IF NOT EXISTS state_transitions (
    transition_id        INTEGER PRIMARY KEY AUTOINCREMENT,
    book_id              TEXT NOT NULL REFERENCES books(book_id),
    from_phase           INTEGER,
    to_phase             INTEGER,
    from_chapter_stage   TEXT,
    to_chapter_stage     TEXT,
    trigger_event        TEXT,
    trigger_by           TEXT,                          -- 'df-auto' | 'martin-approval' | 'martin-override'
    git_commit_sha       TEXT,
    justification        TEXT,
    transitioned_at      TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_transitions_book ON state_transitions(book_id, transitioned_at DESC);

-- ==========================================================================
-- 6. CLAIMS-TABLE (Wave-2 W8 - Codex+Gemini Konsens kanonisch)
-- ==========================================================================

CREATE TABLE IF NOT EXISTS claims (
    claim_id             INTEGER PRIMARY KEY AUTOINCREMENT,
    book_id              TEXT NOT NULL REFERENCES books(book_id),
    chapter_no           INTEGER,
    span_start           INTEGER,
    span_end             INTEGER,
    claim_text           TEXT NOT NULL,
    claim_type           TEXT CHECK (claim_type IN ('fact','interpretation','rhetoric','narrative_assertion')),
    domain               TEXT,                          -- finance|history|science|narrative|...
    needs_verification   BOOLEAN DEFAULT 1,
    source_ids           TEXT,                          -- JSON array von entity_ids oder URLs
    page_refs            TEXT,
    confidence_model     REAL,
    confidence_editor    REAL,
    status               TEXT DEFAULT 'unverified'
                         CHECK (status IN ('unverified','supported','disputed','missing_source','stale','approved')),
    author_id            TEXT,
    verification_agent   TEXT,                          -- welches LLM/System hat validated
    created_at           TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at           TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_claims_book_chapter ON claims(book_id, chapter_no);
CREATE INDEX idx_claims_status ON claims(status);
CREATE INDEX idx_claims_type ON claims(claim_type);

-- ==========================================================================
-- 7. STORY-STATE-GRAPH (K1 Narrativ-Spezifisch, Wave-2 W8)
-- ==========================================================================

CREATE TABLE IF NOT EXISTS story_assertions (
    assertion_id         INTEGER PRIMARY KEY AUTOINCREMENT,
    book_id              TEXT NOT NULL REFERENCES books(book_id),
    entity_id            TEXT NOT NULL REFERENCES entities(entity_id),   -- Figur/Ort/Objekt
    attribute            TEXT NOT NULL,                 -- age|residence|relationship|injury|possession|alive_status|timeline_position|...
    value                TEXT NOT NULL,
    time_scope_type      TEXT CHECK (time_scope_type IN ('abs_date','relative_day','chapter_range')),
    time_scope_value     TEXT,                          -- "1999-03-15" oder "Kap 5-8"
    source_scene         TEXT,                          -- "kap09_arche_init"
    certainty            REAL DEFAULT 1.0,
    narrator_scope       TEXT CHECK (narrator_scope IN ('omniscient','character_belief','unreliable')),
    created_at           TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_assertions_entity ON story_assertions(entity_id);
CREATE INDEX idx_assertions_book_attr ON story_assertions(book_id, attribute);
CREATE INDEX idx_assertions_time ON story_assertions(time_scope_type, time_scope_value);

-- ==========================================================================
-- 8. TASK-HISTORY (Crash-Recovery Context-Preservation, Gemini)
-- ==========================================================================

CREATE TABLE IF NOT EXISTS task_history (
    task_id              INTEGER PRIMARY KEY AUTOINCREMENT,
    run_id               TEXT NOT NULL REFERENCES runs(run_id),
    book_id              TEXT NOT NULL,
    chapter_no           INTEGER,
    prompt_hash          TEXT,                          -- SHA256 des Prompts (dedup)
    prompt_text          TEXT,                          -- truncated Prompt (max 10k chars)
    response_text        TEXT,                          -- LLM-Response
    model_used           TEXT,                          -- haiku-4.5|sonnet-4.6|opus-4.5|codex|gemini
    cost_eur             REAL,
    tokens_input         INTEGER,
    tokens_output        INTEGER,
    recorded_at          TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_task_run ON task_history(run_id);
CREATE INDEX idx_task_book_chapter ON task_history(book_id, chapter_no);

-- ==========================================================================
-- 9. VIEWS
-- ==========================================================================

-- Orphaned Runs (running + abgelaufener Heartbeat)
CREATE VIEW IF NOT EXISTS v_orphaned_runs AS
SELECT r.*, CAST((julianday('now') - julianday(r.heartbeat_at)) * 24 * 60 AS INTEGER) AS minutes_stale
FROM runs r
WHERE r.step_marker NOT IN ('state_applied','abandoned','failed')
  AND r.heartbeat_at IS NOT NULL
  AND julianday('now') - julianday(r.heartbeat_at) > 1.0 / 24;   -- > 60 min

-- Phase-Stuck Books (awaiting_approval > 24h)
CREATE VIEW IF NOT EXISTS v_stuck_approvals AS
SELECT book_id, current_phase, phase_entered_at,
       CAST((julianday('now') - julianday(phase_entered_at)) AS INTEGER) AS days_waiting
FROM book_state
WHERE phase_status = 'awaiting_approval'
  AND julianday('now') - julianday(phase_entered_at) > 1.0;

-- Narrative Inconsistencies (gleiche Entity + Attribute, divergierende Values)
CREATE VIEW IF NOT EXISTS v_story_inconsistencies AS
SELECT book_id, entity_id, attribute,
       GROUP_CONCAT(value, ' | ') AS divergent_values,
       COUNT(DISTINCT value) AS n_values,
       GROUP_CONCAT(source_scene, ',') AS source_scenes
FROM story_assertions
GROUP BY book_id, entity_id, attribute
HAVING n_values > 1
  AND attribute IN ('age','alive_status','residence');

-- Unverified Claims ueber Schwelle
CREATE VIEW IF NOT EXISTS v_claims_unverified AS
SELECT c.*, b.primary_category
FROM claims c
JOIN books b ON c.book_id = b.book_id
WHERE c.status = 'unverified'
  AND c.needs_verification = 1
  AND b.primary_category IN ('K2','K5')  -- Pflicht-Provenance-Kategorien
ORDER BY c.created_at DESC;

-- [CRUX-MK]
