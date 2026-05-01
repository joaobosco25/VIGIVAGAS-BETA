import os
import re
import sqlite3
from pathlib import Path
from typing import Iterable
from werkzeug.security import generate_password_hash

try:
    import psycopg
    from psycopg.rows import dict_row
except Exception:  # pragma: no cover - dependency may not be installed locally yet
    psycopg = None
    dict_row = None

BASE_DIR = Path(__file__).resolve().parent.parent
DEFAULT_DATABASE = BASE_DIR / "database" / "database.db"


def get_database_path() -> Path:
    return Path(os.getenv("DATABASE_PATH", str(DEFAULT_DATABASE))).resolve()


def get_database_url() -> str:
    return (os.getenv("DATABASE_URL", "") or "").strip()


def require_postgres() -> bool:
    return (os.getenv("REQUIRE_POSTGRES", "1") or "1").strip() != "0"


def allow_sqlite_fallback() -> bool:
    return (os.getenv("ALLOW_SQLITE_FALLBACK", "0") or "0").strip() == "1"


def using_postgres() -> bool:
    url = get_database_url().lower()
    return url.startswith("postgresql://") or url.startswith("postgres://")


def _normalize_database_url(url: str) -> str:
    if url.startswith("postgres://"):
        return "postgresql://" + url[len("postgres://"):]
    return url


def _adapt_sql(sql: str, postgres: bool) -> str:
    if not postgres:
        return sql
    return re.sub(r"\?", "%s", sql)


class CursorWrapper:
    def __init__(self, cursor, postgres: bool = False):
        self._cursor = cursor
        self._postgres = postgres

    def execute(self, sql: str, params: Iterable | None = None):
        sql = _adapt_sql(sql, self._postgres)
        if params is None:
            self._cursor.execute(sql)
        else:
            self._cursor.execute(sql, params)
        return self

    def fetchone(self):
        return self._cursor.fetchone()

    def fetchall(self):
        return self._cursor.fetchall()

    @property
    def lastrowid(self):
        return getattr(self._cursor, "lastrowid", None)


class ConnectionWrapper:
    def __init__(self, connection, postgres: bool = False):
        self._connection = connection
        self._postgres = postgres

    def cursor(self):
        return CursorWrapper(self._connection.cursor(), self._postgres)

    def execute(self, sql: str, params: Iterable | None = None):
        cursor = self.cursor()
        return cursor.execute(sql, params)

    def commit(self):
        self._connection.commit()

    def rollback(self):
        self._connection.rollback()

    def close(self):
        self._connection.close()

    @property
    def raw(self):
        return self._connection


def get_connection():
    if using_postgres():
        if psycopg is None:
            raise RuntimeError(
                "PostgreSQL configurado, mas a dependência 'psycopg[binary]' não está instalada. "
                "Execute: pip install -r requirements.txt"
            )
        conn = psycopg.connect(_normalize_database_url(get_database_url()), row_factory=dict_row)
        return ConnectionWrapper(conn, postgres=True)

    if require_postgres() and not allow_sqlite_fallback():
        raise RuntimeError(
            "DATABASE_URL não está configurada com PostgreSQL. "
            "Para ambiente beta/produção, defina uma DATABASE_URL postgresql://... válida. "
            "Use ALLOW_SQLITE_FALLBACK=1 apenas em desenvolvimento local temporário."
        )

    db_path = get_database_path()
    db_path.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    return ConnectionWrapper(conn, postgres=False)


def _sqlite_column_names(cursor, table: str) -> set[str]:
    cursor.execute(f"PRAGMA table_info({table})")
    return {row[1] for row in cursor.fetchall()}


def _postgres_column_names(cursor, table: str) -> set[str]:
    rows = cursor.execute(
        """
        SELECT column_name
        FROM information_schema.columns
        WHERE table_schema = 'public' AND table_name = ?
        """,
        (table,),
    ).fetchall()
    return {row["column_name"] for row in rows}


def _column_names(cursor, table: str, postgres: bool) -> set[str]:
    return _postgres_column_names(cursor, table) if postgres else _sqlite_column_names(cursor, table)


def init_db():
    conn = get_connection()
    cursor = conn.cursor()
    postgres = using_postgres()

    id_type = "SERIAL PRIMARY KEY" if postgres else "INTEGER PRIMARY KEY AUTOINCREMENT"
    timestamp_type = "TIMESTAMP DEFAULT CURRENT_TIMESTAMP"

    cursor.execute(
        f"""
        CREATE TABLE IF NOT EXISTS candidatos (
            id {id_type},
            nome TEXT NOT NULL,
            cpf TEXT NOT NULL,
            telefone TEXT NOT NULL,
            email TEXT NOT NULL,
            cidade TEXT NOT NULL,
            estado TEXT,
            endereco TEXT,
            cep TEXT,
            curso TEXT NOT NULL,
            reciclagem TEXT,
            area TEXT,
            mensagem TEXT,
            ip_cadastro TEXT,
            user_agent TEXT,
            antifraude_score INTEGER NOT NULL DEFAULT 0,
            antifraude_flags TEXT,
            antifraude_status TEXT NOT NULL DEFAULT 'normal',
            created_at {timestamp_type}
        )
        """
    )

    cursor.execute(
        f"""
        CREATE TABLE IF NOT EXISTS administradores (
            id {id_type},
            username TEXT NOT NULL UNIQUE,
            password TEXT NOT NULL,
            nome_exibicao TEXT
        )
        """
    )

    cursor.execute(
        f"""
        CREATE TABLE IF NOT EXISTS mauricio_usuarios (
            id {id_type},
            username TEXT NOT NULL UNIQUE,
            password TEXT NOT NULL,
            nome_exibicao TEXT,
            ativo INTEGER NOT NULL DEFAULT 1,
            created_at {timestamp_type}
        )
        """
    )

    cursor.execute(
        f"""
        CREATE TABLE IF NOT EXISTS recrutadores (
            id {id_type},
            nome_empresa TEXT,
            nome_responsavel TEXT NOT NULL,
            email TEXT NOT NULL UNIQUE,
            telefone TEXT,
            cidade TEXT,
            estado TEXT,
            cnpj TEXT,
            razao_social TEXT,
            situacao_cadastral TEXT,
            site_empresa TEXT,
            descricao_empresa TEXT,
            cnpj_modo_validacao TEXT NOT NULL DEFAULT 'online',
            email_verificado INTEGER NOT NULL DEFAULT 0,
            email_token TEXT,
            email_token_expires_at TEXT,
            email_ultimo_envio_em TEXT,
            ip_cadastro TEXT,
            user_agent TEXT,
            antifraude_score INTEGER NOT NULL DEFAULT 0,
            antifraude_flags TEXT,
            antifraude_status TEXT NOT NULL DEFAULT 'normal',
            password TEXT NOT NULL,
            status TEXT NOT NULL DEFAULT 'pendente',
            created_at {timestamp_type}
        )
        """
    )

    cursor.execute(
        f"""
        CREATE TABLE IF NOT EXISTS vigilantes (
            id {id_type},
            nome TEXT NOT NULL,
            cpf TEXT NOT NULL UNIQUE,
            telefone TEXT NOT NULL,
            email TEXT NOT NULL UNIQUE,
            cidade TEXT NOT NULL,
            estado TEXT,
            endereco TEXT,
            cep TEXT,
            curso TEXT,
            reciclagem TEXT,
            area_interesse TEXT,
            resumo_profissional TEXT,
            objetivo_cargo TEXT,
            escolaridade TEXT,
            possui_cfv TEXT,
            instituicao_formacao TEXT,
            ext_ctv TEXT,
            ext_cea TEXT,
            ext_csp TEXT,
            ext_cnl1 TEXT,
            ext_ces TEXT,
            data_ultima_reciclagem TEXT,
            curso_ultima_reciclagem TEXT,
            ultima_experiencia_profissional TEXT,
            ip_cadastro TEXT,
            user_agent TEXT,
            antifraude_score INTEGER NOT NULL DEFAULT 0,
            antifraude_flags TEXT,
            antifraude_status TEXT NOT NULL DEFAULT 'normal',
            password TEXT NOT NULL,
            status TEXT NOT NULL DEFAULT 'ativo',
            created_at {timestamp_type}
        )
        """
    )

    cursor.execute(
        f"""
        CREATE TABLE IF NOT EXISTS vagas (
            id {id_type},
            titulo TEXT NOT NULL,
            empresa TEXT NOT NULL,
            cidade TEXT NOT NULL,
            estado TEXT NOT NULL,
            escala TEXT,
            salario TEXT,
            descricao TEXT NOT NULL,
            requisitos TEXT,
            contato TEXT,
            link_candidatura TEXT,
            recrutador_id INTEGER,
            status TEXT NOT NULL DEFAULT 'ativa',
            created_at {timestamp_type},
            FOREIGN KEY (recrutador_id) REFERENCES recrutadores (id)
        )
        """
    )

    cursor.execute(
        f"""
        CREATE TABLE IF NOT EXISTS candidaturas (
            id {id_type},
            vigilante_id INTEGER NOT NULL,
            vaga_id INTEGER NOT NULL,
            status TEXT NOT NULL DEFAULT 'Recebida',
            observacoes TEXT,
            created_at {timestamp_type},
            updated_at {timestamp_type},
            UNIQUE(vigilante_id, vaga_id),
            FOREIGN KEY (vigilante_id) REFERENCES vigilantes (id),
            FOREIGN KEY (vaga_id) REFERENCES vagas (id)
        )
        """
    )



    cursor.execute(
        f"""
        CREATE TABLE IF NOT EXISTS password_resets (
            id {id_type},
            user_type TEXT NOT NULL,
            user_id INTEGER NOT NULL,
            token_hash TEXT NOT NULL UNIQUE,
            expires_at TEXT NOT NULL,
            used_at TEXT,
            created_at {timestamp_type}
        )
        """
    )

    cursor.execute(
        f"""
        CREATE TABLE IF NOT EXISTS lgpd_consents (
            id {id_type},
            user_type TEXT NOT NULL,
            user_id INTEGER,
            email TEXT,
            policy_version TEXT NOT NULL,
            terms_version TEXT NOT NULL,
            consent_text TEXT NOT NULL,
            ip_address TEXT,
            user_agent TEXT,
            created_at {timestamp_type}
        )
        """
    )

    cursor.execute(
        f"""
        CREATE TABLE IF NOT EXISTS audit_logs (
            id {id_type},
            actor_type TEXT NOT NULL,
            actor_id TEXT,
            action TEXT NOT NULL,
            entity_type TEXT,
            entity_id TEXT,
            details TEXT,
            ip_address TEXT,
            user_agent TEXT,
            created_at {timestamp_type}
        )
        """
    )

    candidatos_columns = _column_names(cursor, "candidatos", postgres)
    if "ip_cadastro" not in candidatos_columns:
        cursor.execute("ALTER TABLE candidatos ADD COLUMN ip_cadastro TEXT")
    if "user_agent" not in candidatos_columns:
        cursor.execute("ALTER TABLE candidatos ADD COLUMN user_agent TEXT")
    if "antifraude_score" not in candidatos_columns:
        cursor.execute("ALTER TABLE candidatos ADD COLUMN antifraude_score INTEGER NOT NULL DEFAULT 0")
    if "antifraude_flags" not in candidatos_columns:
        cursor.execute("ALTER TABLE candidatos ADD COLUMN antifraude_flags TEXT")
    if "antifraude_status" not in candidatos_columns:
        cursor.execute("ALTER TABLE candidatos ADD COLUMN antifraude_status TEXT NOT NULL DEFAULT 'normal'")
    if "estado" not in candidatos_columns:
        cursor.execute("ALTER TABLE candidatos ADD COLUMN estado TEXT")

    recrutadores_columns = _column_names(cursor, "recrutadores", postgres)
    if "cnpj" not in recrutadores_columns:
        cursor.execute("ALTER TABLE recrutadores ADD COLUMN cnpj TEXT")
    if "razao_social" not in recrutadores_columns:
        cursor.execute("ALTER TABLE recrutadores ADD COLUMN razao_social TEXT")
    if "situacao_cadastral" not in recrutadores_columns:
        cursor.execute("ALTER TABLE recrutadores ADD COLUMN situacao_cadastral TEXT")
    if "site_empresa" not in recrutadores_columns:
        cursor.execute("ALTER TABLE recrutadores ADD COLUMN site_empresa TEXT")
    if "descricao_empresa" not in recrutadores_columns:
        cursor.execute("ALTER TABLE recrutadores ADD COLUMN descricao_empresa TEXT")
    if "cnpj_modo_validacao" not in recrutadores_columns:
        cursor.execute("ALTER TABLE recrutadores ADD COLUMN cnpj_modo_validacao TEXT NOT NULL DEFAULT 'online'")
    if "email_verificado" not in recrutadores_columns:
        cursor.execute("ALTER TABLE recrutadores ADD COLUMN email_verificado INTEGER NOT NULL DEFAULT 0")
    if "email_token" not in recrutadores_columns:
        cursor.execute("ALTER TABLE recrutadores ADD COLUMN email_token TEXT")
    if "email_token_expires_at" not in recrutadores_columns:
        cursor.execute("ALTER TABLE recrutadores ADD COLUMN email_token_expires_at TEXT")
    if "email_ultimo_envio_em" not in recrutadores_columns:
        cursor.execute("ALTER TABLE recrutadores ADD COLUMN email_ultimo_envio_em TEXT")
    if "ip_cadastro" not in recrutadores_columns:
        cursor.execute("ALTER TABLE recrutadores ADD COLUMN ip_cadastro TEXT")
    if "user_agent" not in recrutadores_columns:
        cursor.execute("ALTER TABLE recrutadores ADD COLUMN user_agent TEXT")
    if "antifraude_score" not in recrutadores_columns:
        cursor.execute("ALTER TABLE recrutadores ADD COLUMN antifraude_score INTEGER NOT NULL DEFAULT 0")
    if "antifraude_flags" not in recrutadores_columns:
        cursor.execute("ALTER TABLE recrutadores ADD COLUMN antifraude_flags TEXT")
    if "antifraude_status" not in recrutadores_columns:
        cursor.execute("ALTER TABLE recrutadores ADD COLUMN antifraude_status TEXT NOT NULL DEFAULT 'normal'")
    if "cidade" not in recrutadores_columns:
        cursor.execute("ALTER TABLE recrutadores ADD COLUMN cidade TEXT")
    if "estado" not in recrutadores_columns:
        cursor.execute("ALTER TABLE recrutadores ADD COLUMN estado TEXT")

    vigilantes_columns = _column_names(cursor, "vigilantes", postgres)
    if "ip_cadastro" not in vigilantes_columns:
        cursor.execute("ALTER TABLE vigilantes ADD COLUMN ip_cadastro TEXT")
    if "user_agent" not in vigilantes_columns:
        cursor.execute("ALTER TABLE vigilantes ADD COLUMN user_agent TEXT")
    if "antifraude_score" not in vigilantes_columns:
        cursor.execute("ALTER TABLE vigilantes ADD COLUMN antifraude_score INTEGER NOT NULL DEFAULT 0")
    if "antifraude_flags" not in vigilantes_columns:
        cursor.execute("ALTER TABLE vigilantes ADD COLUMN antifraude_flags TEXT")
    if "antifraude_status" not in vigilantes_columns:
        cursor.execute("ALTER TABLE vigilantes ADD COLUMN antifraude_status TEXT NOT NULL DEFAULT 'normal'")
    if "objetivo_cargo" not in vigilantes_columns:
        cursor.execute("ALTER TABLE vigilantes ADD COLUMN objetivo_cargo TEXT")
    if "escolaridade" not in vigilantes_columns:
        cursor.execute("ALTER TABLE vigilantes ADD COLUMN escolaridade TEXT")
    if "possui_cfv" not in vigilantes_columns:
        cursor.execute("ALTER TABLE vigilantes ADD COLUMN possui_cfv TEXT")
    if "instituicao_formacao" not in vigilantes_columns:
        cursor.execute("ALTER TABLE vigilantes ADD COLUMN instituicao_formacao TEXT")
    if "ext_ctv" not in vigilantes_columns:
        cursor.execute("ALTER TABLE vigilantes ADD COLUMN ext_ctv TEXT")
    if "ext_cea" not in vigilantes_columns:
        cursor.execute("ALTER TABLE vigilantes ADD COLUMN ext_cea TEXT")
    if "ext_csp" not in vigilantes_columns:
        cursor.execute("ALTER TABLE vigilantes ADD COLUMN ext_csp TEXT")
    if "ext_cnl1" not in vigilantes_columns:
        cursor.execute("ALTER TABLE vigilantes ADD COLUMN ext_cnl1 TEXT")
    if "ext_ces" not in vigilantes_columns:
        cursor.execute("ALTER TABLE vigilantes ADD COLUMN ext_ces TEXT")
    if "data_ultima_reciclagem" not in vigilantes_columns:
        cursor.execute("ALTER TABLE vigilantes ADD COLUMN data_ultima_reciclagem TEXT")
    if "curso_ultima_reciclagem" not in vigilantes_columns:
        cursor.execute("ALTER TABLE vigilantes ADD COLUMN curso_ultima_reciclagem TEXT")
    if "ultima_experiencia_profissional" not in vigilantes_columns:
        cursor.execute("ALTER TABLE vigilantes ADD COLUMN ultima_experiencia_profissional TEXT")
    if "estado" not in vigilantes_columns:
        cursor.execute("ALTER TABLE vigilantes ADD COLUMN estado TEXT")

    vagas_columns = _column_names(cursor, "vagas", postgres)
    if "recrutador_id" not in vagas_columns:
        cursor.execute("ALTER TABLE vagas ADD COLUMN recrutador_id INTEGER")

    cursor.execute("UPDATE recrutadores SET status = 'validado' WHERE LOWER(status) = 'ativo'")

    # Índices essenciais para filtros e listagens em beta.
    index_sql = [
        "CREATE INDEX IF NOT EXISTS idx_vigilantes_cidade ON vigilantes (cidade)",
        "CREATE INDEX IF NOT EXISTS idx_vigilantes_status ON vigilantes (status)",
        "CREATE INDEX IF NOT EXISTS idx_vigilantes_antifraude_status ON vigilantes (antifraude_status)",
        "CREATE INDEX IF NOT EXISTS idx_vigilantes_created_at ON vigilantes (created_at)",
        "CREATE INDEX IF NOT EXISTS idx_recrutadores_nome_empresa ON recrutadores (nome_empresa)",
        "CREATE INDEX IF NOT EXISTS idx_recrutadores_status ON recrutadores (status)",
        "CREATE INDEX IF NOT EXISTS idx_recrutadores_antifraude_status ON recrutadores (antifraude_status)",
        "CREATE INDEX IF NOT EXISTS idx_vagas_cidade ON vagas (cidade)",
        "CREATE INDEX IF NOT EXISTS idx_vagas_status ON vagas (status)",
        "CREATE INDEX IF NOT EXISTS idx_vagas_recrutador_id ON vagas (recrutador_id)",
        "CREATE INDEX IF NOT EXISTS idx_candidaturas_status ON candidaturas (status)",
        "CREATE INDEX IF NOT EXISTS idx_candidaturas_vaga_id ON candidaturas (vaga_id)",
        "CREATE INDEX IF NOT EXISTS idx_candidaturas_vigilante_id ON candidaturas (vigilante_id)",
        "CREATE INDEX IF NOT EXISTS idx_candidatos_cidade ON candidatos (cidade)",
        "CREATE INDEX IF NOT EXISTS idx_password_resets_token_hash ON password_resets (token_hash)",
        "CREATE INDEX IF NOT EXISTS idx_lgpd_consents_user ON lgpd_consents (user_type, user_id)",
        "CREATE INDEX IF NOT EXISTS idx_audit_logs_created_at ON audit_logs (created_at)",
    ]
    for sql in index_sql:
        cursor.execute(sql)

    # Normalização mínima para reduzir inconsistências em filtros e exportações.
    cleanup_sql = [
        "UPDATE candidatos SET cidade = TRIM(UPPER(cidade)) WHERE cidade IS NOT NULL",
        "UPDATE candidatos SET estado = TRIM(UPPER(estado)) WHERE estado IS NOT NULL",
        "UPDATE recrutadores SET cidade = TRIM(UPPER(cidade)) WHERE cidade IS NOT NULL",
        "UPDATE recrutadores SET estado = TRIM(UPPER(estado)) WHERE estado IS NOT NULL",
        "UPDATE vigilantes SET cidade = TRIM(UPPER(cidade)) WHERE cidade IS NOT NULL",
        "UPDATE vigilantes SET estado = TRIM(UPPER(estado)) WHERE estado IS NOT NULL",
        "UPDATE vagas SET cidade = TRIM(UPPER(cidade)) WHERE cidade IS NOT NULL",
        "UPDATE vagas SET estado = TRIM(UPPER(estado)) WHERE estado IS NOT NULL",
        """
        UPDATE vigilantes
           SET curso = CASE
                WHEN UPPER(COALESCE(possui_cfv, '')) = 'SIM' AND TRIM(COALESCE(instituicao_formacao, '')) <> '' THEN 'CFV - ' || TRIM(instituicao_formacao)
                WHEN UPPER(COALESCE(possui_cfv, '')) = 'SIM' THEN 'CFV'
                WHEN UPPER(COALESCE(possui_cfv, '')) IN ('NAO', 'NÃO') THEN 'NAO POSSUI CFV'
                ELSE curso
           END
         WHERE curso IS NULL
            OR TRIM(curso) = ''
            OR UPPER(TRIM(curso)) IN ('SIM', 'NAO', 'NÃO')
        """,
        """
        UPDATE vigilantes
           SET reciclagem = CASE
                WHEN TRIM(COALESCE(data_ultima_reciclagem, '')) <> '' AND TRIM(COALESCE(curso_ultima_reciclagem, '')) <> ''
                    THEN TRIM(data_ultima_reciclagem) || ' - ' || TRIM(curso_ultima_reciclagem)
                WHEN TRIM(COALESCE(data_ultima_reciclagem, '')) <> ''
                    THEN TRIM(data_ultima_reciclagem)
                ELSE reciclagem
           END
         WHERE reciclagem IS NULL
            OR TRIM(reciclagem) = ''
            OR reciclagem = data_ultima_reciclagem
        """,
    ]
    for sql in cleanup_sql:
        cursor.execute(sql)

    # Sinalização mínima de registros antigos que ainda exigem revisão humana antes da beta aberta.
    quality_review_sql = [
        "UPDATE vigilantes SET antifraude_status = 'suspeito' WHERE LOWER(COALESCE(antifraude_status, 'normal')) = 'normal' AND (estado IS NULL OR TRIM(estado) = '' OR cpf LIKE 'NAO-INFORMADO-%' OR UPPER(COALESCE(cidade, '')) IN ('NAO INFORMADA', 'NÃO INFORMADA', 'TESTE'))",
        "UPDATE recrutadores SET antifraude_status = 'suspeito' WHERE LOWER(COALESCE(antifraude_status, 'normal')) = 'normal' AND ((cidade IS NULL OR TRIM(cidade) = '') OR (estado IS NULL OR TRIM(estado) = ''))",
        "UPDATE candidatos SET antifraude_status = 'suspeito' WHERE LOWER(COALESCE(antifraude_status, 'normal')) = 'normal' AND ((estado IS NULL OR TRIM(estado) = '') OR UPPER(COALESCE(cidade, '')) IN ('NAO INFORMADA', 'NÃO INFORMADA', 'TESTE'))",
    ]
    for sql in quality_review_sql:
        cursor.execute(sql)

    conn.commit()
    conn.close()



def ensure_default_admin(username: str, password: str, display_name: str):
    conn = get_connection()
    cursor = conn.cursor()
    admin = cursor.execute(
        "SELECT id FROM administradores WHERE username = ?",
        (username,),
    ).fetchone()

    if not admin:
        cursor.execute(
            "INSERT INTO administradores (username, password, nome_exibicao) VALUES (?, ?, ?)",
            (username, generate_password_hash(password), display_name),
        )
        conn.commit()

    conn.close()



def ensure_default_mauricio(username: str, password: str, display_name: str):
    conn = get_connection()
    cursor = conn.cursor()
    usuario = cursor.execute(
        "SELECT id FROM mauricio_usuarios WHERE username = ?",
        (username,),
    ).fetchone()

    if not usuario:
        cursor.execute(
            "INSERT INTO mauricio_usuarios (username, password, nome_exibicao) VALUES (?, ?, ?)",
            (username, generate_password_hash(password), display_name),
        )
        conn.commit()

    conn.close()
