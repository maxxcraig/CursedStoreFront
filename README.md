# Cursed Storefronts

CS 514 final project: tracking the business history of San Diego commercial
addresses to find the storefronts where businesses keep failing.

**Stack:** PostgreSQL 16 (Docker) · Python / Flask · Bootstrap · Chart.js

## Setup

### 1. Install prerequisites
- Python 3.11+ (`python3 --version`)
- [Docker Desktop](https://www.docker.com/products/docker-desktop/), which must be open whenever you work on the project

### 2. Clone and configure
```
git clone <repo-url>
cd CursedStoreFront
cp .env.example .env
```
**Set your own `DB_PASSWORD` in `.env` now, BEFORE step 4.** Postgres only reads
the password the first time it starts. If you change it later, you'll get
"password authentication failed" and have to reset (see Troubleshooting).

### 3. Create a virtual environment and install packages
```
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```
Run `source .venv/bin/activate` every time you open a new terminal.

### 4. Start the database
```
docker compose up -d
```

### 5. Create tables and load sample data
Wait a few seconds after step 4, then:
```
docker exec -i cursed_db psql -U cursed -d cursed_storefronts < db/migrations/001_init.sql
docker exec -i cursed_db psql -U cursed -d cursed_storefronts < db/seed.sql
```
Run migrations in number order. When new migration files are added, run each new one.

### 6. Run the app
```
python run.py
```
- App: http://localhost:5001
- Health check: http://localhost:5001/health (should say `"database": "connected"`)

## Project structure
```
app/            Flask app: routes, database helper, templates, static files
db/migrations/  SQL files that build the schema, run in number order
db/seed.sql     Fake starter data
data/scripts/   Scripts that clean and load real city data
data/raw/       Downloaded datasets (not committed)
docs/           ER diagram, screenshots, project documents
```

## Team workflow
1. Pick up an issue assigned to you on GitHub.
2. Create a branch for it: `git checkout -b issue-12-short-name`
3. Commit as you go, with clear messages.
4. Push and open a pull request that says `Closes #12`.
5. Max reviews and merges into `main`.

Never push directly to `main`. Log any AI help in `AI_USAGE.md`.

## Rules for database code
- Always pass user input as parameters: `query("... WHERE street = %s", (value,))`.
  Never build SQL with f-strings, because that allows SQL injection.
- Schema changes go in a **new** numbered migration file. Don't edit old ones
  after they've been merged.

## Troubleshooting
| Problem | Fix |
|---|---|
| `password authentication failed` | Reset the database: `docker compose down -v`, `docker compose up -d`, then rerun step 5 |
| `connection refused` | Docker Desktop isn't open, or run `docker compose up -d` |
| `No module named 'flask'` | Activate the venv: `source .venv/bin/activate` |
| Port 5432 already in use | You have Postgres installed locally. Change the port to `"5433:5432"` in `docker-compose.yml` and `DB_PORT=5433` in `.env` |
| Empty table on home page | Run `seed.sql` (step 5) |

`docker compose down -v` deletes all database data. That's fine for seed data,
but rerun any data-loading scripts afterward.