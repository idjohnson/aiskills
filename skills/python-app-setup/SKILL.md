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
├── .gitea/
│   └── workflows/
│       └── cicd.yaml
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
├── helm-chart/ (required for CI/CD Helm packaging)
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

### 8. CI/CD (Gitea Actions)
- Every project must include a Gitea Actions workflow at `.gitea/workflows/cicd.yaml` that builds the Docker image on push to `main`, publishes it to both the team Harbor registry and Dockerhub, and packages/pushes the Helm chart as an OCI artifact.
- Use [assets/gitea-cicd.yaml](assets/gitea-cicd.yaml) as the template. Copy it into the new project unmodified except for:
  - The Helm push target `oci://harbor.freshbrewed.science/chartrepo/<app-name>-helm` — replace `<app-name>` with the actual application name.
- The workflow derives its build tags dynamically, so no other app-specific edits are required as long as these conventions are followed:
  - `version.ini` has a `version = X.Y` key under a `[version]` (or equivalent) section — the workflow reads it with `awk` to tag the image.
  - The final line of the `Dockerfile` is `#harbor.freshbrewed.science/library/<app-name>` (see Docker & Container Registry Standards above) — the workflow strips the leading `#` to get the Harbor push target and uses the segment after the last `/` as the Dockerhub image name.
  - A `helm-chart/` directory exists at the project root containing a valid Helm chart — it gets packaged and pushed as an OCI artifact.
- The workflow expects these secrets to be configured in the Gitea repo: `CR_PAT`/`CR_USER` (Harbor registry + chart repo credentials) and `DHPAT`/`DHUSER` (Dockerhub credentials). Mention these in `INSTALL.md` so operators know to set them up.

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
- [ ] `.gitea/workflows/cicd.yaml` present (from [assets/gitea-cicd.yaml](assets/gitea-cicd.yaml)) with `<app-name>` substituted in the Helm OCI push target
- [ ] `helm-chart/` directory present with a valid Helm chart for CI/CD packaging

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

# Set up the Gitea CI/CD workflow (replace <skill-dir> with this skill's own
# directory, and "myapp" with the project name)
mkdir -p .gitea/workflows
cp <skill-dir>/assets/gitea-cicd.yaml .gitea/workflows/cicd.yaml
sed -i 's/<app-name>/myapp/' .gitea/workflows/cicd.yaml
```
