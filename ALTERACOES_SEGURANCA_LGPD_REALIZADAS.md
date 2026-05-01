# Alterações aplicadas neste ZIP

- CSRF em formulários POST.
- Rate limit simples em endpoints sensíveis.
- Headers de segurança: CSP, X-Frame-Options, HSTS quando HTTPS, Referrer-Policy, Permissions-Policy.
- Cookies/sessão reforçados e tempo de sessão configurável.
- Dependências travadas no requirements.txt.
- Tabelas novas: password_resets, lgpd_consents, audit_logs.
- Política de Privacidade e Termos de Uso.
- Checkbox obrigatório de LGPD nos cadastros públicos, vigilante e recrutador.
- Registro de consentimento no banco com IP, user agent e versão da política.
- Exportação de dados do vigilante e recrutador em JSON.
- Exclusão/anonimização de conta de vigilante e recrutador.
- Auditoria básica para ações críticas do painel Maurício.
- Scripts de backup PostgreSQL para Windows e Linux.

Observação: após subir, rode a aplicação uma vez para o init_db criar as novas tabelas.

- Recuperação de senha funcional para vigilante e recrutador: token forte, hash no banco, expiração de 1 hora, uso único e envio via SMTP.
- Correção de configuração de remetente: aceita SMTP_FROM, SMTP_SENDER ou MAIL_FROM.
