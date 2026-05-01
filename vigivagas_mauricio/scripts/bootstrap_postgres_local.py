import os
import sys
from pathlib import Path

from dotenv import load_dotenv

PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

load_dotenv(PROJECT_ROOT / '.env')

try:
    import psycopg
    from psycopg import sql
except Exception as exc:
    raise RuntimeError('Instale as dependências com: pip install -r requirements.txt') from exc


def normalize_url(url: str) -> str:
    url = (url or '').strip()
    if url.startswith('postgres://'):
        return 'postgresql://' + url[len('postgres://'):]
    return url


def main():
    database_url = normalize_url(os.getenv('DATABASE_URL', ''))
    if not database_url:
        raise RuntimeError('DATABASE_URL não está definida no .env')

    conninfo = psycopg.conninfo.conninfo_to_dict(database_url)
    target_db = conninfo.get('dbname')
    if not target_db:
        raise RuntimeError('Não foi possível identificar o nome do banco na DATABASE_URL')

    admin_url = normalize_url(os.getenv('POSTGRES_ADMIN_URL', ''))
    if admin_url:
        admin_conninfo = psycopg.conninfo.conninfo_to_dict(admin_url)
    else:
        admin_conninfo = dict(conninfo)
        admin_conninfo['dbname'] = os.getenv('POSTGRES_ADMIN_DB', 'postgres')

    with psycopg.connect(**admin_conninfo, autocommit=True) as conn:
        with conn.cursor() as cur:
            exists = cur.execute('SELECT 1 FROM pg_database WHERE datname = %s', (target_db,)).fetchone()
            if exists:
                print(f'Banco {target_db} já existe. Nada para criar.')
                return
            cur.execute(sql.SQL('CREATE DATABASE {}').format(sql.Identifier(target_db)))
            print(f'Banco {target_db} criado com sucesso.')


if __name__ == '__main__':
    main()
