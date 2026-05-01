# VigiVagas - PostgreSQL e deploy

## 1. Objetivo
Este projeto agora aceita dois modos:
- **SQLite** para desenvolvimento local rápido
- **PostgreSQL** para produção e deploy

A prioridade de conexão é:
1. Se `DATABASE_URL` estiver preenchida, a aplicação usa **PostgreSQL**
2. Se `DATABASE_URL` estiver vazia, a aplicação usa **SQLite** em `DATABASE_PATH`

## 2. Dependências
Instale exatamente assim:

```bash
pip install -r requirements.txt
```

## 3. Arquivo `.env`
Crie um arquivo `.env` na raiz do projeto com este conteúdo:

```env
SECRET_KEY="troque-esta-chave-por-uma-chave-forte"
DATABASE_PATH="database/database.db"
DATABASE_URL="postgresql://USUARIO:SENHA@HOST:5432/NOME_DO_BANCO"
DEFAULT_ADMIN_USERNAME="admin"
DEFAULT_ADMIN_PASSWORD="123456"
DEFAULT_ADMIN_DISPLAY_NAME="Administrador"
MAURICIO_USERNAME="mauricio"
MAURICIO_PASSWORD="123456"
MAURICIO_DISPLAY_NAME="Maurício"
ADMIN_HOST="admin.vigivagas.com.br"
SESSION_COOKIE_SECURE="0"
FLASK_DEBUG="1"
FLASK_HOST="127.0.0.1"
PORT="5000"
```

## 4. Teste local com PostgreSQL
Depois de preencher o `.env`, rode exatamente:

```bash
python app.py
```

## 5. Migrar dados do SQLite para PostgreSQL
Mantenha o `database/database.db` original no projeto e rode:

```bash
python scripts/migrate_sqlite_to_postgres.py
```

## 6. Arquivos de deploy incluídos
- `wsgi.py`
- `passenger_wsgi.py`
- `gunicorn.conf.py`
- `start_gunicorn.sh`

## 7. Observação para Locaweb
Na Locaweb, confirme se o ambiente permite rodar aplicação Python via WSGI/Passenger ou Gunicorn. O projeto já foi preparado para esses cenários, mas o apontamento final depende da forma como o seu plano expõe a publicação.
