# VigiVagas Público

Este pacote contém apenas o site público do VigiVagas, além das áreas de recrutador, vigilante e admin.

## O que foi removido
- blueprint do Maurício
- link público direto para o painel Maurício

## Porta local sugerida
- 5000

## Banco
- compartilha o mesmo PostgreSQL do painel Maurício

## Como rodar
1. Ajuste a DATABASE_URL no `.env`
2. Ative a `.venv`
3. `pip install -r requirements.txt`
4. `python app.py`

## Observação
Use um subdomínio separado em produção para o painel Maurício.
