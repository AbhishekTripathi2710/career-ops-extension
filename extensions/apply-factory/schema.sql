-- apply-factory KB schema

PRAGMA foreign_keys = ON;
PRAGMA journal_mode = WAL;

CREATE TABLE IF NOT EXISTS kb_entries (
    intent_key    TEXT PRIMARY KEY,
    answer_type   TEXT NOT NULL,
    answer        TEXT NOT NULL,
    confidence    REAL DEFAULT 1.0,
    source        TEXT DEFAULT 'manual',
    seen_count    INTEGER DEFAULT 1,
    last_seen     TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    created_at    TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    notes         TEXT
);

CREATE TABLE IF NOT EXISTS kb_question_variants (
    variant_id    INTEGER PRIMARY KEY AUTOINCREMENT,
    intent_key    TEXT NOT NULL REFERENCES kb_entries(intent_key),
    question_text TEXT NOT NULL,
    field_type    TEXT,
    first_seen    TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(intent_key, question_text)
);

CREATE INDEX IF NOT EXISTS idx_variants_intent ON kb_question_variants(intent_key);

CREATE TABLE IF NOT EXISTS learning_events (
    event_id      INTEGER PRIMARY KEY AUTOINCREMENT,
    app_id        INTEGER,
    intent_key    TEXT NOT NULL,
    question_text TEXT NOT NULL,
    old_answer    TEXT,
    new_answer    TEXT NOT NULL,
    event_type    TEXT NOT NULL,
    created_at    TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
