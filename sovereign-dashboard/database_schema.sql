-- ============================================================================
-- aSiReM SOVEREIGN COMMAND CENTER - DATABASE SCHEMA
-- ============================================================================
-- Purpose: Persistent storage for discoveries, agent tasks, credits, and state
-- Database: SQLite (lightweight, embedded, perfect for local use)
-- Version: 1.0
-- Date: 2026-01-18
-- ============================================================================

-- Enable foreign key support
PRAGMA foreign_keys = ON;

-- ============================================================================
-- CORE TABLES
-- ============================================================================

-- System State
-- Stores overall system configuration and runtime state
CREATE TABLE IF NOT EXISTS system_state (
    id INTEGER PRIMARY KEY CHECK (id = 1), -- Only one row allowed
    mode TEXT NOT NULL DEFAULT 'real',
    auto_evolve_enabled BOOLEAN DEFAULT 0,
    last_pipeline_run TIMESTAMP,
    total_patterns_discovered INTEGER DEFAULT 0,
    total_files_scanned INTEGER DEFAULT 0,
    total_knowledge_nodes INTEGER DEFAULT 0,
    veo3_credits_remaining INTEGER DEFAULT 12500,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Initialize with default state
INSERT OR IGNORE INTO system_state (id) VALUES (1);

-- ============================================================================
-- DISCOVERY SYSTEM
-- ============================================================================

-- Discovered Files
-- All files found by the scanner agent
CREATE TABLE IF NOT EXISTS discovered_files (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    path TEXT NOT NULL UNIQUE,
    name TEXT NOT NULL,
    extension TEXT,
    size_bytes INTEGER,
    language TEXT,
    score REAL DEFAULT 0.0,
    discovered_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    last_analyzed TIMESTAMP,
    
    -- Metadata
    git_repo TEXT,
    relative_path TEXT,
    
    -- Indexing
    INDEX idx_extension (extension),
    INDEX idx_language (language),
    INDEX idx_score (score DESC),
    INDEX idx_discovered_at (discovered_at DESC)
);

-- File Patterns
-- Patterns discovered within files (many-to-many relationship)
CREATE TABLE IF NOT EXISTS file_patterns (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    file_id INTEGER NOT NULL,
    pattern_type TEXT NOT NULL, -- 'agent', 'tool', 'workflow', 'rag', 'streaming', etc.
    pattern_value TEXT NOT NULL,
    line_number INTEGER,
    confidence REAL DEFAULT 1.0,
    
    FOREIGN KEY (file_id) REFERENCES discovered_files(id) ON DELETE CASCADE,
    INDEX idx_pattern_type (pattern_type),
    INDEX idx_pattern_value (pattern_value)
);

-- Code Elements
-- Functions, classes, imports extracted from files
CREATE TABLE IF NOT EXISTS code_elements (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    file_id INTEGER NOT NULL,
    element_type TEXT NOT NULL, -- 'function', 'class', 'import'
    element_name TEXT NOT NULL,
    line_start INTEGER,
    line_end INTEGER,
    signature TEXT,
    docstring TEXT,
    
    FOREIGN KEY (file_id) REFERENCES discovered_files(id) ON DELETE CASCADE,
    INDEX idx_element_type (element_type),
    INDEX idx_element_name (element_name)
);

-- ============================================================================
-- KNOWLEDGE GRAPH
-- ============================================================================

-- Concepts
-- High-level concepts extracted from code
CREATE TABLE IF NOT EXISTS concepts (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL UNIQUE,
    category TEXT, -- 'agent', 'tool', 'pattern', 'framework', etc.
    description TEXT,
    importance_score REAL DEFAULT 0.0,
    occurrence_count INTEGER DEFAULT 1,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    INDEX idx_category (category),
    INDEX idx_importance (importance_score DESC)
);

-- Concept Relationships
-- Relationships between concepts (edges in knowledge graph)
CREATE TABLE IF NOT EXISTS concept_relationships (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    source_concept_id INTEGER NOT NULL,
    target_concept_id INTEGER NOT NULL,
    relationship_type TEXT NOT NULL, -- 'uses', 'extends', 'implements', 'related_to'
    strength REAL DEFAULT 1.0,
    evidence TEXT, -- JSON array of evidence (file paths, line numbers)
    
    FOREIGN KEY (source_concept_id) REFERENCES concepts(id) ON DELETE CASCADE,
    FOREIGN KEY (target_concept_id) REFERENCES concepts(id) ON DELETE CASCADE,
    UNIQUE(source_concept_id, target_concept_id, relationship_type),
    INDEX idx_source (source_concept_id),
    INDEX idx_target (target_concept_id),
    INDEX idx_type (relationship_type)
);

-- ============================================================================
-- AGENT SYSTEM
-- ============================================================================

-- Agent Definitions
-- All registered agents in the system
CREATE TABLE IF NOT EXISTS agents (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    agent_id TEXT NOT NULL UNIQUE,
    agent_name TEXT NOT NULL,
    agent_icon TEXT,
    agent_type TEXT, -- 'scanner', 'classifier', 'extractor', 'researcher', etc.
    capabilities TEXT, -- JSON array of capabilities
    status TEXT DEFAULT 'idle', -- 'idle', 'working', 'error'
    total_tasks_completed INTEGER DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    INDEX idx_agent_type (agent_type),
    INDEX idx_status (status)
);

-- Agent Tasks
-- Historical log of all tasks executed by agents
CREATE TABLE IF NOT EXISTS agent_tasks (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    task_id TEXT NOT NULL UNIQUE,
    agent_id TEXT NOT NULL,
    action TEXT NOT NULL,
    target TEXT,
    status TEXT DEFAULT 'pending', -- 'pending', 'running', 'completed', 'failed'
    progress INTEGER DEFAULT 0,
    started_at TIMESTAMP,
    completed_at TIMESTAMP,
    duration_seconds REAL,
    result_summary TEXT, -- JSON object with task results
    error_message TEXT,
    
    FOREIGN KEY (agent_id) REFERENCES agents(agent_id) ON DELETE CASCADE,
    INDEX idx_agent_id (agent_id),
    INDEX idx_status (status),
    INDEX idx_started_at (started_at DESC)
);

-- Agent Metrics
-- Performance metrics for each agent
CREATE TABLE IF NOT EXISTS agent_metrics (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    agent_id TEXT NOT NULL,
    metric_type TEXT NOT NULL, -- 'files_scanned', 'patterns_found', 'success_rate'
    metric_value REAL NOT NULL,
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    FOREIGN KEY (agent_id) REFERENCES agents(agent_id) ON DELETE CASCADE,
    INDEX idx_agent_metric (agent_id, metric_type),
    INDEX idx_timestamp (timestamp DESC)
);

-- ============================================================================
-- WEB SEARCH
-- ============================================================================

-- Web Search Results
-- All web searches performed and their results
CREATE TABLE IF NOT EXISTS web_searches (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    query TEXT NOT NULL,
    source TEXT NOT NULL, -- 'duckduckgo', 'searxng', 'perplexity'
    results_count INTEGER DEFAULT 0,
    search_timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    INDEX idx_query (query),
    INDEX idx_timestamp (search_timestamp DESC)
);

-- Web Search Results Detail
CREATE TABLE IF NOT EXISTS web_search_results (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    search_id INTEGER NOT NULL,
    title TEXT NOT NULL,
    url TEXT NOT NULL,
    snippet TEXT,
    relevance_score REAL DEFAULT 0.0,
    
    FOREIGN KEY (search_id) REFERENCES web_searches(id) ON DELETE CASCADE,
    INDEX idx_search_id (search_id)
);

-- ============================================================================
-- VOICE & VIDEO PRODUCTION
-- ============================================================================

-- Speaking Sessions
-- All aSiReM speaking sessions
CREATE TABLE IF NOT EXISTS speaking_sessions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    session_id TEXT NOT NULL UNIQUE,
    topic TEXT NOT NULL,
    narrative_type TEXT, -- 'greeting', 'explanation', 'narrative', 'cinematic'
    script_text TEXT,
    audio_path TEXT,
    video_path TEXT,
    duration_seconds REAL,
    tts_engine TEXT, -- 'xtts', 'f5-tts', 'macos-say'
    lipsync_method TEXT, -- 'musetalk', 'demo-video'
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    INDEX idx_topic (topic),
    INDEX idx_created_at (created_at DESC)
);

-- Narrative Productions
-- Multi-scene cinematic narratives with 9-expert deliberation
CREATE TABLE IF NOT EXISTS narrative_productions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    production_id TEXT NOT NULL UNIQUE,
    topic TEXT NOT NULL,
    scene_count INTEGER,
    total_duration_seconds REAL,
    veo3_credits_used INTEGER DEFAULT 0,
    deliberation_transcript TEXT, -- JSON of expert deliberation
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    INDEX idx_created_at (created_at DESC)
);

-- Narrative Scenes
-- Individual scenes within a cinematic narrative
CREATE TABLE IF NOT EXISTS narrative_scenes (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    production_id TEXT NOT NULL,
    scene_number INTEGER NOT NULL,
    scene_description TEXT,
    script_text TEXT,
    audio_path TEXT,
    veo3_prompt TEXT,
    video_path TEXT,
    credits_used INTEGER DEFAULT 0,
    
    FOREIGN KEY (production_id) REFERENCES narrative_productions(production_id) ON DELETE CASCADE,
    INDEX idx_production_id (production_id)
);

-- ============================================================================
-- VEO3 CREDITS & USAGE
-- ============================================================================

-- Veo3 Credit Transactions
-- Audit log of all Veo3 credit usage
CREATE TABLE IF NOT EXISTS veo3_transactions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    transaction_type TEXT NOT NULL, -- 'fast_video', 'quality_video', 'refund'
    credits_amount INTEGER NOT NULL, -- Negative for usage, positive for refunds
    credits_remaining INTEGER NOT NULL,
    description TEXT,
    production_id TEXT, -- Link to narrative production if applicable
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    INDEX idx_timestamp (timestamp DESC)
);

-- ============================================================================
-- VISUAL STREAMS
-- ============================================================================

-- Agent Visual Streams
-- History of all visual streams generated for agents
CREATE TABLE IF NOT EXISTS agent_visual_streams (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    agent_id TEXT NOT NULL,
    work_type TEXT NOT NULL, -- 'scanning', 'speaking', 'analyzing', 'searching'
    stream_path TEXT NOT NULL,
    context_data TEXT, -- JSON of stream context (metrics, file counts, etc.)
    duration_seconds REAL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    FOREIGN KEY (agent_id) REFERENCES agents(agent_id) ON DELETE CASCADE,
    INDEX idx_agent_work (agent_id, work_type),
    INDEX idx_created_at (created_at DESC)
);

-- ============================================================================
-- ACTIVITY LOG
-- ============================================================================

-- Activity Events
-- Real-time activity stream events (for replay and analytics)
CREATE TABLE IF NOT EXISTS activity_events (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    event_type TEXT NOT NULL, -- 'agent_started', 'file_discovered', 'pattern_found', etc.
    agent_id TEXT,
    event_data TEXT, -- JSON of event details
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    INDEX idx_event_type (event_type),
    INDEX idx_agent_id (agent_id),
    INDEX idx_timestamp (timestamp DESC)
);

-- ============================================================================
-- VIEWS (For Convenience)
-- ============================================================================

-- Active Agents View
CREATE VIEW IF NOT EXISTS v_active_agents AS
SELECT 
    a.agent_id,
    a.agent_name,
    a.agent_type,
    a.status,
    COUNT(t.id) as active_tasks,
    a.total_tasks_completed
FROM agents a
LEFT JOIN agent_tasks t ON a.agent_id = t.agent_id AND t.status IN ('pending', 'running')
GROUP BY a.agent_id;

-- Recent Discoveries View
CREATE VIEW IF NOT EXISTS v_recent_discoveries AS
SELECT 
    df.id,
    df.name,
    df.path,
    df.language,
    COUNT(fp.id) as pattern_count,
    df.discovered_at
FROM discovered_files df
LEFT JOIN file_patterns fp ON df.id = fp.file_id
GROUP BY df.id
ORDER BY df.discovered_at DESC
LIMIT 100;

-- Knowledge Graph Stats View
CREATE VIEW IF NOT EXISTS v_knowledge_stats AS
SELECT 
    (SELECT COUNT(*) FROM concepts) as total_concepts,
    (SELECT COUNT(*) FROM concept_relationships) as total_relationships,
    (SELECT COUNT(*) FROM discovered_files) as total_files,
    (SELECT COUNT(*) FROM file_patterns) as total_patterns;

-- Veo3 Credits Summary View
CREATE VIEW IF NOT EXISTS v_veo3_credits AS
SELECT 
    (SELECT veo3_credits_remaining FROM system_state WHERE id = 1) as credits_remaining,
    (SELECT COUNT(*) FROM veo3_transactions WHERE transaction_type = 'fast_video') as fast_videos_generated,
    (SELECT COUNT(*) FROM veo3_transactions WHERE transaction_type = 'quality_video') as quality_videos_generated,
    (SELECT SUM(ABS(credits_amount)) FROM veo3_transactions WHERE credits_amount < 0) as total_credits_used;

-- ============================================================================
-- TRIGGERS (Auto-update timestamps and computed fields)
-- ============================================================================

-- Update system_state timestamps
CREATE TRIGGER IF NOT EXISTS update_system_state_timestamp
AFTER UPDATE ON system_state
BEGIN
    UPDATE system_state SET updated_at = CURRENT_TIMESTAMP WHERE id = NEW.id;
END;

-- Update Veo3 credits in system_state when transaction occurs
CREATE TRIGGER IF NOT EXISTS update_veo3_credits
AFTER INSERT ON veo3_transactions
BEGIN
    UPDATE system_state 
    SET veo3_credits_remaining = NEW.credits_remaining 
    WHERE id = 1;
END;

-- Increment agent task count on completion
CREATE TRIGGER IF NOT EXISTS increment_agent_tasks
AFTER UPDATE ON agent_tasks
WHEN NEW.status = 'completed' AND OLD.status != 'completed'
BEGIN
    UPDATE agents 
    SET total_tasks_completed = total_tasks_completed + 1 
    WHERE agent_id = NEW.agent_id;
END;

-- Calculate task duration
CREATE TRIGGER IF NOT EXISTS calculate_task_duration
AFTER UPDATE ON agent_tasks
WHEN NEW.completed_at IS NOT NULL AND OLD.completed_at IS NULL
BEGIN
    UPDATE agent_tasks 
    SET duration_seconds = (
        julianday(NEW.completed_at) - julianday(NEW.started_at)
    ) * 86400.0 
    WHERE id = NEW.id;
END;

-- ============================================================================
-- INDEXES (Performance optimization)
-- ============================================================================

-- Composite indexes for common queries
CREATE INDEX IF NOT EXISTS idx_file_patterns_composite 
ON file_patterns(pattern_type, pattern_value);

CREATE INDEX IF NOT EXISTS idx_tasks_agent_status 
ON agent_tasks(agent_id, status, started_at DESC);

CREATE INDEX IF NOT EXISTS idx_concepts_category_score 
ON concepts(category, importance_score DESC);

-- ============================================================================
-- INITIAL DATA
-- ============================================================================

-- Register default agents
INSERT OR IGNORE INTO agents (agent_id, agent_name, agent_icon, agent_type) VALUES
    ('azirem', 'AZIREM', '👑', 'orchestrator'),
    ('scanner', 'Scanner', '🔍', 'discovery'),
    ('classifier', 'Classifier', '🏷️', 'analysis'),
    ('extractor', 'Extractor', '🔬', 'extraction'),
    ('researcher', 'Researcher', '🌐', 'search'),
    ('story_team', 'Story Team', '🤝', 'narrative'),
    ('director', 'Director', '🎬', 'narrative'),
    ('scriptwriter', 'Scriptwriter', '✍️', 'narrative'),
    ('visual_architect', 'Visual Architect', '🎨', 'narrative'),
    ('narrative_analyst', 'Narrative Analyst', '🎭', 'narrative'),
    ('drone_specialist', 'Drone Specialist', '🚁', 'narrative'),
    ('sound_designer', 'Sound Designer', '🎵', 'narrative'),
    ('tech_director', 'Tech Director', '⚙️', 'narrative');

-- ============================================================================
-- MAINTENANCE QUERIES
-- ============================================================================

-- Clean up old activity events (keep last 10,000)
-- Run this periodically to prevent database bloat
-- DELETE FROM activity_events WHERE id NOT IN (
--     SELECT id FROM activity_events ORDER BY timestamp DESC LIMIT 10000
-- );

-- Vacuum to reclaim space (run manually when needed)
-- VACUUM;

-- ============================================================================
-- END OF SCHEMA
-- ============================================================================
