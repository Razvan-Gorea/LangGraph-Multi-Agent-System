# DocGenie

A multi-agent Retrieval Augmented Generation (RAG) system that centralises fragmented external datastores into a single queryable vector database. Users interact with their data through a conversational chatbot interface, with access control enforced at the namespace level.

**DCU CSC1097 — Year 4 Project**
Authors: Razvan Gorea & Shane Power | Supervisor: Tomas Ward

---

## Table of Contents

- [Overview](#overview)
- [Architecture](#architecture)
- [Tech Stack](#tech-stack)
- [Project Structure](#project-structure)
- [Getting Started](#getting-started)
  - [Prerequisites](#prerequisites)
  - [Environment Variables](#environment-variables)
  - [Running with Docker Compose](#running-with-docker-compose)
  - [Running Locally (Development)](#running-locally-development)
- [Connectors](#connectors)
  - [REST Connector](#rest-connector)
  - [PostgreSQL Connector](#postgresql-connector)
  - [Adding a New Connector](#adding-a-new-connector)
- [Agents](#agents)
  - [Supervisor Agent](#supervisor-agent)
  - [Integration Agent](#integration-agent)
- [API Reference](#api-reference)
- [Seeding the Database](#seeding-the-database)
- [Testing](#testing)
- [CI/CD](#cicd)
- [Documentation](#documentation)

---

## Overview

DocGenie solves the problem of fragmented organisational datastores. Rather than querying each system independently, DocGenie:

1. **Ingests** data from external sources (REST APIs, PostgreSQL databases) via a pluggable connector system.
2. **Vectorises** that data and stores it in [Pinecone](https://www.pinecone.io/) using the `multilingual-e5-large` embedding model.
3. **Answers** natural language questions by retrieving relevant context from the vector store and generating a response using an LLM — all scoped to the user's permissions.

Users with access to certain datastores see answers drawn only from those sources. Technical users can manage connectors and inspect data directly via the REST API.

Real-time data freshness is handled for PostgreSQL sources via Debezium Change Data Capture (CDC) over Kafka: any insert, update, or delete in a monitored Postgres table automatically triggers re-ingestion into Pinecone.

---

## Architecture

```
┌─────────────────────────────────────────────────────────┐
│                      Client (Browser)                   │
│                    Next.js — port 3000                  │
└────────────────────────┬────────────────────────────────┘
                         │ HTTP
┌────────────────────────▼───────────────────────────────┐
│                FastAPI Backend — port 8888             │
│                                                        │
│  ┌──────────────────┐   ┌───────────────────────────┐  │
│  │  Supervisor Agent│   │    Integration Agent      │  │
│  │  (query flow)    │   │    (ingestion flow)       │  │
│  │                  │   │                           │  │
│  │  context_agent   │   │  query → format → upsert  │  │
│  │  gen_agent       │   │                           │  │
│  └────────┬─────────┘   └──────────────┬────────────┘  │
│           │                            │               │
└───────────┼────────────────────────────┼───────────────┘
            │                            │
   ┌────────▼────────┐         ┌─────────▼──────────┐
   │    Pinecone     │         │  External Sources  │
   │  Vector Store   │◄────────│  REST APIs         │
   │  (namespaced)   │         │  PostgreSQL + Kafka│
   └─────────────────┘         └────────────────────┘
            │
   ┌────────▼────────┐
   │  SQLite (local) │
   │  Users, Perms,  │
   │  Conversations  │
   └─────────────────┘
```

**Query flow:** User message → `SupervisorAgent` → `context_agent` retrieves matching vectors from permitted Pinecone namespaces → `gen_agent` formats the facts into a plain-text answer → response returned to the user.

**Ingestion flow:** Connector startup / Kafka CDC event / webhook → `IntegrationAgent` → query connector → format data → upsert vectors to Pinecone namespace.

---

## Tech Stack

| Layer | Technology |
|---|---|
| Frontend | Next.js 18 (React, TypeScript) |
| Backend | Python 3.10, FastAPI, Uvicorn |
| Multi-agent | LangGraph, LangChain |
| LLM | Mistral (`mistral-large-latest`) via `langchain-mistralai` |
| Vector store | Pinecone (`multilingual-e5-large` embeddings) |
| Local DB | SQLite via SQLModel / SQLAlchemy |
| CDC / streaming | Debezium, Apache Kafka, Zookeeper |
| External DB | PostgreSQL |
| Containerisation | Docker, Docker Compose |
| Static analysis | basedpyright |
| Testing | pytest, pytest-cov, Jest |
| CI | GitLab CI |

---

## Project Structure

```
.
├── docs/                        # Project documentation
│   ├── proposal/                # Original project proposal
│   ├── functional-spec/         # Functional specification (PDF)
│   ├── documentation/           # User manual & technical manual (PDFs)
│   └── video-walk-through/      # Video walkthrough (.mkv)
├── res/
│   └── diagrams/                # Architecture & class diagrams (PlantUML / PNG)
└── src/
    ├── docker-compose.yml       # Full stack orchestration
    ├── Dockerfile               # Multi-stage build (Next.js + Python)
    ├── requirements.txt
    ├── main.py                  # FastAPI app entrypoint
    ├── config.py                # Dependency wiring (env, db, agents)
    ├── external/
    │   ├── postgres_example/    # Sample PostgreSQL service + seed data
    │   └── rest_example/        # Sample REST API (FastAPI)
    ├── tests/
    │   ├── unit/                # Unit tests (pytest)
    │   └── e2e/                 # End-to-end tests
    └── application/
        ├── environment.py       # Env var loader
        ├── dbutils.py           # Pinecone client wrapper
        ├── agents/
        │   ├── supervisor_agent/  # RAG query agent
        │   ├── integration_agent/ # Data ingestion agent
        │   └── tools/             # LangChain tools (query, upsert, list)
        ├── api/
        │   ├── models/            # SQLModel schemas (User, Connector, Chat…)
        │   ├── routes/            # FastAPI routers
        │   └── sqlclient.py       # SQLite CRUD helper
        ├── connectors/
        │   ├── connector_base.py
        │   ├── connector_builder.py
        │   ├── rest_connector.py
        │   └── postgres_connector.py
        ├── seeds/
        │   ├── database/          # JSON seed data (users, permissions…)
        │   └── connectors/        # Connector config + OpenAPI specs
        └── front_end/
            └── docgenie/          # Next.js application
```

---

## Getting Started

### Prerequisites

- [Docker](https://docs.docker.com/get-docker/) and Docker Compose
- A [Pinecone](https://www.pinecone.io/) account and API key
- A [Mistral AI](https://mistral.ai/) API key

### Environment Variables

Create a `.env` file inside `src/`:

```env
PINECONE_API_KEY=your_pinecone_api_key
DEEPSEEK_API_KEY=your_mistral_api_key
SQL_LITE_DB_STRING=sqlite:///./test.db
LOCAL_HOST_BACKEND_IP=0.0.0.0
LOCAL_HOST_FRONTEND_IP=0.0.0.0
DEBUG_MODE=False
```

> `DEEPSEEK_API_KEY` is used as the Mistral API key — the variable name is a historical artefact.

### Running with Docker Compose

The compose file starts Zookeeper, Kafka, Kafka Connect (Debezium), PostgreSQL, the sample REST API, and the DocGenie app.

```bash
cd src

# Build the DocGenie image
docker build -t docgenie-app:latest .

# Build the sample REST API image (optional, for demo connectors)
cd external/rest_example
docker build -t fast-api-example .
cd ../..

# Start everything
docker compose up
```

| Service | URL |
|---|---|
| DocGenie frontend | http://localhost:3000 |
| DocGenie backend API | http://localhost:8888 |
| Kafka Connect | http://localhost:8083 |
| Sample REST API | http://localhost:8000 |
| PostgreSQL | localhost:5432 |

### Running Locally (Development)

```bash
cd src

# Create and activate a virtual environment
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

pip install -r requirements.txt

# Install frontend dependencies
cd application/front_end/docgenie
npm ci --legacy-peer-deps
cd ../../..

# Start the backend (also spawns the Next.js dev server)
python main.py
```

> The infrastructure services (Postgres, Kafka, Debezium) still need to run via Docker Compose for the PostgreSQL connector to function. You can start just the infrastructure: `docker compose up zookeeper kafka kafka-connect postgres`.

---

## Connectors

Connectors are the plugin layer between external datastores and the DocGenie ingestion pipeline. Each connector is registered in the SQLite database and loaded at startup by `ConnectorBuilder`.

### REST Connector

Connects to any HTTP REST API. On startup it loads an optional OpenAPI spec (stored under `seeds/connectors/spec_<name>.json`) to give the integration agent schema context.

**Config shape (`c_params`):**

```json
{
  "base_url": "http://api.example.com",
  "headers": { "Content-Type": "application/json" },
  "timeout": 30,
  "retries": 3,
  "has_schema": "True",
  "api_key": "optional"
}
```

REST connectors can also receive **webhooks** at `POST /receive_webhook/{connector_name}` to trigger re-ingestion when upstream data changes.

### PostgreSQL Connector

Connects to a PostgreSQL database and registers a Debezium CDC connector with Kafka Connect. A background thread subscribes to all Kafka topics matching the configured prefix and re-runs the integration agent whenever a change event arrives.

**Config shape (`c_params` / `e_params`):**

```json
{
  "c_params": {
    "db_name": "mydatabase",
    "user": "myuser",
    "password": "mypassword",
    "host": "postgres",
    "port": 5432
  },
  "e_params": {
    "class": "io.debezium.connector.postgresql.PostgresConnector",
    "topic": "business_management",
    "include_list": "public.*",
    "plugin.name": "pgoutput",
    "publication.name": "dbz_publication"
  }
}
```

### Adding a New Connector

1. Subclass `ConnectorBase` in `src/application/connectors/`.
2. Implement `startup(integration_agent)` and optionally `shutdown()`.
3. Register the type string in `ConnectorBuilder.connector_types`.
4. Add a connector record (via API or seed JSON) with the correct `type_c` and params.

---

## Agents

Both agents are built with [LangGraph](https://langchain-ai.github.io/langgraph/) and use `mistral-large-latest` as the underlying LLM.

### Supervisor Agent

Handles user queries. The graph has three nodes:

```
START → supervisor → context → supervisor → gen → END
```

- **supervisor**: Decides which worker to call next using structured output (`Router`).
- **context**: Uses a Pinecone tool to retrieve the top-k matching vectors from the namespaces the user has permission to access. Returns formatted facts.
- **gen**: Reads the facts from `context` and formats them into a plain-text answer, citing the namespaces used.

Permissions map directly to Pinecone namespaces: a user only sees data from connectors they have been granted access to.

### Integration Agent

Handles data ingestion. The pipeline is linear:

```
START → query_node → formatter_node → upserter_node → END
```

- **query_node**: Calls the appropriate connector tool (REST GET or PostgreSQL query) to extract raw data.
- **formatter_node**: Converts raw data into the Pinecone schema (`id`, `text`, metadata) using structured output (`PineconeSchemaHolder`). Checks existing IDs to avoid overwrites.
- **upserter_node**: Batches and upserts the formatted vectors to the correct Pinecone namespace.

---

## API Reference

The full OpenAPI docs are available at `http://localhost:8888/docs` when the server is running.

| Method | Path | Description |
|---|---|---|
| `POST` | `/receive_webhook/{connector_name}` | Trigger ingestion from a webhook payload |
| `GET` | `/user/{user_id}` | Get user with permissions |
| `POST` | `/user/login` | Authenticate a user |
| `POST` | `/user/create` | Register a new user |
| `PUT` | `/user/{user_id}` | Update a user |
| `DELETE` | `/user/{user_id}` | Delete a user |
| `POST` | `/permission/create` | Create a permission (namespace) |
| `GET/PUT/DELETE` | `/permission/{permission_id}` | Manage a permission |
| `POST` | `/conversation/create` | Start a new conversation |
| `POST` | `/conversation/all` | List all conversations for a user |
| `GET` | `/conversation/{convo_id}` | Get a conversation |
| `POST` | `/conversation/{convo_id}/chat/create` | Add a user message |
| `POST` | `/conversation/{convo_id}/chat/response` | Get an AI response |
| `GET` | `/conversation/{convo_id}/chat/all` | Get all messages in a conversation |
| `GET` | `/connector/all` | List all connectors |
| `POST` | `/connector/new` | Register and start a new connector |
| `GET` | `/connector/{name}/status` | Check if a connector is active |
| `GET` | `/seed/all` | Seed the database with default data |

---

## Seeding the Database

Default seed data is stored under `src/application/seeds/database/` and `src/application/seeds/connectors/`. Once the app is running, call the seed endpoint to populate SQLite:

```bash
curl http://localhost:8888/seed/all
```

This loads the default permissions, users, conversations, and the three example connectors (`SimplyTransport`, `DayofTheWeek`, `postgres_database`).

---

## Testing

```bash
cd src

# Unit tests with coverage
coverage run -m pytest tests/unit
coverage report -m

# E2E tests (requires live Pinecone + Mistral credentials)
python -m pytest tests/e2e

# Static type checking
basedpyright --pythonversion 3.10

# Frontend tests
cd application/front_end/docgenie
npx jest ./tests --ci --coverage
```

---

## CI/CD

The GitLab CI pipeline (`.gitlab-ci.yml`) runs on every push across three stages:

| Stage | Job | What it does |
|---|---|---|
| build | `build-frontend` | `npm ci` + `npm run build` for the Next.js app |
| test | `python-unit-tests` | pytest + coverage report |
| test | `python-e2e-tests` | End-to-end pytest suite |
| test | `javascript-unit-tests` | Jest with coverage |
| test | `formatting-tests` | basedpyright static analysis + GitLab Code Quality report |

E2E tests are permitted to fail on PRs (they can be flaky against live external services). One approval is required to merge into `main`.

---

## Documentation

Full documentation is available under `docs/`:

| Document | Path |
|---|---|
| Project Proposal | `docs/proposal/proposal.md` |
| Functional Specification | `docs/functional-spec/Functional Specification.pdf` |
| Technical Manual | `docs/documentation/Technical Manual.pdf` |
| User Manual | `docs/documentation/User Manual.pdf` |
| Video Walkthrough | `docs/video-walk-through/docgenie_walkthrough.mkv` |
| Architecture Diagrams | `res/diagrams/` |
