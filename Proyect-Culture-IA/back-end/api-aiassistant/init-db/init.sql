CREATE TABLE IF NOT EXISTS chat_queries (
    id UUID PRIMARY KEY,
    user_id VARCHAR(255) NOT NULL,
    query_text TEXT NOT NULL,
    response_text TEXT,
    ai_provider VARCHAR(50) NOT NULL DEFAULT 'openai',
    status VARCHAR(20) NOT NULL DEFAULT 'pending',
    metadata JSONB,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_chat_queries_user_id ON chat_queries (user_id);
