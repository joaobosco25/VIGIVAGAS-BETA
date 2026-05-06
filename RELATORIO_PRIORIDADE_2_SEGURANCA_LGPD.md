# Relatório - Prioridade 2: Segurança e LGPD grave

## Arquivos novos
- `vigivagas_publico/utils/privacy.py`
- `vigivagas_mauricio/utils/privacy.py`
- `POLITICA_TECNICA_RETENCAO_LGPD.md`
- `sql/2026_05_06_prioridade_2_seguranca_lgpd.sql`

## Segurança e LGPD aplicados
1. Mascaramento de e-mail, telefone, CNPJ e IP em telas administrativas.
2. Remoção/mascaramento de dados pessoais nas exportações XLSX administrativas.
3. CPF permanece fora das exportações de candidaturas por vaga.
4. Endereço e CEP de vigilantes foram removidos da exportação administrativa.
5. Logs de exportação XLSX foram detalhados com indicação do mascaramento aplicado.
6. Acesso ao dashboard administrativo passa a gerar log de auditoria.
7. Exportação de “meus dados” por vigilante/recrutador passa a gerar log.
8. Ações administrativas sensíveis agora exigem senha do Maurício novamente.
9. Alteração de status de recrutador exige senha do Maurício.
10. Alteração de antifraude de recrutador exige senha do Maurício.
11. Alteração de antifraude de vigilante exige senha do Maurício.
12. Fluxo LGPD agora separa: desativar, anonimizar e solicitar exclusão definitiva.
13. Fluxo LGPD agora exige senha atual do usuário.
14. Fluxo LGPD agora exige confirmação textual forte: DESATIVAR, ANONIMIZAR ou EXCLUIR.
15. Exclusão definitiva não apaga diretamente: vira solicitação pendente de revisão.
16. Anonimização remove IP e user-agent do cadastro do titular.
17. Rate limit deixou de depender apenas de memória e passou a suportar tabela no banco.
18. Criada tabela `rate_limit_events` para persistência de rate limit.
19. Código de validação de e-mail do recrutador passou de 5 para 8 dígitos.
20. Código de validação de e-mail agora é salvo em hash SHA-256 no banco.
21. Expiração do código de validação caiu de 15 para 10 minutos.
22. CSP removeu `unsafe-inline` de script e style.
23. Scripts inline relevantes foram movidos para arquivos `.js` externos.
24. Foram adicionados cabeçalhos `Cross-Origin-Opener-Policy` e `Cross-Origin-Resource-Policy`.
25. Criada política técnica de retenção/expurgo de IP e user-agent.

## Arquivos de deploy removidos novamente
- `.git`
- `backup_vigivagas.sql`
- `__pycache__`
- arquivos `.pyc`

## Observação importante
Esta etapa cria uma tabela nova para rate limit persistente. No Render/PostgreSQL, execute o SQL:

`sql/2026_05_06_prioridade_2_seguranca_lgpd.sql`

Ou habilite a criação automática se o projeto estiver configurado para rodar `RUN_INIT_DB=1`, embora o recomendado seja executar a migration SQL explicitamente no banco.

## Validação feita
- `python3 -m compileall -q vigivagas_mauricio vigivagas_publico`
- Remoção posterior de `__pycache__` e `.pyc`
- Busca por `unsafe-inline`, `<script>` inline e `onsubmit=` sem ocorrências restantes nos templates/utils principais.
