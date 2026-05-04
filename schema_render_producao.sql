-- VIGIVAGAS BETA -> PRODUÇÃO / RENDER
-- Rode este arquivo no PostgreSQL do Render antes do checklist real.
-- Ele NÃO apaga dados. Apenas cria tabelas/colunas necessárias para LGPD, segurança e recuperação de senha.

CREATE TABLE IF NOT EXISTS password_resets (
    id SERIAL PRIMARY KEY,
    user_type TEXT NOT NULL,
    user_id INTEGER NOT NULL,
    token_hash TEXT UNIQUE,
    expires_at TEXT NOT NULL,
    used_at TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

ALTER TABLE password_resets ADD COLUMN IF NOT EXISTS user_type TEXT;
ALTER TABLE password_resets ADD COLUMN IF NOT EXISTS user_id INTEGER;
ALTER TABLE password_resets ADD COLUMN IF NOT EXISTS token_hash TEXT;
ALTER TABLE password_resets ADD COLUMN IF NOT EXISTS expires_at TEXT;
ALTER TABLE password_resets ADD COLUMN IF NOT EXISTS used_at TEXT;
ALTER TABLE password_resets ADD COLUMN IF NOT EXISTS created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP;

-- Compatibilidade: se tabela antiga tinha coluna token, copia para token_hash somente quando existir.
-- O código atual salva apenas HASH do token, não o token puro.
DO $$
BEGIN
    IF EXISTS (SELECT 1 FROM information_schema.columns WHERE table_schema='public' AND table_name='password_resets' AND column_name='token') THEN
        EXECUTE 'UPDATE password_resets SET token_hash = token WHERE token_hash IS NULL';
    END IF;
END $$;

CREATE INDEX IF NOT EXISTS idx_password_resets_token_hash ON password_resets (token_hash);
CREATE INDEX IF NOT EXISTS idx_password_resets_user ON password_resets (user_type, user_id);

CREATE TABLE IF NOT EXISTS lgpd_consents (
    id SERIAL PRIMARY KEY,
    user_type TEXT NOT NULL,
    user_id INTEGER,
    email TEXT,
    policy_version TEXT NOT NULL DEFAULT '1.0',
    terms_version TEXT NOT NULL DEFAULT '1.0',
    consent_text TEXT NOT NULL,
    ip_address TEXT,
    user_agent TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_lgpd_consents_user ON lgpd_consents (user_type, user_id);
CREATE INDEX IF NOT EXISTS idx_lgpd_consents_email ON lgpd_consents (email);

CREATE TABLE IF NOT EXISTS audit_logs (
    id SERIAL PRIMARY KEY,
    actor_type TEXT NOT NULL,
    actor_id TEXT,
    action TEXT NOT NULL,
    entity_type TEXT,
    entity_id TEXT,
    details TEXT,
    ip_address TEXT,
    user_agent TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_audit_logs_created_at ON audit_logs (created_at);
CREATE INDEX IF NOT EXISTS idx_audit_logs_actor ON audit_logs (actor_type, actor_id);
CREATE INDEX IF NOT EXISTS idx_audit_logs_entity ON audit_logs (entity_type, entity_id);

CREATE TABLE IF NOT EXISTS lgpd_requests (
    id SERIAL PRIMARY KEY,
    user_type TEXT NOT NULL,
    user_id INTEGER,
    email TEXT NOT NULL,
    request_type TEXT NOT NULL,
    status TEXT NOT NULL DEFAULT 'pendente',
    details TEXT,
    ip_address TEXT,
    user_agent TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    resolved_at TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_lgpd_requests_status ON lgpd_requests (status);
CREATE INDEX IF NOT EXISTS idx_lgpd_requests_email ON lgpd_requests (email);

ALTER TABLE recrutadores ADD COLUMN IF NOT EXISTS cidade TEXT;
ALTER TABLE recrutadores ADD COLUMN IF NOT EXISTS estado TEXT;
ALTER TABLE recrutadores ADD COLUMN IF NOT EXISTS cnpj TEXT;
ALTER TABLE recrutadores ADD COLUMN IF NOT EXISTS razao_social TEXT;
ALTER TABLE recrutadores ADD COLUMN IF NOT EXISTS situacao_cadastral TEXT;
ALTER TABLE recrutadores ADD COLUMN IF NOT EXISTS site_empresa TEXT;
ALTER TABLE recrutadores ADD COLUMN IF NOT EXISTS descricao_empresa TEXT;
ALTER TABLE recrutadores ADD COLUMN IF NOT EXISTS cnpj_modo_validacao TEXT DEFAULT 'online';
ALTER TABLE recrutadores ADD COLUMN IF NOT EXISTS email_verificado INTEGER DEFAULT 0;
ALTER TABLE recrutadores ADD COLUMN IF NOT EXISTS email_token TEXT;
ALTER TABLE recrutadores ADD COLUMN IF NOT EXISTS email_token_expires_at TEXT;
ALTER TABLE recrutadores ADD COLUMN IF NOT EXISTS email_ultimo_envio_em TEXT;
ALTER TABLE recrutadores ADD COLUMN IF NOT EXISTS ip_cadastro TEXT;
ALTER TABLE recrutadores ADD COLUMN IF NOT EXISTS user_agent TEXT;
ALTER TABLE recrutadores ADD COLUMN IF NOT EXISTS antifraude_score INTEGER DEFAULT 0;
ALTER TABLE recrutadores ADD COLUMN IF NOT EXISTS antifraude_flags TEXT;
ALTER TABLE recrutadores ADD COLUMN IF NOT EXISTS antifraude_status TEXT DEFAULT 'normal';

ALTER TABLE vigilantes ADD COLUMN IF NOT EXISTS estado TEXT;
ALTER TABLE vigilantes ADD COLUMN IF NOT EXISTS ip_cadastro TEXT;
ALTER TABLE vigilantes ADD COLUMN IF NOT EXISTS user_agent TEXT;
ALTER TABLE vigilantes ADD COLUMN IF NOT EXISTS antifraude_score INTEGER DEFAULT 0;
ALTER TABLE vigilantes ADD COLUMN IF NOT EXISTS antifraude_flags TEXT;
ALTER TABLE vigilantes ADD COLUMN IF NOT EXISTS antifraude_status TEXT DEFAULT 'normal';
ALTER TABLE vigilantes ADD COLUMN IF NOT EXISTS objetivo_cargo TEXT;
ALTER TABLE vigilantes ADD COLUMN IF NOT EXISTS escolaridade TEXT;
ALTER TABLE vigilantes ADD COLUMN IF NOT EXISTS possui_cfv TEXT;
ALTER TABLE vigilantes ADD COLUMN IF NOT EXISTS instituicao_formacao TEXT;
ALTER TABLE vigilantes ADD COLUMN IF NOT EXISTS data_ultima_reciclagem TEXT;
ALTER TABLE vigilantes ADD COLUMN IF NOT EXISTS curso_ultima_reciclagem TEXT;
ALTER TABLE vigilantes ADD COLUMN IF NOT EXISTS ultima_experiencia_profissional TEXT;

ALTER TABLE vagas ADD COLUMN IF NOT EXISTS recrutador_id INTEGER;

CREATE INDEX IF NOT EXISTS idx_vigilantes_cidade ON vigilantes (cidade);
CREATE INDEX IF NOT EXISTS idx_vigilantes_status ON vigilantes (status);
CREATE INDEX IF NOT EXISTS idx_recrutadores_status ON recrutadores (status);
CREATE INDEX IF NOT EXISTS idx_vagas_status ON vagas (status);
CREATE INDEX IF NOT EXISTS idx_vagas_recrutador_id ON vagas (recrutador_id);
CREATE INDEX IF NOT EXISTS idx_candidaturas_vaga_id ON candidaturas (vaga_id);
CREATE INDEX IF NOT EXISTS idx_candidaturas_vigilante_id ON candidaturas (vigilante_id);
