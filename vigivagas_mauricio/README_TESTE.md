# VigiVagas refatorado para separar público e admin

## O que mudou
- Rotas públicas separadas das administrativas.
- Templates separados em `templates/public` e `templates/admin`.
- Banco movido para `database/database.db`.
- Login admin continua em `/admin/login`.
- Dashboard continua em `/admin/dashboard`.
- Cadastro de vagas continua em `/admin/vagas`.
- Nova exportação CSV em `/admin/exportar-candidatos`.
- `SECRET_KEY` e credenciais padrão saíram do código fixo e foram para variáveis de ambiente.

## Como rodar localmente
1. Abra o terminal na pasta do projeto.
2. Crie e ative um ambiente virtual.
3. Instale as dependências com `pip install -r requirements.txt`.
4. Defina as variáveis de ambiente ou use os padrões atuais.
5. Rode `python app.py`.
6. Acesse `http://127.0.0.1:5000`.

## URLs principais
- Público: `/`
- Formulário candidato: `/candidato`
- Login admin: `/admin/login`
- Dashboard: `/admin/dashboard`
- Vagas admin: `/admin/vagas`
- Exportação CSV: `/admin/exportar-candidatos`
