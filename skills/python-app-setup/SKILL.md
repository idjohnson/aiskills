---
name: python-app-setup
description: Scaffolding and setting up Python applications, FastAPI APIs, FastMCP servers, and project structures in this workspace. ALWAYS trigger this skill whenever the user mentions creating a new Python project, setting up a Python service, scaffolding FastAPI/FastMCP, initializing a Python app from scratch, or asking for Python project conventions.
---

# Python App Setup Skill

Defines the required setup conventions, project structure, and boilerplate rules for Python applications in this workspace.

## Required Project Structure

All Python applications must adhere to the following file layout:

```
project/
├── Dockerfile
├── docker-compose.yaml
├── version.ini
├── pyproject.toml
├── pytest.ini
├── openapi.yaml (required for FastAPI apps)
├── README.md
├── INSTALL.md
├── SYSTEM.md
├── alembic.ini (if database required)
├── app/
│   ├── __init__.py
│   └── main.py
├── alembic/ (if database required)
└── tests/
    ├── __init__.py
    └── test_main.py
```

---

## Architecture & Framework Requirements

### 1. Framework Selection
- **FastAPI**: Preferred for traditional REST APIs and HTTP microservices.
- **FastMCP**: Preferred for Model Context Protocol (MCP) servers (stdio/SSE transport).

### 2. OpenAPI Specification
- Generate an `openapi.yaml` file matching valid OpenAPI 3.x specification.
- For FastAPI apps:
  - Expose `/openapi.yaml` endpoint.
  - Enable Swagger UI at `/docs`.
- For FastMCP servers:
  - Document tool/resource schemas clearly; expose REST endpoints/OpenAPI spec if standard HTTP transport is enabled.

### 3. Docker & Container Registry Standards
- Base image: `python:3.11-slim` (or Python 3.11+).
- Use multi-stage builds for production images and include a container healthcheck.
- Default container port: `8000`.
- **CRITICAL**: The final line of the `Dockerfile` MUST end with a comment referencing the team container registry:
  ```dockerfile
  #harbor.freshbrewed.science/library/<app-name>
  ```

### 4. Version Configuration (`version.ini`)
- Include a root-level `version.ini` initialized to version `0.1`:
  ```ini
  [version]
  version = 0.1
  ```

### 5. Database & Migrations (Alembic)
- If the application requires a database, use [Alembic](https://alembic.sqlalchemy.org/en/latest/) for schema migrations.
- Include `alembic.ini` and a populated `alembic/` migration directory.

### 6. Testing Strategy
- Framework: `pytest`.
- Root-level `pytest.ini` with test configuration.
- Place all test files under `tests/` named `test_*.py`. Include `conftest.py` for shared fixtures.

### 7. Documentation Standards
- **`README.md`**: Project title, quick start, prerequisites, API overview.
- **`INSTALL.md`**: Detailed installation steps, environment variables, database setup, and migration commands.
- **`SYSTEM.md`**: System architecture including a MermaidJS diagram:
  ```mermaid
  graph TB
      Client --> API[FastAPI/FastMCP]
      API --> Service[Business Logic]
      Service --> DB[(Database)]
      API --> External[External Services]
  ```

---

## Virtual Environment & Execution Rules

- Initialize local environment: `python3 -m venv venv`.
- Note for automated executions: Prefer invoking commands via direct venv paths (`venv/bin/pytest`, `venv/bin/python`) to ensure environment isolation across stateless shell executions.

---

## Scaffolding Verification Checklist

When scaffolding a new Python app, verify all items:

- [ ] Virtual environment created (`venv/`)
- [ ] `Dockerfile` present with `#harbor.freshbrewed.science/library/<app-name>` on the final line
- [ ] `docker-compose.yaml` present and configured
- [ ] `version.ini` set to `0.1`
- [ ] `pyproject.toml` and `pytest.ini` present
- [ ] `app/main.py` implemented with FastAPI or FastMCP
- [ ] `openapi.yaml` generated
- [ ] Documentation complete (`README.md`, `INSTALL.md`, `SYSTEM.md` with Mermaid diagram)
- [ ] `tests/` directory populated with working `pytest` tests
- [ ] Database migrations configured via Alembic (if database required)
- [ ] `.dockerignore` file included

---

## Commands

After setup, the following standard execution commands apply:

```bash
# Setup virtual environment
python3 -m venv venv

# Run tests using direct venv executable
venv/bin/pytest

# Run with Docker
docker build -t app .
docker run -p 8000:8000 app

# Run with Docker Compose
docker-compose up --build

# Run database migrations (if database required)
venv/bin/alembic upgrade head

# Generate OpenAPI spec
venv/bin/python -c "from app.main import app; print(app.openapi())"
```
