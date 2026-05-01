# Deploy no Render — Vigivagas

Build Command:

```bash
pip install -r requirements.txt
```

Start Command:

```bash
gunicorn -c gunicorn.conf.py wsgi:application
```

Configure as variáveis do arquivo `.env.render.example` em **Environment Variables** no Render.

Crie dois Web Services separados: um para o público e outro para o painel Maurício. Os dois devem apontar para a mesma `DATABASE_URL` do PostgreSQL.

Não suba `.env`, `venv`, `.venv`, backups SQL nem `database/outbox` para GitHub/Render.
