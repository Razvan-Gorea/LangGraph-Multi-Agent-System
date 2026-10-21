# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Overview

DocGenie: a multi-agent RAG system. External datastores (REST APIs, PostgreSQL) are ingested into Pinecone by an **Integration Agent**; users query them through a chatbot handled by a **Supervisor Agent**, scoped by per-user permissions. All code lives in `src/` (backend: FastAPI + LangGraph + Mistral; frontend: Next.js in `src/application/front_end/docgenie`). `docs/` and `res/` are PDFs/diagrams only.

## Commands

All Python commands run from `src/` (Python 3.10; deps in `src/requirements.txt`; secrets in `src/.env`, see `src/.env_example`).

```bash
python main.py                          # backend on :8888 AND spawns `npm run dev` (frontend :3000)
docker compose up zookeeper kafka kafka-connect postgres   # infra needed for the PostgreSQL connector
curl http://localhost:8888/seed/all     # seed SQLite with default users/permissions/connectors

python -m pytest tests/unit             # unit tests (Pinecone/Mistral mocked)
python -m pytest tests/unit/api/test_chat_router.py::test_name   # single test
coverage run -m pytest tests/unit && coverage report -m
python -m pytest tests/e2e              # needs live Pinecone + Mistral credentials
basedpyright --pythonversion 3.10       # type check; uses .basedpyright/baseline.json (CI rewrites the baseline)

# frontend (cd application/front_end/docgenie)
npm ci --legacy-peer-deps               # --legacy-peer-deps is required
npx jest ./tests --ci --coverage
```

Full stack via Docker: `docker build -t docgenie-app:latest .` in `src/`, then `docker compose up`.

## Architecture

**Wiring (`src/config.py`)** builds module-level singletons at import time: `env`, `dbutils` (Pinecone wrapper, `multilingual-e5-large`), `sqlclient` (SQLite via SQLModel; creates tables on import), `connector_manager` (`ConnectorBuilder`), `supervisor_agent`, `integration_agent`. `main.py` imports these, so importing `main` (as `tests/conftest.py` does) has side effects; tests override via FastAPI dependencies in `application/api/dependencies.py` (`get_sql_client`, `get_dbutils`, `get_supervisor_agent`).

**Two LangGraph flows, both on `mistral-large-latest`:**
- *Query* (`agents/supervisor_agent`): `START → supervisor → context → supervisor → gen → END`. The supervisor routes with structured output; `context` calls a Pinecone tool restricted to the namespaces the user has permission for; `gen` writes the plain-text answer citing namespaces.
- *Ingestion* (`agents/integration_agent`): `query_node → formatter_node → upserter_node`. The formatter uses structured output (`PineconeSchemaHolder`, `pinecone_schema.py`) and checks existing IDs to avoid overwrites. Tools are in `agents/tools/`.

**Permissions == Pinecone namespaces.** A `Permission` row is a namespace; a connector's data is upserted into the namespace named after it. Access control is enforced only by restricting namespaces in the query tool.

**Connectors (`application/connectors/`)**: `ConnectorBase` subclasses (`rest_connector.py`, `postgres_connector.py`) are registered by type string in `ConnectorBuilder.connector_types` and loaded from SQLite rows at FastAPI lifespan startup (`startup_all_connectors`, which receives the integration agent). Three triggers feed the Integration Agent:
1. connector startup,
2. `POST /receive_webhook/{connector_name}` (REST connectors; handler is in `main.py`),
3. Postgres CDC: the connector registers a Debezium connector with Kafka Connect and a background thread consumes Kafka topics, re-running the agent on each change event.

REST connectors optionally load an OpenAPI spec from `seeds/connectors/spec_<name>.json` to give the agent schema context. Seed data is in `application/seeds/`.

## Gotchas

- `DEEPSEEK_API_KEY` is the **Mistral** API key (historical name).
- `src/external/` holds demo REST/Postgres services used by the seeded connectors; they are not part of the app.
- `main.py` CORS `origins` list is missing a comma after `http://127.0.0.1:3000`, so that entry is concatenated with the next string.
