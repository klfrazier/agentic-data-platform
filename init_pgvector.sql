-- ─────────────────────────────────────────────
-- Auto-runs on first postgres container start
-- Place this file in: ./database/init/
-- ─────────────────────────────────────────────

-- Enable pgvector extension
CREATE EXTENSION IF NOT EXISTS vector;

-- Enable useful postgres extensions
CREATE EXTENSION IF NOT EXISTS pg_trgm;     -- fuzzy text search
CREATE EXTENSION IF NOT EXISTS btree_gin;   -- GIN index support

-- Confirm
SELECT extname, extversion FROM pg_extension WHERE extname = 'vector';