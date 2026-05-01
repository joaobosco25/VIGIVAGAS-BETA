import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

import os
import sqlite3

from dotenv import load_dotenv

load_dotenv(PROJECT_ROOT / ".env")

from utils.db import DEFAULT_DATABASE, get_database_path, get_connection, init_db, using_postgres

TABLES = [
    "administradores",
    "mauricio_usuarios",
    "recrutadores",
    "vigilantes",
    "vagas",
    "candidatos",
    "candidaturas",
]


def main():
    if not using_postgres():
        raise RuntimeError("Defina DATABASE_URL com uma conexão PostgreSQL válida no arquivo .env antes de migrar.")

    sqlite_path = get_database_path()
    if not sqlite_path.exists():
        raise FileNotFoundError(f"Banco SQLite não encontrado em: {sqlite_path}")

    sqlite_conn = sqlite3.connect(sqlite_path)
    sqlite_conn.row_factory = sqlite3.Row

    init_db()
    pg_conn = get_connection()

    try:
        pg_conn.execute("DELETE FROM candidaturas")
        pg_conn.execute("DELETE FROM vagas")
        pg_conn.execute("DELETE FROM vigilantes")
        pg_conn.execute("DELETE FROM candidatos")
        pg_conn.execute("DELETE FROM recrutadores")
        pg_conn.execute("DELETE FROM mauricio_usuarios")
        pg_conn.execute("DELETE FROM administradores")
        pg_conn.commit()

        for table in TABLES:
            rows = sqlite_conn.execute(f"SELECT * FROM {table} ORDER BY id").fetchall()
            if not rows:
                continue

            columns = rows[0].keys()
            columns_csv = ", ".join(columns)
            placeholders = ", ".join(["?" for _ in columns])
            sql = f"INSERT INTO {table} ({columns_csv}) VALUES ({placeholders})"

            for row in rows:
                values = [row[column] for column in columns]
                pg_conn.execute(sql, values)

        for table in TABLES:
            pg_conn.execute(
                "SELECT setval(pg_get_serial_sequence(%s, 'id'), COALESCE((SELECT MAX(id) FROM " + table + "), 1), true)",
                (table,),
            )

        pg_conn.commit()
        print("Migração concluída com sucesso.")
        for table in TABLES:
            total = pg_conn.execute(f"SELECT COUNT(*) AS total FROM {table}").fetchone()["total"]
            print(f"{table}: {total} registro(s)")
    except Exception:
        pg_conn.rollback()
        raise
    finally:
        sqlite_conn.close()
        pg_conn.close()


if __name__ == "__main__":
    main()
