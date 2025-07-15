-- Bruno AI V3.1 Database Schema
-- Complete memory and context persistence system

-- User contexts table for cross-session recall
CREATE TABLE IF NOT EXISTS user_contexts (
    id SERIAL PRIMARY KEY,
    context_id VARCHAR(255) NOT NULL UNIQUE,
    user_id VARCHAR(100),
    data JSONB NOT NULL,
    preferences JSONB DEFAULT '{}',
    budget_info JSONB DEFAULT '{}',
    dietary_restrictions TEXT[],
    family_size INTEGER DEFAULT 4,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    expires_at TIMESTAMP,
    INDEX idx_context_id (context_id),
    INDEX idx_user_id (user_id),
    INDEX idx_updated_at (updated_at)
);

-- Agent history table for tracking interactions
CREATE TABLE IF NOT EXISTS agent_history (
    id SERIAL PRIMARY KEY,
    agent_id VARCHAR(100) NOT NULL,
    context_id VARCHAR(255) NOT NULL,
    user_id VARCHAR(100),
    action_type VARCHAR(100) NOT NULL,
    data JSONB NOT NULL,
    request_tokens INTEGER DEFAULT 0,
    response_tokens INTEGER DEFAULT 0,
    processing_time FLOAT DEFAULT 0,
    success BOOLEAN DEFAULT TRUE,
    error_message TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_agent_id (agent_id),
    INDEX idx_context_id (context_id),
    INDEX idx_user_id (user_id),
    INDEX idx_action_type (action_type),
    INDEX idx_created_at (created_at)
);

-- Agent memory table (existing, enhanced)
CREATE TABLE IF NOT EXISTS agent_memory (
    id SERIAL PRIMARY KEY,
    agent_id VARCHAR(100) NOT NULL,
    session_id VARCHAR(100),
    context_id VARCHAR(255),
    memory_type VARCHAR(50) NOT NULL,
    content JSONB NOT NULL,
    metadata JSONB DEFAULT '{}',
    ttl_seconds INTEGER DEFAULT 3600,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    expires_at TIMESTAMP,
    INDEX idx_agent_session (agent_id, session_id),
    INDEX idx_context_id (context_id),
    INDEX idx_memory_type (memory_type),
    INDEX idx_expires_at (expires_at)
);

-- Performance metrics table (existing, enhanced)
CREATE TABLE IF NOT EXISTS performance_metrics (
    id SERIAL PRIMARY KEY,
    agent_id VARCHAR(100) NOT NULL,
    endpoint VARCHAR(100) NOT NULL,
    context_id VARCHAR(255),
    response_time FLOAT NOT NULL,
    token_usage INTEGER DEFAULT 0,
    cache_hit BOOLEAN DEFAULT FALSE,
    compression_ratio FLOAT DEFAULT 1.0,
    status_code INTEGER DEFAULT 200,
    error_type VARCHAR(100),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_agent_endpoint (agent_id, endpoint),
    INDEX idx_context_id (context_id),
    INDEX idx_created_at (created_at)
);

-- User feedback table (existing, enhanced)
CREATE TABLE IF NOT EXISTS user_feedback (
    id SERIAL PRIMARY KEY,
    session_id VARCHAR(100) NOT NULL,
    agent_id VARCHAR(100) NOT NULL,
    context_id VARCHAR(255),
    user_id VARCHAR(100),
    rating INTEGER CHECK (rating >= 1 AND rating <= 5),
    feedback_text TEXT,
    feedback_type VARCHAR(50),
    improvement_suggestions TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_session_agent (session_id, agent_id),
    INDEX idx_context_id (context_id),
    INDEX idx_user_id (user_id),
    INDEX idx_rating (rating)
);

-- Shopping history for budget analysis
CREATE TABLE IF NOT EXISTS shopping_history (
    id SERIAL PRIMARY KEY,
    user_id VARCHAR(100) NOT NULL,
    context_id VARCHAR(255),
    shopping_list JSONB NOT NULL,
    total_cost DECIMAL(10,2),
    items_purchased INTEGER DEFAULT 0,
    store_id VARCHAR(100),
    purchase_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    preferences_applied JSONB DEFAULT '{}',
    INDEX idx_user_id (user_id),
    INDEX idx_context_id (context_id),
    INDEX idx_purchase_date (purchase_date)
);

-- Meal plans for context persistence
CREATE TABLE IF NOT EXISTS meal_plans (
    id SERIAL PRIMARY KEY,
    user_id VARCHAR(100) NOT NULL,
    context_id VARCHAR(255),
    plan_data JSONB NOT NULL,
    duration_days INTEGER DEFAULT 7,
    family_size INTEGER DEFAULT 4,
    budget_used DECIMAL(10,2),
    cuisine_preferences TEXT[],
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    active_until TIMESTAMP,
    INDEX idx_user_id (user_id),
    INDEX idx_context_id (context_id),
    INDEX idx_active_until (active_until)
);

-- Token usage tracking for optimization
CREATE TABLE IF NOT EXISTS token_usage (
    id SERIAL PRIMARY KEY,
    agent_id VARCHAR(100) NOT NULL,
    context_id VARCHAR(255),
    model_used VARCHAR(100) NOT NULL,
    prompt_tokens INTEGER DEFAULT 0,
    completion_tokens INTEGER DEFAULT 0,
    total_tokens INTEGER DEFAULT 0,
    compression_applied BOOLEAN DEFAULT FALSE,
    cost_estimate DECIMAL(10,4),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_agent_id (agent_id),
    INDEX idx_context_id (context_id),
    INDEX idx_model_used (model_used),
    INDEX idx_created_at (created_at)
);

-- Cache performance metrics
CREATE TABLE IF NOT EXISTS cache_metrics (
    id SERIAL PRIMARY KEY,
    agent_id VARCHAR(100) NOT NULL,
    cache_key VARCHAR(255) NOT NULL,
    hit_count INTEGER DEFAULT 0,
    miss_count INTEGER DEFAULT 0,
    ttl_seconds INTEGER DEFAULT 3600,
    avg_retrieval_time FLOAT DEFAULT 0,
    last_accessed TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_agent_key (agent_id, cache_key),
    INDEX idx_last_accessed (last_accessed)
);

-- A2A message logs for debugging
CREATE TABLE IF NOT EXISTS a2a_messages (
    id SERIAL PRIMARY KEY,
    message_id VARCHAR(255) NOT NULL,
    from_agent VARCHAR(100) NOT NULL,
    to_agent VARCHAR(100) NOT NULL,
    context_id VARCHAR(255),
    message_type VARCHAR(50) DEFAULT 'query',
    payload JSONB NOT NULL,
    response JSONB,
    processing_time FLOAT DEFAULT 0,
    success BOOLEAN DEFAULT TRUE,
    error_message TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_message_id (message_id),
    INDEX idx_from_agent (from_agent),
    INDEX idx_to_agent (to_agent),
    INDEX idx_context_id (context_id)
);

-- Auto-cleanup functions for expired data
CREATE OR REPLACE FUNCTION cleanup_expired_data() RETURNS void AS $$
BEGIN
    -- Clean up expired user contexts
    DELETE FROM user_contexts WHERE expires_at IS NOT NULL AND expires_at < NOW();
    
    -- Clean up expired agent memory
    DELETE FROM agent_memory WHERE expires_at IS NOT NULL AND expires_at < NOW();
    
    -- Clean up old performance metrics (keep last 30 days)
    DELETE FROM performance_metrics WHERE created_at < NOW() - INTERVAL '30 days';
    
    -- Clean up old token usage data (keep last 90 days)
    DELETE FROM token_usage WHERE created_at < NOW() - INTERVAL '90 days';
    
    -- Clean up old A2A messages (keep last 7 days)
    DELETE FROM a2a_messages WHERE created_at < NOW() - INTERVAL '7 days';
    
    -- Reset cache metrics for old entries
    UPDATE cache_metrics SET hit_count = 0, miss_count = 0 
    WHERE last_accessed < NOW() - INTERVAL '7 days';
END;
$$ LANGUAGE plpgsql;

-- Create indexes for better performance
CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_user_contexts_preferences ON user_contexts USING GIN (preferences);
CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_agent_history_data ON agent_history USING GIN (data);
CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_meal_plans_data ON meal_plans USING GIN (plan_data);
CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_shopping_history_list ON shopping_history USING GIN (shopping_list);
CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_a2a_messages_payload ON a2a_messages USING GIN (payload);

-- Update triggers for timestamp management
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER update_user_contexts_updated_at BEFORE UPDATE ON user_contexts FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_agent_memory_updated_at BEFORE UPDATE ON agent_memory FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
