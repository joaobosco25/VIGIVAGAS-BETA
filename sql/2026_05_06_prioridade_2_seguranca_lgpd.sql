-- Prioridade 2 - Segurança e LGPD grave
-- Execute no PostgreSQL do Render antes/depois do deploy se RUN_INIT_DB não estiver habilitado.

CREATE TABLE IF NOT EXISTS rate_limit_events (
    id SERIAL PRIMARY KEY,
    scope TEXT NOT NULL,
    key_value TEXT NOT NULL,
    created_at DOUBLE PRECISION NOT NULL
);

CREATE INDEX IF NOT EXISTS idx_rate_limit_scope_key_time
ON rate_limit_events (scope, key_value, created_at);

-- Exemplo de anonimização manual de IP/user-agent antigos (ajuste o intervalo conforme política):
-- UPDATE vigilantes SET ip_cadastro = NULL, user_agent = NULL WHERE created_at < NOW() - INTERVAL '180 days';
-- UPDATE recrutadores SET ip_cadastro = NULL, user_agent = NULL WHERE created_at < NOW() - INTERVAL '180 days';
-- DELETE FROM rate_limit_events WHERE created_at < EXTRACT(EPOCH FROM NOW() - INTERVAL '7 days');
