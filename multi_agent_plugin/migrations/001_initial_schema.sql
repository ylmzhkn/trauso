CREATE TABLE IF NOT EXISTS tasks (
    task_id UUID PRIMARY KEY,
    original_prompt TEXT NOT NULL,
    status TEXT NOT NULL,
    assigned_agent TEXT,
    retry_count INTEGER NOT NULL DEFAULT 0,
    checkpoint JSONB NOT NULL DEFAULT '{}'::jsonb,
    result JSONB,
    error TEXT,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS agent_events (
    event_id BIGSERIAL PRIMARY KEY,
    task_id UUID REFERENCES tasks(task_id),
    agent_id TEXT NOT NULL,
    event_type TEXT NOT NULL,
    payload JSONB NOT NULL DEFAULT '{}'::jsonb,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS agent_messages (
    message_id UUID PRIMARY KEY,
    task_id UUID NOT NULL REFERENCES tasks(task_id),
    sender TEXT NOT NULL,
    recipient TEXT NOT NULL,
    message_type TEXT NOT NULL,
    correlation_id UUID NOT NULL,
    payload JSONB NOT NULL DEFAULT '{}'::jsonb,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_tasks_status ON tasks(status);
CREATE INDEX IF NOT EXISTS idx_agent_events_task_time ON agent_events(task_id, created_at);
CREATE INDEX IF NOT EXISTS idx_agent_messages_task_time ON agent_messages(task_id, created_at);
