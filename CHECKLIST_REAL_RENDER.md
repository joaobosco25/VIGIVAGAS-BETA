# VIGIVAGAS — Checklist real antes dos testes no Render

## 1. Subir o código
1. Substitua as pastas `vigivagas_publico/` e `vigivagas_mauricio/` pelas versões deste ZIP.
2. Faça commit e push para o GitHub.
3. No Render, faça deploy dos dois serviços.

## 2. Rodar a migração do banco
Antes de testar recuperação de senha, LGPD e painel, rode no PostgreSQL do Render o arquivo:

```text
schema_render_producao.sql
```

Ele cria/ajusta, sem apagar dados:

- `password_resets`
- `lgpd_consents`
- `lgpd_requests`
- `audit_logs`
- colunas necessárias em `recrutadores`, `vigilantes` e `vagas`
- índices para filtros, relatórios e exportações

## 3. Variáveis obrigatórias no Render
Nos dois serviços:

```env
DATABASE_URL=postgresql://...
SECRET_KEY=chave_forte
FLASK_DEBUG=0
RUN_INIT_DB=0
SESSION_COOKIE_SECURE=1
APP_ENV=production
```

No serviço público, também manter SMTP:

```env
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=...
SMTP_PASSWORD=senha_de_app
SMTP_FROM=...
APP_BASE_URL=https://vigivagas-publico.onrender.com
```

## 4. Testes reais

### Público
- Cadastro de vigilante com aceite LGPD.
- Login de vigilante.
- Download `meus-dados.json`.
- Solicitação de anonimização/exclusão.
- Recuperação de senha de vigilante.
- Cadastro de recrutador com aceite LGPD.
- Validação de e-mail do recrutador.
- Recuperação de senha do recrutador.
- Publicação de vaga.
- Edição de vaga.
- Candidatura.

### Painel Maurício
- Login.
- Filtros de recrutadores.
- Filtros de vigilantes.
- Filtros de vagas.
- Filtros de candidaturas.
- Exportação XLSX das quatro abas.
- Alteração de status de recrutador.
- Alteração antifraude de recrutador e vigilante.
- Conferência de logs administrativos.
- Conferência de solicitações LGPD.

## 5. O que foi ajustado nesta versão
- Schema SQL oficial para Render/produção.
- Correção estrutural da tabela `password_resets` usada pelo código.
- Registro de solicitações LGPD em `lgpd_requests` ao anonimizar conta.
- Painel Maurício exibindo solicitações LGPD e logs administrativos.
- Logs administrativos ao alterar status/antifraude.
- Termos de Uso e Política de Privacidade revisados.
- Mantido `RUN_INIT_DB=0` em produção.

## 6. Próxima etapa
Depois que este checklist passar, trocar SMTP Gmail por e-mail profissional e refazer testes de envio.
