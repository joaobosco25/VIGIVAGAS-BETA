# Relatório de Ajustes - Prioridade 1

Data: 2026-05-06
Pacote base: VIGIVAGAS DEPLOY BETA (3).zip
Pacote gerado: VIGIVAGAS_DEPLOY_BETA_PRIORIDADE_1_CORRIGIDO.zip

## O que foi corrigido

1. Remoção de artefatos proibidos no pacote de deploy
   - Removida a pasta `.git` inteira.
   - Removido o arquivo `backup_vigivagas.sql`.
   - Removidas pastas `__pycache__`.
   - Removidos arquivos `.pyc`.

2. Segurança de ambiente
   - O sistema agora bloqueia inicialização em beta/produção se `SESSION_COOKIE_SECURE` não estiver definido como `1`.
   - A validação de `FLASK_DEBUG=0`, `SECRET_KEY` forte e `DATABASE_URL` PostgreSQL foi mantida.

3. Fallback de CNPJ
   - O fallback local de validação de CNPJ agora fica desativado por padrão em beta/produção.
   - Em produção, `CNPJ_ALLOW_FALLBACK_ON_API_ERROR` deve permanecer `0`.
   - O fallback só deve ser usado em ambiente local/teste.

4. Confiança em X-Forwarded-For
   - O sistema deixou de confiar em `X-Forwarded-For` por padrão.
   - O header só será usado se `TRUST_PROXY_HEADERS=1` for configurado conscientemente.
   - Isso reduz risco de IP falsificado em logs, antifraude e rate limit.

5. Exportações XLSX do painel Maurício
   - Adicionado log de auditoria para exportações XLSX.
   - Removido IP de cadastro das exportações de recrutadores e vigilantes.
   - Removido CPF da exportação de candidaturas por vaga.
   - O log informa qual relatório foi exportado e quantas linhas foram geradas.

6. Arquivos de exemplo de ambiente
   - `.env.render.example` recebeu `CNPJ_ALLOW_FALLBACK_ON_API_ERROR=0`.
   - `.env.render.example` recebeu `TRUST_PROXY_HEADERS=0`.

## Validação executada

- Foi executado `python -m compileall` nos projetos `vigivagas_publico` e `vigivagas_mauricio`.
- A compilação não retornou erro de sintaxe.
- Após a validação, os novos `__pycache__` gerados pelo teste foram removidos novamente do pacote final.

## Observação importante

Este pacote corrige a Prioridade 1 de forma inicial. Ainda restam itens das próximas prioridades, principalmente UX dos formulários, LGPD avançada, rate limit persistente, CSP sem `unsafe-inline`, migrações formais e testes automatizados.
