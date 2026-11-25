# AppDespesas

Aplicação web local para controle pessoal de despesas. A interface e o backend executam no computador; os dados são armazenados no PostgreSQL hospedado no Neon.

## Requisitos

- Python 3.11 ou superior (recomendado)
- PostgreSQL acessível pela internet (Neon)

## Configuração

1. Crie e ative um ambiente virtual.
2. Instale as dependências: `pip install -r requirements.txt`.
3. Copie `.env.example` para `.env` (no Windows PowerShell: `Copy-Item .env.example .env`).
4. No arquivo `.env`, preencha `DATABASE_URL` com a connection string do Neon.

Use a URL no formato SQLAlchemy com psycopg 3:

```text
postgresql+psycopg://USUARIO:SENHA@HOST/BANCO?sslmode=require
```

Se o Neon fornecer `postgresql://...`, também pode colar a URL como veio: a aplicação converte o esquema para `postgresql+psycopg://` automaticamente.

**Não** coloque a URL no código Python, em arquivos versionados ou em mensagens públicas. O arquivo `.env` está ignorado pelo Git.

## Executar

```powershell
uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
```

Abra <http://127.0.0.1:8000>. A documentação da API fica em <http://127.0.0.1:8000/docs>.

## Verificações

- `GET /health`: verifica se a aplicação está respondendo.
- `GET /health/db`: executa `SELECT 1` no PostgreSQL e verifica a conexão.

## Migrations

Depois de configurar `DATABASE_URL`:

```powershell
alembic revision --autogenerate -m "initial schema"
alembic upgrade head
```

O primeiro comando só deverá ser executado depois que os primeiros modelos SQLAlchemy forem criados em `app/models/`.

## Segurança e backups

- Nunca faça commit do `.env`.
- Restrinja a conexão do banco e mantenha TLS habilitado (`sslmode=require`).
- Configure backups independentes do provedor antes de inserir dados financeiros importantes.
