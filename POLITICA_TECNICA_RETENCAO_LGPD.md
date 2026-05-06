# Política técnica de retenção e expurgo LGPD - VigiVagas

## Objetivo
Reduzir exposição de dados pessoais e manter somente dados necessários para operação, segurança, auditoria, prevenção a fraudes, cumprimento legal e defesa de direitos.

## Dados de IP e user-agent
- `ip_cadastro`, `ip_address` e `user_agent` devem ser usados apenas para segurança, auditoria e antifraude.
- Em telas administrativas, IP deve aparecer mascarado.
- Em exportações, IP não deve ser exportado.
- Registros antigos devem ser anonimizados/expurgados periodicamente.

## Retenção recomendada
- Logs de rate limit: expurgo automático de eventos antigos pela própria rotina de rate limit.
- IP/user-agent de cadastro: anonimizar após 180 dias, salvo se houver investigação, fraude, obrigação legal ou disputa ativa.
- Auditoria administrativa: manter pelo prazo necessário para segurança e defesa de direitos, sempre exibindo IP mascarado no painel.
- Solicitações LGPD: preservar registro mínimo da solicitação para comprovar atendimento.

## Exportações
- Toda exportação administrativa deve registrar auditoria.
- Exportações administrativas devem usar mascaramento ou remoção de CPF, e-mail, telefone, endereço e IP sempre que o dado integral não for indispensável.

## Exclusão, anonimização e desativação
- Desativação: suspende acesso, preserva dados.
- Anonimização: remove identificadores diretos e preserva registros mínimos.
- Exclusão definitiva: registrada como solicitação pendente de revisão quando puder afetar obrigações legais, auditoria ou defesa de direitos.
