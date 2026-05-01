# Checklist de deploy beta - Público

## Obrigatório antes de subir
- Configure `SECRET_KEY` forte e exclusiva.
- Configure `DATABASE_URL` PostgreSQL válida.
- Mantenha `REQUIRE_POSTGRES=1`.
- Mantenha `ALLOW_SQLITE_FALLBACK=0`.
- Mantenha `FLASK_DEBUG=0`.
- Revise `SESSION_COOKIE_SECURE=1` se usar HTTPS.

## Banco de dados
- O app cria tabelas ausentes e índices principais automaticamente.
- O app normaliza cidade/estado para filtros e exportações.
- Para dados antigos, revise registros com cidade/estado faltando antes da beta aberta.

## Segurança mínima
- Não use credenciais padrão.
- Revise o painel Maurício com usuário e senha exclusivos.
- Não publique dumps de banco nem `.env`.
