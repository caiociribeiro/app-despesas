# AppDespesas

Aplicação web local para controle pessoal de despesas. O backend e a interface executam no computador; os dados são armazenados em PostgreSQL hospedado no Neon. O sistema exige conexão com a internet e não mantém banco financeiro local.

## Stack

- Python 3.11+
- FastAPI + Uvicorn
- HTML, CSS, JavaScript e Jinja2
- SQLAlchemy 2 + psycopg 3
- PostgreSQL (Neon)
- Alembic para migrations

## Configuração no Windows (PowerShell)

```powershell
py -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
Copy-Item .env.example .env
```

Preencha `DATABASE_URL` no `.env` com a connection string do Neon. Exemplo de formato:

```text
postgresql+psycopg://USUARIO:SENHA@HOST/appdespesas?sslmode=require
```

Não compartilhe nem versione o `.env`.

## Criar/atualizar o banco

Depois de configurar a conexão:

```powershell
alembic upgrade head
```

A migration inicial cria categorias, subcategorias, formas de pagamento e despesas. A migration seguinte adiciona estabelecimentos e torna seu vínculo obrigatório nas despesas. Também insere as formas de pagamento iniciais: PIX, Boleto, Cartão de crédito, Cartão de débito e Dinheiro / Outro.

## Executar

```powershell
uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
```

Acesse <http://127.0.0.1:8000>. O gerenciamento visual de categorias fica em <http://127.0.0.1:8000/categories>. A documentação da API fica em <http://127.0.0.1:8000/docs>.

## Endpoints disponíveis

- `GET /health` — disponibilidade da aplicação.
- `GET /health/db` — testa conexão com PostgreSQL.
- `GET /api/categories` — lista categorias e subcategorias.\n- Interface `/categories` — cria e edita categorias, cores e subcategorias.
- `POST /api/categories` — cria categoria e sua primeira subcategoria na mesma operação.
- `PATCH /api/categories/{id}` — altera nome ou cor da categoria.
- `POST /api/categories/{id}/subcategories` — adiciona subcategoria.
- `DELETE /api/categories/subcategories/{id}` — remove subcategoria, desde que não seja a última nem tenha despesas vinculadas.
- `GET/POST /api/payment-methods` — consulta e cadastra formas de pagamento.
- `GET/POST /api/establishments` — consulta e cadastra estabelecimentos.\n- `GET/POST /api/expenses` — consulta e cadastra despesas (com estabelecimento obrigatório).
- `PATCH/DELETE /api/expenses/{id}` — altera ou remove despesa.
- `GET /api/dashboard/monthly` — total do mês e últimas despesas.

Valores monetários são armazenados em centavos inteiros. A despesa referencia uma subcategoria e um estabelecimento obrigatório; a categoria é obtida pelo relacionamento da subcategoria, evitando inconsistências entre categoria e subcategoria.

## Testes

```powershell
pytest
```

## Segurança e backup

- O servidor local deve permanecer vinculado a `127.0.0.1`.
- Nunca faça commit do `.env`.
- A conexão com o Neon deve usar TLS (`sslmode=require`).
- Configure backups independentes do provedor antes de inserir dados financeiros importantes.

## Etiquetas nas despesas

Cada despesa possui uma categoria e uma subcategoria, e pode ter até 10 etiquetas complementares. As etiquetas são reutilizáveis e independentes das categorias (por exemplo, `Fast food` como subcategoria e `Delivery` como etiqueta).

Para aplicar a alteração no banco existente, execute:

```powershell
alembic upgrade head
```

A API disponibiliza `GET /api/tags` e `POST /api/tags`. Ao criar ou editar uma despesa, envie `tag_names` como uma lista de nomes; etiquetas inexistentes serão criadas automaticamente e nomes repetidos serão normalizados sem diferenciar maiúsculas/minúsculas.
