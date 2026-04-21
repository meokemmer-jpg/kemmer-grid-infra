-- cross-reference-index.schema.sql [CRUX-MK]
-- Graphity Cross-Reference Schema fuer Medium-to-Large Buecher (2k-20k Refs)
-- Empfohlen von Codex + Gemini (CROSS-LLM-2OF3) + Grok-Dissens dokumentiert
--
-- Skalierung-Thresholds (aus Wargame 2026-04-19):
--   <500 Refs:       single YAML (registry.yaml)
--   500-2000 Refs:   multi-file YAML
--   2000-20000 Refs: DIESES SCHEMA (SQLite + Junction-Tables)
--   >20000 Refs:     Neo4j/DuckDB analytics
--
-- Authoring bleibt YAML, Build konvertiert in SQLite.
-- Version: 0.1.0 (MYZ-Wave-1, 2026-04-19)

-- ==========================================================================
-- 1. GLOBALE ENTITY-REGISTRY (Shared across books)
-- ==========================================================================

CREATE TABLE IF NOT EXISTS entities (
    entity_id          TEXT PRIMARY KEY,                    -- z.B. "STAHL-SCHATTENKIND"
    entity_type        TEXT NOT NULL,                       -- zutat|figur|these|kapitel|lernziel|...
    canonical_name     TEXT NOT NULL,
    description        TEXT,
    source_reference   TEXT,                                -- "Stefanie Stahl - Das Kind in dir..."
    source_quote       TEXT,                                -- original quote (optional)
    crux_mk            INTEGER DEFAULT 1,                   -- [CRUX-MK] marker
    created_at         TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at         TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    metadata_json      TEXT                                 -- flexibler Zusatz
);

CREATE INDEX idx_entities_type ON entities(entity_type);

-- ==========================================================================
-- 2. BUCH-REGISTRY (Pro Buch-Projekt)
-- ==========================================================================

CREATE TABLE IF NOT EXISTS books (
    book_id            TEXT PRIMARY KEY,                    -- z.B. "souveraene-maschine"
    title              TEXT NOT NULL,
    category_bitmask   INTEGER NOT NULL,                    -- 0b0000001 = K1, 0b0011001 = K1+K4+K5 Hybrid
    primary_category   TEXT NOT NULL,                       -- dominante Kategorie fuer Pipeline-Routing
    ebenen_profile     TEXT DEFAULT 'default',              -- 'default' oder 'meta_narrative_opt_in'
    phase              INTEGER DEFAULT 1,                   -- 1=Masterplan, 2=Playbook, 3=Draft, 4=Wargame, 5=Produktionsbibel, 6=PMO
    status             TEXT DEFAULT 'active',               -- active|paused|published|superseded
    author_count       INTEGER DEFAULT 1,                   -- 1=solo, >1=co-autor
    bundle_parent      TEXT REFERENCES books(book_id),      -- fuer Serien/Bundles
    created_at         TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    metadata_json      TEXT
);

CREATE INDEX idx_books_category ON books(primary_category);
CREATE INDEX idx_books_status ON books(status);

-- ==========================================================================
-- 3. BUCH-SPEZIFISCHE OCCURRENCES (Entity-Overlays pro Buch)
-- ==========================================================================

CREATE TABLE IF NOT EXISTS book_occurrences (
    book_id             TEXT NOT NULL REFERENCES books(book_id),
    entity_id           TEXT NOT NULL REFERENCES entities(entity_id),
    introduced_in       INTEGER,                            -- Kapitel-Nummer (NULL = buchweit)
    last_seen           INTEGER,
    first_mention_context TEXT,                             -- kurzer Context-Snippet
    local_alias         TEXT,                               -- buch-spezifische Benennung
    prominence          INTEGER DEFAULT 1,                  -- 1=subsidiaer, 2=secondary, 3=primary (Anti-Drift)
    metadata_json       TEXT,
    PRIMARY KEY (book_id, entity_id)
);

CREATE INDEX idx_occ_book ON book_occurrences(book_id);
CREATE INDEX idx_occ_entity ON book_occurrences(entity_id);

-- ==========================================================================
-- 4. RELATIONEN / EDGES (zwischen Entitaeten)
-- ==========================================================================

CREATE TABLE IF NOT EXISTS edges (
    edge_id            INTEGER PRIMARY KEY AUTOINCREMENT,
    source_entity      TEXT NOT NULL REFERENCES entities(entity_id),
    target_entity      TEXT NOT NULL REFERENCES entities(entity_id),
    relation_type      TEXT NOT NULL,                       -- references|contrasts|develops_from|mirrors|foreshadows|resolves|...
    book_id            TEXT REFERENCES books(book_id),      -- NULL = globale Relation (registry-library)
    chapter_num        INTEGER,                             -- NULL = buchweit
    confidence         REAL DEFAULT 1.0,                    -- 0.0-1.0 (fuer Soft-Warn-Resolution)
    note               TEXT,
    created_at         TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_edges_source ON edges(source_entity);
CREATE INDEX idx_edges_target ON edges(target_entity);
CREATE INDEX idx_edges_book ON edges(book_id);
CREATE INDEX idx_edges_chapter ON edges(book_id, chapter_num);
CREATE INDEX idx_edges_relation ON edges(relation_type);

-- ==========================================================================
-- 5. ALIASES (alternative Namen fuer dieselbe Entity)
-- ==========================================================================

CREATE TABLE IF NOT EXISTS aliases (
    alias              TEXT NOT NULL,
    entity_id          TEXT NOT NULL REFERENCES entities(entity_id),
    book_id            TEXT REFERENCES books(book_id),      -- NULL = globaler Alias
    context            TEXT,                                -- z.B. "Figur referenziert nur mit Nachname"
    PRIMARY KEY (alias, entity_id, book_id)
);

CREATE INDEX idx_aliases_entity ON aliases(entity_id);
CREATE INDEX idx_aliases_alias ON aliases(alias);

-- ==========================================================================
-- 6. KAPITEL-CONTRACT (Anti-Drift-Vertrag pro Kapitel)
-- ==========================================================================

CREATE TABLE IF NOT EXISTS chapter_contracts (
    book_id            TEXT NOT NULL REFERENCES books(book_id),
    chapter_num        INTEGER NOT NULL,
    spine              TEXT,                                -- 1 Handlungs-/Claim-Verpflichtung
    primary_lens       TEXT,                                -- 1 aktive Linse (entity_id Referenz)
    secondary_lens     TEXT,                                -- 0..1 Counter-Force (entity_id Referenz)
    global_invariants  TEXT,                                -- JSON-Array frozen defaults (NOT counted as dominant)
    forbidden_lenses   TEXT,                                -- JSON-Array explizite Ausschluesse
    meta_frame         TEXT,                                -- 0..1 optional
    word_budget_min    INTEGER,
    word_budget_max    INTEGER,
    status             TEXT DEFAULT 'draft',                -- draft|reviewed|published
    PRIMARY KEY (book_id, chapter_num)
);

CREATE INDEX idx_contracts_status ON chapter_contracts(status);

-- ==========================================================================
-- 7. RESOLVER-LOG (Build-Audit-Trail)
-- ==========================================================================

CREATE TABLE IF NOT EXISTS resolver_log (
    log_id             INTEGER PRIMARY KEY AUTOINCREMENT,
    book_id            TEXT NOT NULL REFERENCES books(book_id),
    chapter_num        INTEGER,
    placeholder        TEXT NOT NULL,                       -- "{{CRX:STAHL:ROLF:KAP-09}}"
    resolved_to        TEXT,                                -- entity_id oder "FAIL"
    severity           TEXT,                                -- ok|warn|block
    reason             TEXT,
    resolved_at        TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_resolver_severity ON resolver_log(severity);
CREATE INDEX idx_resolver_book ON resolver_log(book_id);

-- ==========================================================================
-- 8. IMPACT-REPORTS (Build-Impact-Tracking)
-- ==========================================================================

CREATE TABLE IF NOT EXISTS impact_reports (
    report_id          INTEGER PRIMARY KEY AUTOINCREMENT,
    entity_id          TEXT REFERENCES entities(entity_id),
    change_type        TEXT,                                -- added|renamed|deprecated|archived
    book_id            TEXT REFERENCES books(book_id),
    affected_chapters  TEXT,                                -- JSON-Array
    report_at          TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    action_taken       TEXT                                 -- rebuild_requested|manual_review|automated_reindex
);

-- ==========================================================================
-- VIEWS fuer haeufige Queries
-- ==========================================================================

-- V1: Welche Kapitel nutzen Entity X?
CREATE VIEW IF NOT EXISTS v_entity_chapters AS
SELECT
    e.entity_id,
    e.canonical_name,
    bo.book_id,
    b.title AS book_title,
    bo.introduced_in,
    bo.last_seen,
    bo.prominence
FROM entities e
JOIN book_occurrences bo ON e.entity_id = bo.entity_id
JOIN books b ON bo.book_id = b.book_id;

-- V2: Cross-Kapitel-Referenzen
CREATE VIEW IF NOT EXISTS v_chapter_refs AS
SELECT
    ed.book_id,
    b.title,
    ed.chapter_num AS source_chapter,
    ed.relation_type,
    ed.target_entity,
    e.canonical_name AS target_name,
    ed.confidence
FROM edges ed
JOIN entities e ON ed.target_entity = e.entity_id
JOIN books b ON ed.book_id = b.book_id
WHERE ed.chapter_num IS NOT NULL
ORDER BY ed.book_id, ed.chapter_num;

-- V3: Temporale Inkonsistenz-Check (Verweis vor introduced_in)
CREATE VIEW IF NOT EXISTS v_temporal_violations AS
SELECT
    ed.book_id,
    ed.chapter_num AS reference_chapter,
    ed.target_entity,
    bo.introduced_in AS introduced_chapter
FROM edges ed
JOIN book_occurrences bo
  ON ed.target_entity = bo.entity_id
  AND ed.book_id = bo.book_id
WHERE ed.chapter_num IS NOT NULL
  AND bo.introduced_in IS NOT NULL
  AND ed.chapter_num < bo.introduced_in;

-- V4: Anti-Drift-Check (mehr als 1 primary_lens pro Kapitel)
CREATE VIEW IF NOT EXISTS v_dominance_violations AS
SELECT
    cc.book_id,
    cc.chapter_num,
    cc.primary_lens,
    cc.secondary_lens,
    (CASE
        WHEN cc.primary_lens IS NOT NULL AND cc.secondary_lens IS NOT NULL THEN 2
        WHEN cc.primary_lens IS NOT NULL THEN 1
        ELSE 0
    END) AS active_dominants
FROM chapter_contracts cc
WHERE (CASE
        WHEN cc.primary_lens IS NOT NULL AND cc.secondary_lens IS NOT NULL THEN 2
        WHEN cc.primary_lens IS NOT NULL THEN 1
        ELSE 0
    END) > 2;

-- [CRUX-MK]
