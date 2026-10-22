# DocGenie

DocGenie is a multi-agent Retrieval Augmented Generation (RAG) system. It pulls data out of separate external datastores (REST APIs and PostgreSQL databases), stores it in one Pinecone vector index, and lets users ask questions about it through a chatbot. Each user only sees answers drawn from the datastores they have been given access to.

Authors: Razvan Gorea and Shane Power.

## Table of Contents

- [How it works](#how-it-works)
- [Architecture](#architecture)
  - [System overview](#system-overview)
  - [Query flow (Supervisor Agent)](#query-flow-supervisor-agent)
  - [Ingestion flow (Integration Agent)](#ingestion-flow-integration-agent)
  - [Permissions and namespaces](#permissions-and-namespaces)
  - [Startup wiring](#startup-wiring)
  - [Data model](#data-model)
  - [Docker topology](#docker-topology)
- [Tech stack](#tech-stack)
- [Getting started](#getting-started)
  - [Prerequisites](#prerequisites)
  - [Environment variables](#environment-variables)
  - [Create the Pinecone index](#create-the-pinecone-index)
  - [Run with Docker Compose](#run-with-docker-compose)
  - [Run locally for development](#run-locally-for-development)
  - [Seed the database](#seed-the-database)
- [Connectors](#connectors)
- [MCP server (optional)](#mcp-server-optional)
- [API reference](#api-reference)
- [Frontend](#frontend)
- [Testing and quality](#testing-and-quality)
- [CI](#ci)
- [Repository file guide](#repository-file-guide)
- [Known limitations](#known-limitations)
- [Further documentation](#further-documentation)

## How it works

There are two LangGraph pipelines, both built on a configurable chat model (Anthropic `claude-sonnet-5-5` by default):

- **Integration Agent** (ingestion): reads data from a connector, rewrites it as short factual sentences, and upserts them into Pinecone.
- **Supervisor Agent** (query): takes a user's question, retrieves matching facts from Pinecone, and writes a plain-text answer that names the namespaces it used.

Connectors are the plug-in layer between an external datastore and the Integration Agent. Two types exist today: `rest` and `postgres`. The Integration Agent can reach them through built-in tools (the default) or through an [MCP server](#mcp-server-optional) that the app hosts when `MCP_SERVER_URL` is set.

## Architecture

### System overview

![High-level architecture](res/diagrams/highlevel_architecture.png)

### Query flow (Supervisor Agent)

Defined in `src/application/agents/supervisor_agent/supervisor_agent.py`.

```
START -> supervisor -> context -> supervisor -> gen -> END
```

1. `POST /conversation/{id}/chat/response` loads the conversation's user and their permissions, then calls `SupervisorAgent.take_input`.
2. **supervisor** decides which worker runs next, using structured output (`Router`). It must run `context` and `gen` at least once each, and counters stop it looping more than three times.
3. **context** is a ReAct agent with one tool (`query_dbutils`) that embeds the question and searches Pinecone. It is told to use only the namespaces in the user's permission list, and returns facts.
4. **gen** turns those facts into a plain-text answer and ends with `Namespace(s) used: ...`.

### Ingestion flow (Integration Agent)

Defined in `src/application/agents/integration_agent/integration_agent.py`.

```
START -> query_node -> formatter_node -> upserter_node -> END
```

- **query_node** calls a connector tool (`query_rest_connector` or `query_postgres_connector`) and returns the raw data plus where it came from. The tools are the built-in ones in `tools/query_connectors.py`, or, when MCP is on, tools of the same names loaded from the MCP server. In MCP mode the graph runs asynchronously (`aquery_node`).
- **formatter_node** converts the data into `PineconeSchemaHolder` rows (`id`, `text`) using structured output. It calls `list_ids` first so it does not reuse ids that already exist in the namespace.
- **upserter_node** embeds the rows with `multilingual-e5-large` and upserts them into the namespace named after the connector.

Three things start this pipeline:

1. **Connector startup.** At FastAPI startup (`lifespan` in `main.py`) every connector's `startup()` runs.
2. **Webhook.** `POST /receive_webhook/{connector_name}` (handler in `main.py`) builds an `IntegrationPrompt` from the body and runs the graph with `ainvoke`. The request returns only after the whole pipeline finishes, which can take tens of seconds.
3. **Postgres change data capture.** `PostgresConnector.startup()` registers a Debezium connector with Kafka Connect and starts a background thread that consumes the resulting Kafka topics. Each insert, update or delete re-runs the graph (`asyncio.run(graph.ainvoke(...))` in that thread).

### Permissions and namespaces

A `Permission` row is a Pinecone namespace. A connector's data is upserted into the namespace named after that connector. Access control is enforced by restricting which namespaces the query tool is told it may use. There is no other access layer between the agent and Pinecone.

### Startup wiring

`src/config.py` builds module-level singletons when it is imported: `env`, `dbutils` (Pinecone wrapper), `sqlclient` (SQLite, creates tables on import), `connector_manager`, `supervisor_agent` and `integration_agent`. `main.py` imports them, so importing `main` has side effects. Tests replace them through the FastAPI dependencies in `application/api/dependencies.py`.

### Data model

| Table | Purpose |
|---|---|
| `User` | username, email, bcrypt password hash, `is_admin` |
| `Permission` | a named permission (equals a Pinecone namespace) |
| `UserPermission` | many-to-many link between users and permissions |
| `Conversation` | a chat thread owned by a user |
| `Chat` | one message links to one conversation (see above) |
| `Connector` | connector name, type (`type_c`), connection params (`c_params`) and event params (`e_params`) as JSON |

### Docker topology

`src/docker-compose.yml` starts six services on one bridge network:

| Service | Image | Role |
|---|---|---|
| `zookeeper` | `quay.io/debezium/zookeeper:3.3` | Kafka coordination |
| `kafka` | `quay.io/debezium/kafka:3.3` | event stream |
| `postgres` | `postgres:17-alpine` | demo external database, logical WAL enabled for Debezium, loaded from `external/postgres_example/dummy_data.sql` |
| `kafka-connect` (container `connect`) | `quay.io/debezium/connect:3.3` | runs the Debezium connector |
| `fast-api` | built from `external/rest_example` | demo REST API |
| `docgenie-app` | built from `src/Dockerfile` | backend and frontend |

## Tech stack

| Layer | Technology |
|---|---|
| Frontend | Next.js 16, React 19, TypeScript, Tailwind CSS v4, shadcn/ui |
| Backend | Python 3.12, FastAPI, Uvicorn |
| Agents | LangGraph, LangChain |
| Datastore tools | Built-in tools, or an optional MCP server (`mcp` `FastMCP`, `langchain-mcp-adapters` client) |
| LLM | Configurable (`LLM_PROVIDER`, `LLM_MODEL`), Anthropic by default |
| Vector store | Pinecone with `multilingual-e5-large` embeddings |
| Application database | SQLite through SQLModel / SQLAlchemy |
| Change data capture | Debezium, Apache Kafka, Zookeeper |
| Containers | Docker, Docker Compose |
| Tests | pytest, pytest-cov, Jest |
| Type checking | basedpyright |
| CI | GitHub Actions |

## Getting started

### Prerequisites

- Docker and Docker Compose
- A Pinecone account and API key
- An API key for your LLM provider
- For local development without Docker: Python 3.12 and Node.js 24

### Environment variables

Copy `src/.env_example` to `src/.env` and fill it in. Docker Compose loads it through `env_file`. The `.env` file is never copied into the image.

| Variable | Meaning |
|---|---|
| `PINECONE_API_KEY` | Pinecone API key |
| `LLM_API_KEY` | API key for the chat model provider |
| `LLM_PROVIDER` | LangChain provider name (default `anthropic`) |
| `LLM_MODEL` | model name (default `claude-sonnet-5-5`) |
| `SQL_LITE_DB_STRING` | SQLAlchemy URL, for example `sqlite:///./database.db` |
| `LOCAL_HOST_BACKEND_IP` | address uvicorn listens on. In Docker this must be `0.0.0.0`: with `127.0.0.1` the published port 8888 cannot reach the backend. Use `127.0.0.1` when running without Docker |
| `LOCAL_HOST_FRONTEND_IP` | currently only checked by a unit test; nothing in the app uses it |
| `DEBUG_MODE` | `True` prints embedding and upsert progress |
| `MCP_SERVER_URL` | empty (default) keeps the built-in connector tools. Set it to `http://127.0.0.1:8888/mcp/` to host the [MCP server](#mcp-server-optional) and use it. Keep the trailing slash |
| `MCP_AUTH_TOKEN` | bearer token the MCP endpoint requires. The app refuses to start if `MCP_SERVER_URL` is set and this is empty |

For a provider other than Anthropic, install its `langchain-<provider>` package and set all three `LLM_*` variables. The model must support tool calling and structured output.

`ChatAnthropic` rejects a missing `LLM_API_KEY` at startup. The unit tests set a dummy key in `tests/conftest.py` for that reason.

### Create the Pinecone index

The code expects an index named **`quickstart`**. The name is hardcoded in the tools under `src/application/agents/tools/`, and nothing in the running app creates the index. Create it once in the Pinecone console or with the SDK:

- name: `quickstart`
- dimension: `1024` (the output size of `multilingual-e5-large`)
- metric: `cosine`

`DbUtils.create_index` in `src/application/dbutils.py` creates an index with these settings (serverless, AWS `us-east-1`) if you prefer to call it yourself.

### Run with Docker Compose

```bash
cd src
cp .env_example .env      # then fill it in
docker compose up --build
```

| Service | URL |
|---|---|
| Frontend | http://localhost:3000 |
| Backend API (and `/docs`) | http://localhost:8888 |
| Kafka Connect | http://localhost:8083 |
| Demo REST API | http://localhost:8000 |
| PostgreSQL | localhost:5433 (host side; containers use `postgres:5432`) |
| MCP endpoint (only when enabled) | http://localhost:8888/mcp/ |

Notes:

- The app image builds the frontend with `next build` and runs the standalone Next.js server (`FRONTEND_STANDALONE=1`), so it contains no `node_modules` or npm.
- PostgreSQL is published on host port 5433 so it does not clash with a Postgres already running on your machine. The app reaches it over the compose network, so the connector's `host`/`port` stay `postgres`/`5432`.
- The `postgres` volume only loads `dummy_data.sql` the first time it is created. Run `docker compose down -v` to reset it.
- The compose file defines a healthcheck for `docgenie-app` (the frontend on `:3000` and `/docs` on `:8888`), which waits for `postgres`, `kafka-connect` and `fast-api` to be healthy.
- **The app's SQLite database lives inside the `docgenie-app` container and has no volume.** `docker compose down`, `up --force-recreate` and rebuilds start with an empty database, so seeded connectors, users and conversations are lost. `docker compose restart docgenie-app` keeps it.
- `.env` is read when the container is created. After editing it (for example to switch MCP on or off), run `docker compose up -d --force-recreate docgenie-app`, then seed again. A plain `restart` does not pick up `.env` changes.

### Run locally for development

```bash
cd src
python -m venv venv
source venv/bin/activate              # Windows: venv\Scripts\activate
pip install -r requirements-dev.txt

cd application/front_end/docgenie
npm ci
cd ../../..

python main.py                        # backend on :8888, also starts `npm run dev` (frontend on :3000)
```

`requirements.txt` holds runtime dependencies. `requirements-dev.txt` includes it and adds the test and type-check tools. The Dockerfile installs only `requirements.txt`.

The Postgres connector needs Kafka and Debezium. Start only the infrastructure with:

```bash
docker compose up zookeeper kafka kafka-connect postgres
```

Run the backend from `src/`: seed files and OpenAPI specs are read with paths relative to that directory.

### Seed the database

With the backend running:

```bash
curl http://localhost:8888/seed/all
```

This inserts the default permissions, users, conversations and the three example connectors (`SimplyTransport`, `DayofTheWeek`, `postgres_database`). Individual endpoints exist too: `/seed/user`, `/seed/permission`, `/seed/conversation`, `/seed/connector`.

- Seeding is not idempotent. Calling it twice duplicates rows.
- The backend reads connectors from SQLite once at startup, so restart it (`docker compose restart docgenie-app`) after seeding connectors. Until then the connector tools answer "No ... connector named ...".
- `POST /connector/new` registers a connector live, with no restart. That is enough for a `rest` connector. A `postgres` connector also needs its `startup()`, which only runs at app startup, so restart after adding one.
- On startup the Postgres connector registers Debezium and starts its Kafka listener, which can run the ingestion pipeline and so use LLM and Pinecone credits.
- The seeded users (for example `john_doe`, an admin) all use the password `hello`. These are demo credentials only.
- Each seeded user is linked to permissions by name, so `/seed/all` runs permissions before users.

## Connectors

Connectors are stored in the `Connector` table and turned into objects by `ConnectorBuilder` (`src/application/connectors/connector_builder.py`) at startup. The type string `type_c` selects the class.

### REST (`rest`)

`RestConnector` calls an HTTP API with retries and a timeout. If `has_schema` is `"True"`, it loads an OpenAPI spec from `src/application/seeds/connectors/spec_<name>.json` and passes it to the agent as context.

```json
{
  "type_c": "rest",
  "name": "DayofTheWeek",
  "c_params": {
    "base_url": "http://fast-api:8000",
    "api_key": "",
    "headers": { "Content-Type": "application/json" },
    "timeout": 30,
    "retries": 3,
    "has_schema": "True"
  },
  "e_params": {}
}
```

A REST source can notify DocGenie of changes by calling `POST /receive_webhook/{connector_name}`.

### PostgreSQL (`postgres`)

`PostgresConnector` runs SQL for the agent and registers a Debezium connector at `http://connect:8083`. A background thread then consumes Kafka topics whose names start with `e_params.topic` (at `kafka:9092`) and re-runs ingestion on each change.

```json
{
  "type_c": "postgres",
  "name": "postgres_database",
  "c_params": {
    "db_name": "mydatabase", "user": "myuser", "password": "mypassword",
    "host": "postgres", "port": 5432
  },
  "e_params": {
    "event_type": "debezium",
    "class": "io.debezium.connector.postgresql.PostgresConnector",
    "topic": "business_management",
    "include_list": "public.*",
    "plugin.name": "pgoutput",
    "publication.name": "dbz_publication"
  }
}
```

### Add a new connector type

1. Subclass `ConnectorBase` in `src/application/connectors/` and override `startup(integration_agent)` and, if needed, `shutdown()`. Keep `__init__` free of anything that can fail.
2. Register the class under a type string in `ConnectorBuilder.connector_types`.
3. Expose a query tool for it:
   - **Built-in tools (default):** add it in `src/application/agents/tools/query_connectors.py`.
   - **MCP mode:** add an `@mcp.tool()` function in `src/application/mcp_server.py`. The agent finds it through tool discovery, so the agent code and prompt need no change. The agent loads its tools once, so restart the app to pick up a new one.
4. Create a connector record with that `type_c`, through `POST /connector/new` or the seed JSON.

The built-in tools and the MCP tools are two copies of the same two functions today. Until the built-in ones are removed, a new datastore needs a tool in both places if you want both modes to support it.

## MCP server (optional)

The app can host an [MCP](https://modelcontextprotocol.io) server that exposes the connector query tools. The Integration Agent then loads its tools from it, so adding a datastore means adding one tool function in one place. It is **off by default**.

### How it works

- `src/application/mcp_server.py` builds a `FastMCP` server with two tools, `query_rest_connector` and `query_postgres_connector`. They look the connector up in the live `ConnectorBuilder`, check its type, and run the call in a thread (the connector code is blocking).
- `main.py` mounts it at `/mcp` when `MCP_SERVER_URL` is set, wrapped in `BearerAuth`, an ASGI check that returns 401 unless `Authorization: Bearer <MCP_AUTH_TOKEN>` matches. It runs inside the same process as the app so it shares the connectors' open database connections.
- `IntegrationAgent` (`integration_agent.py`) uses `MultiServerMCPClient` over streamable HTTP to fetch the tools on the first run and builds its query agent from them. The graph runs with `ainvoke`, because the adapter's tools are async.
- Postgres change data capture (Debezium and Kafka) is not part of MCP. It is push-based and stays in `PostgresConnector`.

### Turn it on and off

```bash
# src/.env
MCP_SERVER_URL="http://127.0.0.1:8888/mcp/"      # empty string = off
MCP_AUTH_TOKEN="<a long random secret>"          # python3 -c "import secrets; print(secrets.token_hex(32))"
```

Then `docker compose up -d --force-recreate docgenie-app` and seed again (see the note about the SQLite database). The URL is where the app connects to itself, so it stays on `127.0.0.1` even though the backend listens on `0.0.0.0`.

Check the mode with `curl -s -o /dev/null -w "%{http_code}\n" localhost:8888/mcp/`: `401` means on, `404` means off.

### Try the tools with the MCP Inspector

```bash
TOKEN=$(docker exec docgenie-app printenv MCP_AUTH_TOKEN)
npx @modelcontextprotocol/inspector --web --transport http \
  --server-url http://localhost:8888/mcp/ \
  --header "Authorization: Bearer $TOKEN"
```

Open the URL it prints. Example calls, which need the connectors to be loaded:

| Tool | Arguments |
|---|---|
| `query_rest_connector` | `connector_name` `DayofTheWeek`, `endpoint` `/day` |
| `query_postgres_connector` | `connector_name` `postgres_database`, `query` `SELECT * FROM product LIMIT 5;` |

`docker exec ... printenv` gives the token without the quotes that `.env` stores around it. Passing the token as a flag puts it in the process list, so other users on the machine can see it. For a command-line check, use `--cli` with `--method tools/list` instead of `--web`.

### Security

- `query_postgres_connector` runs any SQL and commits it. Anyone with the token can read and write the connected database.
- The backend publishes port 8888, so the app refuses to start with MCP on and no token.
- Use a long random token, and give the connector a read-only database role if the agent only needs to read.
- The token check compares the exact string `Bearer <token>`, so a lowercase `bearer` is rejected.

## API reference

Interactive docs are served at `http://localhost:8888/docs`.

| Method | Path | Description |
|---|---|---|
| POST | `/receive_webhook/{connector_name}` | trigger ingestion from a webhook body. The body is any JSON and is passed to the agent as free text. It is not declared in the OpenAPI schema, so Swagger `/docs` shows no body box; use `curl`. Works for `rest` connectors only (see Known limitations) |
| POST, GET, DELETE | `/mcp/` | MCP endpoint (streamable HTTP, bearer token). Only exists when `MCP_SERVER_URL` is set |
| GET | `/user/{user_id}` | user with permissions |
| POST | `/user/login` | check email and password |
| POST | `/user/create` | create a user |
| PUT | `/user/{user_id}` | replace a user |
| DELETE | `/user/{user_id}` | delete a user |
| GET, PUT, DELETE | `/permission/{permission_id}` | read, update, delete a permission |
| POST | `/permission/create` | create a permission |
| POST | `/conversation/create` | create a conversation |
| POST | `/conversation/all` | all conversations for `user_id` |
| POST | `/conversation/latest` | most recent conversation for `user_id` |
| GET, PUT, DELETE | `/conversation/{convo_id}` | read, update, delete a conversation |
| GET | `/conversation/{convo_id}/chat/all` | all messages in a conversation |
| POST | `/conversation/{convo_id}/chat/create` | store a user message |
| POST | `/conversation/{convo_id}/chat/response` | run the Supervisor Agent and store its answer |
| GET, PUT, DELETE | `/conversation/{convo_id}/chat/{chat_id}` | one message (GET, PUT, DELETE) |
| GET | `/connector/all` | list connectors |
| GET | `/connector/{name}` | one connector's record |
| POST | `/connector/new` | register a connector |
| GET | `/connector/{name}/status` | whether the connector is active |
| GET | `/seed/all`, `/seed/user`, `/seed/permission`, `/seed/conversation`, `/seed/connector` | load seed data |

## Frontend

A Next.js App Router application in `src/application/front_end/docgenie`.

| Route | File | Purpose |
|---|---|---|
| `/` | `src/app/page.tsx` | login form, calls `POST /user/login` |
| `/chat_bot/[id]` | `src/app/chat_bot/[id]/page.tsx` | chat view with a conversation sidebar |
| `/admin/[id]` | `src/app/admin/[id]/page.tsx` | shows the user's details and permissions |

The pages call the backend at `http://127.0.0.1:8888`, which is hardcoded. UI primitives in `src/components/ui/` come from shadcn/ui.

## Testing and quality

Run these from `src/`:

```bash
python -m pytest tests/unit                       # unit tests, Pinecone and the LLM are mocked
coverage run -m pytest tests/unit && coverage report -m
python -m pytest tests/e2e                        # needs live Pinecone and LLM credentials
basedpyright --pythonversion 3.12                 # type check
```

Frontend:

```bash
cd application/front_end/docgenie
npx jest ./tests --ci --coverage
```

`basedpyright` compares against `.basedpyright/baseline.json`, so only errors not in the baseline are reported. Use `--writebaseline` to record new ones.

The tests set `SQL_LITE_DB_STRING` to `sqlite:///test.db`, which creates a local `src/test.db`. It is gitignored and safe to delete.

## CI

`.github/workflows/ci.yml` runs on every push, pull request and manual dispatch:

| Job | What it does |
|---|---|
| `python-unit-tests` | pytest with coverage, uploads the JUnit report |
| `python-e2e-tests` | e2e suite, skipped when `PINECONE_API_KEY` or `LLM_API_KEY` secrets are missing |
| `type-check` | basedpyright; new type errors fail the build |
| `frontend-tests` | Jest with coverage |
| `frontend-build` | `npm ci` and `npm run build` |
| `docker-build` | builds the app and demo REST images without pushing |

## Repository file guide

### Repository root

| Path | Purpose |
|---|---|
| `README.md` | this file |
| `.gitignore` | ignored files for the repo |
| `pyrightconfig.json` | type checking mode (`basic`) for the editor and basedpyright |
| `.basedpyright/baseline.json` | known type errors, so only new ones fail |
| `.github/workflows/ci.yml` | GitHub Actions pipeline |

### `docs/`

| Path | Purpose |
|---|---|
| `docs/proposal/proposal.md` | original project proposal |
| `docs/functional-spec/Functional Specification.pdf` | functional specification |
| `docs/documentation/Technical Manual.pdf` | technical manual |
| `docs/documentation/.gitkeep` | keeps the folder in git |
| `docs/video-walk-through/docgenie_walkthrough.mkv` | video walkthrough |

### `res/diagrams/`

| Path | Purpose |
|---|---|
| `highlevel_architecture.png` | high-level architecture image, used in this README |
| `arch.pu`, `arch.png` | early architecture diagram (PlantUML source and image) |
| `class_diagram.pu`, `class_diagram.png` | early class diagram |
| `dfd.dot`, `dfd.png` | data flow diagram (Graphviz source and image) |
| `final_docs/Architecture_Diagram.*` | final architecture diagram |
| `final_docs/ClassDiagram.*` | final class diagram |
| `final_docs/DFD.png` | final data flow diagram |
| `final_docs/IntegrationAgent.*` | Integration Agent flow |
| `final_docs/RAGAgent.*` | Supervisor (RAG) Agent flow |
| `final_docs/Permission_Diagram.*` | permissions and namespaces |

`.pu` files are PlantUML sources and `.png` files are their renders.

### `src/` (backend root)

| Path | Purpose |
|---|---|
| `main.py` | FastAPI app. Registers routers, the webhook route and CORS, runs connector startup/shutdown in `lifespan`, and when run directly starts the frontend and Uvicorn on `:8888` |
| `config.py` | builds the shared singletons (env, Pinecone wrapper, SQLite client, connector manager, both agents) |
| `__init__.py` | marks `src` as a package |
| `Dockerfile` | two-stage build: Node builds the Next.js standalone bundle, a Python image runs backend and frontend |
| `.dockerignore` | files kept out of the Docker build context |
| `docker-compose.yml` | the six-service stack described above |
| `.env_example` | template for `.env` |
| `.gitignore` | ignore rules for `src/` (databases, `.env`, `venv`, `graphify-out`) |
| `requirements.txt` | runtime Python dependencies |
| `requirements-dev.txt` | runtime plus test and type-check tools |

### `src/application/` (core backend)

| Path | Purpose |
|---|---|
| `__init__.py` | package marker |
| `environment.py` | `Environment`: loads variables from `.env` |
| `dbutils.py` | `DbUtils`: Pinecone wrapper for index creation, embeddings, batched upserts, search, namespace and id listing |
| `llm.py` | `get_llm`: builds the chat model from `LLM_PROVIDER` and `LLM_MODEL` with `init_chat_model` |
| `mcp_server.py` | `create_mcp_server` (the `FastMCP` server with the two connector query tools) and `BearerAuth` (token check for the `/mcp` mount) |

#### `application/agents/`

| Path | Purpose |
|---|---|
| `extras.py` | LangGraph state classes (`State`, `IntegrationState`), the `Router` schema, and `GraphCallback` that prints tool output |
| `supervisor_agent/supervisor_agent.py` | `SupervisorAgent`: the query graph and `take_input` |
| `integration_agent/integration_agent.py` | `IntegrationAgent`: the ingestion graph. Uses the built-in connector tools, or tools from the MCP server when `MCP_SERVER_URL` is set |
| `integration_agent/pinecone_schema.py` | Pydantic models (`PineconeSchema`, `PineconeSchemaHolder`) for the formatter's structured output |
| `integration_agent/__init__.py`, `tools/__init__.py` | package markers |
| `tools/query_dbutils.py` | `query_dbutils`: semantic search over one namespace (top 5) |
| `tools/upsert_dbutils.py` | `upsert_dbutils`: embeds rows and upserts them into a namespace |
| `tools/list_ids_tool.py` | `list_ids`: ids already used under a prefix in a namespace |
| `tools/query_connectors.py` | built-in `query_rest_connector` and `query_postgres_connector` tools (used when MCP is off) |
| `tools/namespace_tool.py` | `namespace`: lists namespaces on the index (not wired into either agent at present) |

#### `application/api/`

| Path | Purpose |
|---|---|
| `dependencies.py` | FastAPI dependency providers for the session, SQL client, Pinecone wrapper, environment, supervisor agent and connector manager; tests override these |
| `sqlclient.py` | `SQLClient`: SQLite engine, table creation, generic CRUD helpers, password hashing and comparison with bcrypt |
| `models/user.py` | `User` table |
| `models/permission.py` | `Permission` table |
| `models/user_permission.py` | link table between users and permissions |
| `models/user_with_permissions.py` | response models that embed permissions |
| `models/conversation.py` | `Conversation` table |
| `models/chat.py` | `Chat` table |
| `models/connector.py` | `Connector` table |
| `models/integration_prompt.py` | `IntegrationPrompt`: builds the user message that tells the Integration Agent which connector changed |
| `models/__init__.py`, `routes/__init__.py`, `__init__.py` | package markers |
| `routes/user_routes.py` | user and permission endpoints, including login |
| `routes/chat_routes.py` | conversation and chat endpoints, including the agent response |
| `routes/connector_routes.py` | connector listing, creation and status |
| `routes/seed_routes.py` | endpoints that load the JSON seed files |

#### `application/connectors/`

| Path | Purpose |
|---|---|
| `connector_base.py` | `ConnectorBase`: shared fields and `startup`/`shutdown` hooks |
| `connector_builder.py` | `ConnectorBuilder`: type registry, loads connectors from SQLite, starts and stops them |
| `rest_connector.py` | `RestConnector`: HTTP client with retries and optional OpenAPI spec |
| `postgres_connector.py` | `PostgresConnector`: SQL execution, Debezium registration, Kafka consumer thread |
| `__init__.py` | package marker |

#### `application/seeds/`

| Path | Purpose |
|---|---|
| `database/user.json`, `permission.json`, `conversation.json` | default users, permissions and conversations for `/seed/*` |
| `connectors/connector_details.json` | the three example connectors |
| `connectors/pinecone_schema.json` | the `{id, text}` row shape, passed to `ConnectorBuilder` |
| `connectors/spec_SimplyTransport.json`, `spec_DayofTheWeek.json` | OpenAPI specs loaded by REST connectors |
| `csv_parser.py`, `seed_parser.py` | old path for loading CSV files into Pinecone; unused |
| `csv/laptop_prices.csv`, `json/bus_data.json` | sample data for that old path |
| `__init__.py` | package marker |

#### `application/front_end/docgenie/` (Next.js app)

| Path | Purpose |
|---|---|
| `package.json`, `package-lock.json` | dependencies and scripts (`dev`, `build`, `start`, `test`) |
| `next.config.mjs` | Next config; `output: "standalone"` for the Docker build |
| `tsconfig.json` | TypeScript settings and the `@/*` alias |
| `postcss.config.mjs` | Tailwind v4 PostCSS plugin |
| `components.json` | shadcn/ui settings |
| `jest.config.js`, `jest.setup.js` | Jest configuration and setup |
| `.gitignore` | frontend ignore rules |
| `src/app/layout.tsx` | root layout, page title and font |
| `src/app/globals.css` | global styles and Tailwind theme |
| `src/app/fonts/GeistVF.woff`, `GeistMonoVF.woff` | bundled fonts |
| `src/app/page.tsx` | login page |
| `src/app/chat_bot/[id]/page.tsx` | chat page |
| `src/app/admin/[id]/page.tsx` | admin/user details page |
| `src/components/chat.tsx` | conversation sidebar and chat window components |
| `src/components/ui/button.tsx`, `card.tsx`, `input.tsx`, `label.tsx`, `textarea.tsx` | shadcn/ui primitives |
| `src/lib/utils.ts` | `cn` class-name helper |
| `tests/Login.test.js`, `Chatbot.test.js`, `Admin.test.js` | Jest tests for the three pages |

### `src/external/` (demo services, not part of the app)

| Path | Purpose |
|---|---|
| `rest_example/fast_api_example.py` | small FastAPI service with `/day`, `/favourite_food` and `/trigger-webhook` |
| `rest_example/Dockerfile`, `requirements.txt`, `.dockerignore` | image build for that service (`requirements.txt` includes `httpx`, which `fast_api_example.py` imports) |
| `postgres_example/dummy_data.sql` | creates and fills a `product` table; loaded by the compose `postgres` service |

### `src/tests/`

| Path | Purpose |
|---|---|
| `conftest.py` | shared fixtures: temporary SQLite, mocked agent, FastAPI test client with dependency overrides |
| `unit/api/test_user_router.py`, `test_chat_router.py`, `test_connector_router.py`, `test_seed_router.py` | route tests |
| `unit/agent/test_supervisor_agent.py` | supervisor routing and limits |
| `unit/agent/test_tools.py` | agent tools |
| `unit/agent/test_mcp_server.py` | MCP server tools, connector type check and bearer auth |
| `unit/connectors/test_connector_builder.py` | connector registry and startup |
| `unit/test_dbutils.py` | Pinecone wrapper |
| `unit/test_sqlclient.py` | SQLite client |
| `unit/test_llm.py` | chat model factory |
| `unit/test_settings.py` | environment loading |
| `e2e/test_supervisor_e2e.py` | supervisor against live Pinecone and LLM, with and without permissions |
| `__init__.py`, `unit/__init__.py`, `unit/api/__init__.py` | package markers |

### Files that are not in git

These appear in a working copy but are generated or local. Do not commit or hand-edit them.

| Path | What it is |
|---|---|
| `src/.env` | your secrets |
| `src/*.db` (`database.db`, `test.db`) | local SQLite databases |
| `src/venv/` | Python virtual environment |
| `src/graphify-out/` | output of the graphify knowledge-graph tool |
| `src/application/front_end/docgenie/node_modules/`, `.next/`, `coverage/`, `.swc/` | frontend dependencies, build output, test coverage, compiler cache |

## Known limitations

- The Pinecone index name `quickstart` is hardcoded and the index is not created automatically.
- The CORS `origins` list in `main.py` is missing a comma after `http://127.0.0.1:3000`, so that entry is joined to the next string.
- API routes have no sessions or tokens. Login returns the user record, and the other routes do not check who is calling.
- Seed users have plaintext passwords in `seeds/database/user.json` (they are hashed when stored).
- The supervisor's loop counters (`context_limit`, `gen_limit`) are instance state shared across requests and only reset when a run finishes.
- The Postgres connector assumes the compose network: Kafka Connect at `http://connect:8083` and Kafka at `kafka:9092`.
- The frontend calls `http://127.0.0.1:8888` directly, so the backend must be reachable at that address from the browser.
- Seed endpoints use `GET` and are not idempotent.
- The app's SQLite database is inside the `docgenie-app` container with no volume, so `down` and `--force-recreate` erase seeded data.
- `POST /receive_webhook/{name}` reads `connector.schema`, which `PostgresConnector` does not have, so a webhook for a Postgres connector fails with a 500. Postgres changes enter through the change listener instead.
- The demo REST API's `/day` and `/favourite_food` return fixed strings (`"Tuesday"`, `"Pizza!"`). Its `/trigger-webhook` waits only 5 seconds for the app, which is shorter than a pipeline run, so it reports an error even when the app finishes.
- MCP mode keeps two copies of the connector query tools (built-in and MCP). Switching the default to MCP and removing the built-in tools has not been done. The full path in MCP mode (webhook, Claude calling the MCP tools, Pinecone upsert) has been checked tool by tool, but has not yet been compared with the built-in path end to end.
- The MCP query agent loads its tools once and caches them, so a tool added to `mcp_server.py` needs an app restart.
- The `BearerAuth` check accepts only the exact `Bearer ` prefix; lowercase `bearer` gets a 401.
- The Postgres change listener subscribes with `auto.offset.reset=latest`, so events from Debezium's initial snapshot may be missed if they arrive before it subscribes.

## Further documentation

- `docs/documentation/Technical Manual.pdf` and `User Manual.pdf`
- `docs/functional-spec/Functional Specification.pdf`
- `docs/proposal/proposal.md`
- `res/diagrams/final_docs/` for the architecture, class, data flow and agent diagrams
