-- Migração segura: adiciona campos para encerramento de vagas sem apagar dados.
ALTER TABLE vagas ADD COLUMN IF NOT EXISTS encerrada_em TEXT;
ALTER TABLE vagas ADD COLUMN IF NOT EXISTS encerrada_motivo_tipo TEXT;
ALTER TABLE vagas ADD COLUMN IF NOT EXISTS encerrada_motivo TEXT;
ALTER TABLE vagas ADD COLUMN IF NOT EXISTS vigivagas_ajudou_contratacao TEXT;
ALTER TABLE vagas ADD COLUMN IF NOT EXISTS contratacoes_quantidade INTEGER DEFAULT 0;
ALTER TABLE vagas ADD COLUMN IF NOT EXISTS encerrada_observacoes TEXT;
CREATE INDEX IF NOT EXISTS idx_vagas_encerrada_em ON vagas (encerrada_em);
