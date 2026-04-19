<p align="center">
  <img src="./xacta-logo.svg" alt="Xacta" width="260" />
</p>

<h1 align="center">Xacta GRC</h1>

<p align="center">
  Xacta GRC is a modern, open-source Governance, Risk & Compliance platform for managing audits, risk, controls and evidence across your organization. It ships with an audit universe, audit planning & engagements, checklist execution, work papers with review/approval, and dashboards — all on a hardened Django + SvelteKit stack.
</p>

---

## Features

- **Audit universe & entities** — organizational structures, processes, and activities with hierarchy and geographic metadata.
- **Audit planning & engagements** — plans with approvals, engagements with timeline events, progress tracking.
- **Checklists & execution** — reusable checklist templates and live execution with pass/fail results.
- **Work papers** — file upload, review, approval history.
- **IT Asset Management** — extended asset model with ITAM fields.
- **GRC foundation** — 80+ compliance frameworks (ISO 27001, NIST CSF, SOC 2, PCI DSS, GDPR, DORA, CMMC, …), risk scenarios, applied controls, evidence, reports and dashboards.

## Tech stack

| Layer       | Stack                                                     |
| ----------- | --------------------------------------------------------- |
| Backend     | Python 3.12, Django, Django REST Framework, Huey (tasks)  |
| Frontend    | SvelteKit, TypeScript, TailwindCSS, Skeleton UI           |
| Database    | SQLite (default) / PostgreSQL                             |
| Storage     | Local filesystem / S3-compatible                          |
| Reverse proxy | Caddy                                                   |
| Packaging   | Docker / Docker Compose                                   |

---

## Quick start (Docker)

Prerequisites: [Docker](https://docs.docker.com/get-docker/) and Docker Compose. On Windows, use [WSL2](https://learn.microsoft.com/en-us/windows/wsl/install) with Docker Desktop.

```bash
git clone git@github.com:xactasolutionsai/grc.git
cd grc
./docker-compose.sh
```

The script pulls the images, starts the services, waits for the backend to be healthy, and prompts you to create the first superuser.

Once it finishes, open **https://localhost:8443** and log in with the superuser you just created. The certificate is self-signed, so you'll need to accept the browser warning on first visit.

Subsequent runs:

```bash
docker compose up -d      # start
docker compose down       # stop
docker compose logs -f    # follow logs
```

To build the images locally instead of pulling prebuilt ones (useful on ARM or custom architectures):

```bash
./docker-compose-build.sh
```

> For a clean reset, stop the stack and delete the `./db` folder before re-running `./docker-compose.sh`.

---

## Local development setup

### Requirements

- Python **3.12+**, pip **20.3+**, [Poetry](https://python-poetry.org/docs/#installation) **2.0+**
- Node **22+**, npm **10.2+**, pnpm **9+**
- `yaml-cpp` (`brew install yaml-cpp libyaml` or `apt install libyaml-cpp-dev`)

### 1. Clone

```bash
git clone git@github.com:xactasolutionsai/grc.git
cd grc
```

### 2. Backend

```bash
cd backend
poetry install
pre-commit install                 # optional, recommended

# Minimal env (put these in ../myvars and `source` it)
export DJANGO_DEBUG=True
export CISO_ASSISTANT_URL=http://localhost:5173

poetry run python manage.py migrate
poetry run python manage.py createsuperuser
poetry run python manage.py runserver
```

In a second terminal, run the task worker:

```bash
cd backend
poetry run python manage.py run_huey -w 2 -k process
```

By default the backend uses SQLite. To use PostgreSQL or S3 storage, export the relevant env vars (`POSTGRES_*`, `USE_S3=True`, `AWS_*`) before starting the server.

### 3. Frontend

```bash
cd frontend
npm install -g pnpm
pnpm install
pnpm run dev
```

The app is served at **http://localhost:5173**.

---

## Project layout

```
backend/        Django project (audits, workpapers, core, global_settings, …)
frontend/       SvelteKit app (lib/modules/audits, lib/modules/workpapers, routes/…)
config/         Config builder for custom Docker Compose setups
charts/         Helm charts for Kubernetes deployments
cli/            Command-line client (clica)
documentation/  Architecture notes and data model
tools/          Framework converters, excel helpers, questionnaires
```

---

## Running tests

```bash
# Backend
cd backend
poetry run pytest

# Frontend unit tests
cd frontend
pnpm run test
```

---

## AI features (local, via Ollama)

Xacta GRC ships with optional AI assistance that runs **entirely on your own
infrastructure** using [Ollama](https://ollama.com). No data leaves the
deployment; there are no external API calls.

### What you get

- **Risk AI Assistant** — on the Risk Scenario create/edit form, click
  *Analyze Risk* to expand a short title into a structured description,
  threat scenario, likelihood justification, suggested mitigations, and
  security domains.
- **Smart Auto-Fill** — an *Expand with AI* button on Risk, Applied
  Control / Policy, Reference Control, and Finding forms rewrites short
  input into professional prose.
- **Generate Controls from Risk** — on the Applied Controls list page,
  generate 3–6 candidate controls from a risk description; each result has
  a one-click "Add to form" that opens the standard create modal pre-filled.
- **Generate Finding** — inside the Finding form, turn a raw observation
  into a structured finding (title, description, severity, recommendation).
- **Dashboard Insights** — at the top of `/analytics`, click *Generate
  insights* to get top risks, compliance gaps, recommended actions and an
  executive summary based on your scoped data.

### Enabling

The provided `docker-compose.yml` / `docker-compose-build.yml` already
include an `ollama` service and a one-shot `ollama-pull` sidecar that pulls
the selected model on first boot.

```bash
docker compose up -d
# First boot only: wait for ollama-pull to finish (~4 GB for llama3)
docker logs -f ollama-pull
```

Relevant environment variables (all have sensible defaults):

| Var            | Default                     | Purpose                                   |
|----------------|-----------------------------|-------------------------------------------|
| `AI_ENABLED`   | `True`                      | Master switch. Set `False` to return 503. |
| `OLLAMA_URL`   | `http://ollama:11434`       | Ollama HTTP endpoint used by the backend. |
| `OLLAMA_MODEL` | `llama3`                    | Any model tag from `ollama pull`.         |
| `AI_RATE_LIMIT`| `30/min`                    | DRF throttle per-user on `/api/ai/*`.     |

To use a smaller model (faster on CPU-only hosts):

```bash
OLLAMA_MODEL=phi3 docker compose up -d
```

### Endpoints

All endpoints live under `/api/ai/` and require authentication
(Knox token). They respond with `{ data, raw, parse_error }`:

- `POST /api/ai/analyze-risk` — `{ input }`
- `POST /api/ai/expand-text` — `{ text, field_type, context? }`
- `POST /api/ai/generate-controls` — `{ risk_description }`
- `POST /api/ai/generate-finding` — `{ observation }`
- `POST /api/ai/dashboard-insights` — no body; uses the caller's
  accessible folders to build context.

### Security notes

- Prompts are sent **only** to the in-cluster Ollama service. Do not expose
  port `11434` publicly.
- The backend never logs full prompt bodies — only duration, model name,
  and prompt length.
- When the model returns non-JSON, the API surfaces `parse_error: true` and
  the frontend shows a retry-friendly toast instead of auto-filling fields.

---

## License

This project is a fork of [intuitem/ciso-assistant-community](https://github.com/intuitem/ciso-assistant-community) and is distributed under its original AGPL-3.0 license. See [LICENSE.md](./LICENSE.md) and [LICENSE-AGPL.txt](./LICENSE-AGPL.txt).

© Xacta Solutions AI.
