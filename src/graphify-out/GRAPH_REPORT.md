# Graph Report - .  (2026-10-21)

## Corpus Check
- Corpus is ~14,736 words - fits in a single context window. You may not need a graph.

## Summary
- 427 nodes · 904 edges · 40 communities detected
- Extraction: 44% EXTRACTED · 56% INFERRED · 0% AMBIGUOUS · INFERRED: 502 edges (avg confidence: 0.69)
- Token cost: 0 input · 0 output

## Community Hubs (Navigation)
- [[_COMMUNITY_Data Models & SQL Client|Data Models & SQL Client]]
- [[_COMMUNITY_Test Fixtures|Test Fixtures]]
- [[_COMMUNITY_Connectors|Connectors]]
- [[_COMMUNITY_Integration Agent & Tools|Integration Agent & Tools]]
- [[_COMMUNITY_Pinecone & Seed Parsers|Pinecone & Seed Parsers]]
- [[_COMMUNITY_API Routes|API Routes]]
- [[_COMMUNITY_Supervisor Agent|Supervisor Agent]]
- [[_COMMUNITY_Agent Test Mocks|Agent Test Mocks]]
- [[_COMMUNITY_Runtime & Docker Setup|Runtime & Docker Setup]]
- [[_COMMUNITY_Seed Routes|Seed Routes]]
- [[_COMMUNITY_API Dependencies|API Dependencies]]
- [[_COMMUNITY_Setup & Dependencies|Setup & Dependencies]]
- [[_COMMUNITY_Chatbot Page|Chatbot Page]]
- [[_COMMUNITY_Chatbot Test|Chatbot Test]]
- [[_COMMUNITY_Login Page|Login Page]]
- [[_COMMUNITY_Root Layout|Root Layout]]
- [[_COMMUNITY_Admin Page|Admin Page]]
- [[_COMMUNITY_Home Page|Home Page]]
- [[_COMMUNITY_Pytest|Pytest]]
- [[_COMMUNITY_Basedpyright|Basedpyright]]
- [[_COMMUNITY_ConfigInit 20|Config/Init 20]]
- [[_COMMUNITY_ConfigInit 21|Config/Init 21]]
- [[_COMMUNITY_ConfigInit 22|Config/Init 22]]
- [[_COMMUNITY_ConfigInit 23|Config/Init 23]]
- [[_COMMUNITY_ConfigInit 24|Config/Init 24]]
- [[_COMMUNITY_ConfigInit 25|Config/Init 25]]
- [[_COMMUNITY_ConfigInit 26|Config/Init 26]]
- [[_COMMUNITY_ConfigInit 27|Config/Init 27]]
- [[_COMMUNITY_ConfigInit 28|Config/Init 28]]
- [[_COMMUNITY_ConfigInit 29|Config/Init 29]]
- [[_COMMUNITY_ConfigInit 30|Config/Init 30]]
- [[_COMMUNITY_ConfigInit 31|Config/Init 31]]
- [[_COMMUNITY_ConfigInit 32|Config/Init 32]]
- [[_COMMUNITY_ConfigInit 33|Config/Init 33]]
- [[_COMMUNITY_ConfigInit 34|Config/Init 34]]
- [[_COMMUNITY_ConfigInit 35|Config/Init 35]]
- [[_COMMUNITY_ConfigInit 36|Config/Init 36]]
- [[_COMMUNITY_ConfigInit 37|Config/Init 37]]
- [[_COMMUNITY_ConfigInit 38|Config/Init 38]]
- [[_COMMUNITY_ConfigInit 39|Config/Init 39]]

## God Nodes (most connected - your core abstractions)
1. `SQLClient` - 39 edges
2. `User` - 39 edges
3. `Environment` - 36 edges
4. `DbUtils` - 29 edges
5. `Conversation` - 28 edges
6. `ConnectorBuilder` - 28 edges
7. `Chat` - 27 edges
8. `Connector` - 22 edges
9. `Permission` - 19 edges
10. `SupervisorAgent` - 18 edges

## Surprising Connections (you probably didn't know these)
- `get_test_conversation()` --calls--> `Conversation`  [INFERRED]
  tests/conftest.py → application/api/models/conversation.py
- `get_test_chat()` --calls--> `Chat`  [INFERRED]
  tests/conftest.py → application/api/models/chat.py
- `fastapi (rest_example)` --semantically_similar_to--> `fastapi`  [INFERRED] [semantically similar]
  external/rest_example/requirements.txt → requirements.txt
- `MockAgent` --uses--> `DbUtils`  [INFERRED]
  tests/conftest.py → application/dbutils.py
- `MockAgent` --uses--> `SupervisorAgent`  [INFERRED]
  tests/conftest.py → application/agents/supervisor_agent/supervisor_agent.py

## Hyperedges (group relationships)
- **Developer workflow tooling** — readme_unit_testing, readme_type_checking, requirements_pytest, requirements_basedpyright [INFERRED 0.80]

## Communities

### Community 0 - "Data Models & SQL Client"
Cohesion: 0.09
Nodes (46): Chat, environment_fixture(), MockAgent, sqlclient_fixture(), Connector, Conversation, Environment, Permission (+38 more)

### Community 1 - "Test Fixtures"
Cohesion: 0.07
Nodes (54): create_test_chat(), create_test_conversation(), get_test_permission(), get_test_permission_json(), get_test_rest_connector_json(), get_test_user(), get_test_user_json(), test_create_chat_success() (+46 more)

### Community 2 - "Connectors"
Cohesion: 0.07
Nodes (22): get_test_rest_connector(), ConnectorBase, ConnectorBuilder, Adds a new connector and starts it up., Go to each connector and run its startup method.             Connector types tha, Go to each connector and run its shutdown method.             Connector types wi, ConnectorBase, IntegrationPrompt (+14 more)

### Community 3 - "Integration Agent & Tools"
Cohesion: 0.05
Nodes (27): BaseCallbackHandler, BaseModel, GraphCallback, IntegrationState, Router, State, trigger_webhook(), WebhookPayload (+19 more)

### Community 4 - "Pinecone & Seed Parsers"
Cohesion: 0.08
Nodes (20): BaseSeedParser, dbutils_fixture(), CSVParser, DbUtils, mock_env(), mock_pinecone_client(), A test for getting namespaces from an index, A test for getting the client (+12 more)

### Community 5 - "API Routes"
Cohesion: 0.1
Nodes (26): create_chat(), create_conversation(), delete_chat(), delete_conversation(), get_all_chats_in_conversation(), get_all_conversations(), get_chat(), get_conversation() (+18 more)

### Community 6 - "Supervisor Agent"
Cohesion: 0.11
Nodes (18): create_response(), supervisor_agent(), SupervisorAgent, test_context_node(), test_context_node_empty_response(), test_gen_node(), test_gen_node_empty_response(), test_initialization() (+10 more)

### Community 7 - "Agent Test Mocks"
Cohesion: 0.11
Nodes (6): get_test_chat(), get_test_conversation(), mock_chat_mistralai(), mock_chat_mistralai_structured(), object, BaseSeedParser

### Community 8 - "Runtime & Docker Setup"
Cohesion: 0.25
Nodes (8): Node frontend (npm run dev), main.py (runs backend and frontend), fastapi, Kafka clients (aiokafka, confluent-kafka), fast-api-example Docker image (port 8000), Dockerised FastAPI example setup, fastapi (rest_example), uvicorn (rest_example)

### Community 9 - "Seed Routes"
Cohesion: 0.62
Nodes (5): seed_all_db(), seed_connector_db(), seed_conversations_db(), seed_permission_db(), seed_users_db()

### Community 10 - "API Dependencies"
Cohesion: 0.29
Nodes (0): 

### Community 11 - "Setup & Dependencies"
Cohesion: 0.29
Nodes (7): .env file (.env_example), Python 3.10.11, Project Setup, Python venv, langchain provider packages (anthropic, openai, mistralai, deepseek), langgraph, pinecone

### Community 12 - "Chatbot Page"
Cohesion: 0.4
Nodes (0): 

### Community 13 - "Chatbot Test"
Cohesion: 1.0
Nodes (0): 

### Community 14 - "Login Page"
Cohesion: 1.0
Nodes (0): 

### Community 15 - "Root Layout"
Cohesion: 1.0
Nodes (0): 

### Community 16 - "Admin Page"
Cohesion: 1.0
Nodes (0): 

### Community 17 - "Home Page"
Cohesion: 1.0
Nodes (0): 

### Community 18 - "Pytest"
Cohesion: 1.0
Nodes (2): Unit testing with pytest, pytest

### Community 19 - "Basedpyright"
Cohesion: 1.0
Nodes (2): Type checking with basedpyright (baseline), basedpyright

### Community 20 - "Config/Init 20"
Cohesion: 1.0
Nodes (0): 

### Community 21 - "Config/Init 21"
Cohesion: 1.0
Nodes (0): 

### Community 22 - "Config/Init 22"
Cohesion: 1.0
Nodes (0): 

### Community 23 - "Config/Init 23"
Cohesion: 1.0
Nodes (0): 

### Community 24 - "Config/Init 24"
Cohesion: 1.0
Nodes (0): 

### Community 25 - "Config/Init 25"
Cohesion: 1.0
Nodes (0): 

### Community 26 - "Config/Init 26"
Cohesion: 1.0
Nodes (0): 

### Community 27 - "Config/Init 27"
Cohesion: 1.0
Nodes (0): 

### Community 28 - "Config/Init 28"
Cohesion: 1.0
Nodes (0): 

### Community 29 - "Config/Init 29"
Cohesion: 1.0
Nodes (0): 

### Community 30 - "Config/Init 30"
Cohesion: 1.0
Nodes (0): 

### Community 31 - "Config/Init 31"
Cohesion: 1.0
Nodes (0): 

### Community 32 - "Config/Init 32"
Cohesion: 1.0
Nodes (0): 

### Community 33 - "Config/Init 33"
Cohesion: 1.0
Nodes (0): 

### Community 34 - "Config/Init 34"
Cohesion: 1.0
Nodes (0): 

### Community 35 - "Config/Init 35"
Cohesion: 1.0
Nodes (0): 

### Community 36 - "Config/Init 36"
Cohesion: 1.0
Nodes (0): 

### Community 37 - "Config/Init 37"
Cohesion: 1.0
Nodes (0): 

### Community 38 - "Config/Init 38"
Cohesion: 1.0
Nodes (0): 

### Community 39 - "Config/Init 39"
Cohesion: 1.0
Nodes (0): 

## Knowledge Gaps
- **17 isolated node(s):** `A single row in the pinecone.`, `Holder for each row in the pinecone.`, `Factory to allow access to the dbutils and not trip up the draconian pydantic.`, `Factory to allow access to the dbutils and not trip up the draconian pydantic.`, `Python 3.10.11` (+12 more)
  These have ≤1 connection - possible missing edges or undocumented components.
- **Thin community `Chatbot Test`** (2 nodes): `Chatbot.test.js`, `handleSettingsClick()`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Login Page`** (2 nodes): `page.js`, `Login()`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Root Layout`** (2 nodes): `layout.js`, `RootLayout()`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Admin Page`** (2 nodes): `page.js`, `AdminPage()`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Home Page`** (2 nodes): `page.js`, `Page()`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Pytest`** (2 nodes): `Unit testing with pytest`, `pytest`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Basedpyright`** (2 nodes): `Type checking with basedpyright (baseline)`, `basedpyright`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Config/Init 20`** (1 nodes): `__init__.py`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Config/Init 21`** (1 nodes): `config.py`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Config/Init 22`** (1 nodes): `__init__.py`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Config/Init 23`** (1 nodes): `__init__.py`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Config/Init 24`** (1 nodes): `__init__.py`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Config/Init 25`** (1 nodes): `__init__.py`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Config/Init 26`** (1 nodes): `__init__.py`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Config/Init 27`** (1 nodes): `__init__.py`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Config/Init 28`** (1 nodes): `jest.setup.js`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Config/Init 29`** (1 nodes): `jest.config.js`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Config/Init 30`** (1 nodes): `next.config.mjs`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Config/Init 31`** (1 nodes): `postcss.config.mjs`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Config/Init 32`** (1 nodes): `tailwind.config.js`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Config/Init 33`** (1 nodes): `Admin.test.js`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Config/Init 34`** (1 nodes): `Login.test.js`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Config/Init 35`** (1 nodes): `__init__.py`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Config/Init 36`** (1 nodes): `__init__.py`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Config/Init 37`** (1 nodes): `__init__.py`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Config/Init 38`** (1 nodes): `__init__.py`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Config/Init 39`** (1 nodes): `__init__.py`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `DbUtils` connect `Pinecone & Seed Parsers` to `Data Models & SQL Client`, `Integration Agent & Tools`, `Supervisor Agent`, `Agent Test Mocks`?**
  _High betweenness centrality (0.148) - this node is a cross-community bridge._
- **Why does `SupervisorAgent` connect `Supervisor Agent` to `Data Models & SQL Client`, `Integration Agent & Tools`, `Pinecone & Seed Parsers`?**
  _High betweenness centrality (0.136) - this node is a cross-community bridge._
- **Why does `IntegrationAgent` connect `Integration Agent & Tools` to `Data Models & SQL Client`, `Connectors`, `Pinecone & Seed Parsers`?**
  _High betweenness centrality (0.132) - this node is a cross-community bridge._
- **Are the 24 inferred relationships involving `SQLClient` (e.g. with `MockAgent` and `Testing if hash_password method works`) actually correct?**
  _`SQLClient` has 24 INFERRED edges - model-reasoned connections that need verification._
- **Are the 37 inferred relationships involving `User` (e.g. with `MockAgent` and `Testing if hash_password method works`) actually correct?**
  _`User` has 37 INFERRED edges - model-reasoned connections that need verification._
- **Are the 33 inferred relationships involving `Environment` (e.g. with `MockAgent` and `A mock for environment`) actually correct?**
  _`Environment` has 33 INFERRED edges - model-reasoned connections that need verification._
- **Are the 14 inferred relationships involving `DbUtils` (e.g. with `MockAgent` and `A mock for environment`) actually correct?**
  _`DbUtils` has 14 INFERRED edges - model-reasoned connections that need verification._