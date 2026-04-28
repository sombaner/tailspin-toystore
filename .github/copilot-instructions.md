# Tailspin Toys Development Guidelines

Game crowdfunding platform: Flask API + SQLAlchemy backend, Astro/Svelte + Tailwind frontend.

**All development MUST comply with the [Constitution](../.specify/memory/constitution.md)** (IaC, pipeline security, testing, containers, observability).

> Scoped instruction files provide file-type-specific details:
> - `flask-endpoint.instructions.md` → `server/routes/*.py`
> - `python-tests.instructions.md` → `server/tests/test_*.py`
> - `ui.instructions.md` → `*.svelte, *.astro, *.css`

---

## Coding Instructions

### General

- Red-Green-Refactor: failing test → implement → refactor
- No placeholder/TODO comments — implement fully or ask for clarification
- Preserve existing patterns when modifying code
- Prefer small, focused changes
- Verify before completion: `./scripts/run-server-tests.sh`, `cd client && npm run build`, `cd client && npm run test:e2e`

### Python / Flask Backend

- **Type hints mandatory** on all function params and return values
- **Routes**: Flask blueprints in `server/routes/`, registered in `server/app.py`
- **Models**: extend `BaseModel` from `server/models/base.py`, placed in `server/models/`
  - Include `@validates` (using `validate_string_length`), `to_dict()` (camelCase keys), `__repr__()`
  - Import new models in `server/models/__init__.py`
- **Queries**: `db.session.query(Model).join(...)` with explicit joins, `isouter=True` for optional; centralize as reusable functions
- **Errors**: `jsonify({"error": "<message>"}), <status_code>`
- **DB init**: use `server/utils/database.py` only
- **Docstrings**: required on all public functions/classes (Args/Returns)
- **Deps**: add to `server/requirements.txt`

### Svelte / Astro Frontend

- **File locations**: components → `client/src/components/*.svelte`, layouts → `layouts/*.astro`, pages → `pages/*.astro`, styles → `styles/global.css`
- **Svelte**: `<script lang="ts">`, TS interfaces for data, `export let` props, `onMount` for fetching, loading/error/empty states
- **Astro**: `prerender = false` for dynamic pages, wrap in `<Layout title="...">`, `client:load` for Svelte components
- **API proxy**: `client/src/middleware.ts` proxies `/api/*` → Flask at `API_SERVER_URL` (default `http://localhost:5100`)
- **Styling**: Tailwind only (no custom CSS except `global.css`/`<style is:global>`), dark-mode-first palette (`slate-900/800`, `blue-600/700`), `data-testid` on key elements
- **Deps**: add to `client/package.json`

### Testing

- **Backend**: `unittest`, in-memory SQLite, `setUp`/`tearDown` with proper cleanup, `TEST_DATA` constants, success + failure cases. Prototype: `server/tests/test_games.py`
- **E2E**: Playwright + TypeScript, `data-testid` selectors, `timeout: 10000`, `test.describe` groups. Prototype: `client/e2e-tests/games.spec.ts`
- **Load**: `playwright.load.config.ts`, `WORKERS`/`PLAYWRIGHT_ITERATIONS` env vars
- **Coverage**: Backend ≥80%, Frontend ≥70%, E2E critical paths 100%

### Infrastructure (Terraform)

- All changes in `infra/` modules: `networking`, `compute`, `acr`, `aks`, `monitoring`, `rbac`
- HashiCorp style: 2-space indent, alphabetical ordering, descriptions on all variables
- Tags via `local.common_tags`: `Environment`, `Project`, `ManagedBy=Terraform`, `Owner`, `CostCenter`
- No hardcoded credentials — variables with defaults in `variables.tf`
- OIDC auth in `providers.tf`/`backend.tf` — do not switch to service principal
- New modules: `variables.tf` + `main.tf` + `outputs.tf`; sensitive outputs marked `sensitive = true`

### Kubernetes

- Manifests in `k8s/`, separate files per resource type
- Required: resource requests/limits, liveness/readiness probes, namespace `tail-spin`, labels `app: tailspin-<component>`
- Images: `ghcr.io/OWNER/REPO/tailspin-<component>:latest` (CI substitutes)
- Services: `ClusterIP` (server), `LoadBalancer` (client)

### Docker

- Server: `python:3.11-slim`, port `5100`, `CMD python app.py`
- Client: `node:lts`, port `4321`, `CMD node ./dist/server/entry.mjs`
- Minimal images, production deps only, `.dockerignore` excludes `node_modules`/`dist`/`.DS_Store`

### GitHub Actions

- Explicit `permissions:` block (least-privilege) on every workflow
- OIDC Azure auth: `id-token: write` + `azure/login@v1` with secrets
- Naming: `<component>-<action>.yml`
- Inline comments, `timeout-minutes` on all jobs, rollback/failure notification steps

---

## Code Review Checklist

### Constitution Compliance

- [ ] IaC changes in Terraform under `infra/`
- [ ] Workflows: explicit `permissions:`, OIDC auth, no hardcoded secrets
- [ ] Tests written before/alongside implementation
- [ ] Dockerfiles: minimal base images; K8s: resource limits + health probes
- [ ] Logging: structured JSON with correlation IDs

### Backend

- [ ] Type hints on all functions
- [ ] Blueprints registered in `app.py`; models extend `BaseModel` with validators/`to_dict()`/`__repr__()`
- [ ] Models imported in `server/models/__init__.py`; `to_dict()` uses camelCase
- [ ] Errors: `jsonify({"error":...})` with proper status codes; no raw SQL; no hardcoded DB paths
- [ ] Docstrings present; unit tests exist with in-memory SQLite and success/failure coverage
- [ ] Tests pass: `./scripts/run-server-tests.sh`

### Frontend

- [ ] `<script lang="ts">` with TS interfaces; loading/error/empty states
- [ ] `data-testid` on key elements; `Layout.astro` wrapper; `prerender = false` on dynamic pages
- [ ] `client:load` directive; dark-mode Tailwind palette; no custom CSS outside globals
- [ ] Responsive layout; hover/focus states; accessible (semantic HTML, ARIA, contrast)
- [ ] Build: `cd client && npm run build`; E2E: `cd client && npm run test:e2e`

### API Changes

- [ ] RESTful conventions under `/api/`; camelCase JSON; meaningful error messages
- [ ] Middleware proxies correctly; Svelte components updated; edge-case tests exist

### Infra & DevOps

- [ ] Terraform: `validate`/`plan` in PR; tags via `common_tags`; vars with descriptions/types/defaults
- [ ] Sensitive outputs marked; K8s: resource limits + probes; no secrets in code
- [ ] Docker: minimal base images; workflows: `permissions:` + OIDC + inline comments

### Cross-Cutting

- [ ] `README.md` updated for new features; `copilot-instructions.md` updated for new patterns
- [ ] No `console.log`/`print()` debug statements; no debug endpoints without `ENABLE_DEBUG_ENDPOINTS`
- [ ] File naming: `snake_case.py`, `PascalCase.svelte`, `kebab-case.astro`, `kebab-case.yaml`
- [ ] Existing scripts unbroken; PR description: what, why, how to test

### Observability

- Structured JSON logs with correlation IDs
- Azure Application Insights + Monitor dashboards
- Alerts: error rate >1%, P95 >2s, pod crashes
- Retention: Logs 30d, Metrics 90d, Traces 7d

## Repository Structure

```
server/          Flask API (models/, routes/, tests/, utils/)
client/          Astro/Svelte frontend (src/components/, layouts/, pages/, styles/)
infra/           Terraform IaC (modules/, environments/)
k8s/             Kubernetes manifests
.github/         Workflows, agents, instructions
scripts/         Dev/deploy scripts
data/            Database files
docs/            Documentation
```
