import sys
from pathlib import Path

from dotenv import load_dotenv

PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

load_dotenv(PROJECT_ROOT / '.env')

from utils.db import get_connection, using_postgres

TABLES = [
    'administradores',
    'mauricio_usuarios',
    'recrutadores',
    'vigilantes',
    'vagas',
    'candidatos',
    'candidaturas',
]


def main():
    if not using_postgres():
        raise RuntimeError('A aplicação ainda não está apontando para PostgreSQL. Revise DATABASE_URL no .env.')

    conn = get_connection()
    try:
        print('Conexão PostgreSQL: OK')
        for table in TABLES:
            total = conn.execute(f'SELECT COUNT(*) AS total FROM {table}').fetchone()['total']
            print(f'{table}: {total}')

        conn.execute(
            '''
            SELECT v.id, v.titulo, v.empresa, v.cidade, v.estado, v.status, v.created_at,
                   r.nome_empresa AS recrutador_empresa,
                   COUNT(c.id) AS total_candidaturas
            FROM vagas v
            LEFT JOIN recrutadores r ON r.id = v.recrutador_id
            LEFT JOIN candidaturas c ON c.vaga_id = v.id
            GROUP BY v.id, v.titulo, v.empresa, v.cidade, v.estado, v.status, v.created_at, r.nome_empresa
            ORDER BY v.id DESC
            LIMIT 5
            '''
        ).fetchall()
        print('Consulta do painel Maurício: OK')

        conn.execute(
            '''
            SELECT v.id, v.titulo, v.empresa, v.cidade, v.estado, v.status, v.created_at,
                   COUNT(c.id) AS total_candidaturas
            FROM vagas v
            LEFT JOIN candidaturas c ON c.vaga_id = v.id
            WHERE v.recrutador_id IS NOT NULL
            GROUP BY v.id, v.titulo, v.empresa, v.cidade, v.estado, v.status, v.created_at
            ORDER BY v.id DESC
            LIMIT 5
            '''
        ).fetchall()
        print('Consulta do painel Recrutador: OK')
    finally:
        conn.close()


if __name__ == '__main__':
    main()
