# Tailspin Toys Crowd Funding Development Guidelines

This is a crowdfunding platform for games with a developer theme. The application uses a Flask backend API with SQLAlchemy ORM for database interactions, and an Astro/Svelte frontend with Tailwind CSS for styling.

**IMPORTANT**: All development MUST comply with the [Tailspin Toys Constitution](../.specify/memory/constitution.md), which defines non-negotiable principles for IaC, pipeline security, testing, containerization, and observability. When in doubt, refer to the constitution first.

Please follow these guidelines when contributing:


---

## Copilot Coding Instructions

### General Coding Behavior

- Always read and comply with the [Tailspin Toys Constitution](../.specify/memory/constitution.md) before generating code
- Follow the Red-Green-Refactor cycle: write a failing test first, then implement to make it pass, then refactor
- Never generate placeholder or TODO comments in production code — implement the full solution or explicitly ask for clarification
- When modifying existing code, preserve the established patterns and conventions already in the file
- Prefer small, focused changes over large sweeping rewrites
- Always run the relevant scripts before considering work complete:
  - Backend: `./scripts/run-server-tests.sh`
  - Frontend build: `cd client && npm run build`
  - E2E tests: `cd client && npm run test:e2e`

### Python / Flask Backend Coding

- **Type hints are mandatory**: All function parameters and return values MUST have type annotations
  ```python
  def get_game(id: int) -> tuple[Response, int] | Response:
  ```
- **Blueprints**: All new API routes MUST be created as Flask blueprints in `server/routes/` and registered in `server/app.py`
- **Models**: New SQLAlchemy models MUST extend `BaseModel` from `server/models/base.py` and be placed in `server/models/`
  - Include `@validates` decorators for field validation using `validate_string_length`
  - Include a `to_dict()` method for JSON serialization
  - Include a `__repr__()` method for debugging
  - Use camelCase for JSON output keys (e.g., `starRating` not `star_rating`) in `to_dict()`
- **Model imports**: New models MUST be imported in `server/models/__init__.py` to avoid circular imports
- **Query patterns**: Use `db.session.query(Model).join(...)` with explicit join conditions and `isouter=True` for optional relationships; centralize base queries as reusable functions (see `get_games_base_query()` in `server/routes/games.py`)
- **Error responses**: Return `jsonify({"error": "<message>"}), <status_code>` for error conditions
- **Database utility**: Use `server/utils/database.py` for database initialization; never configure database URIs directly in route files
- **Dependencies**: Add new Python packages to `server/requirements.txt` (pinned or unpinned matching existing style)
- **Docstrings**: All public functions and classes MUST have docstrings with Args/Returns sections

### Svelte / Astro Frontend Coding

- **Component placement**:
  - Interactive components → `client/src/components/*.svelte`
  - Page layouts → `client/src/layouts/*.astro`
  - Page routes → `client/src/pages/*.astro` (use `[param].astro` for dynamic routes)
  - Static assets → `client/src/assets/` or `client/public/`
  - Global styles → `client/src/styles/global.css`
- **Svelte components**:
  - Use `<script lang="ts">` for all Svelte component scripts
  - Define TypeScript interfaces for component data shapes (e.g., `interface Game { ... }`)
  - Use `export let` for component props with sensible defaults
  - Implement loading, error, and empty states for all data-fetching components (see `GameList.svelte` pattern)
  - Use `onMount` for data fetching; do not fetch in reactive statements
- **Astro pages**:
  - Set `export const prerender = false;` for dynamic pages that need server-side rendering
  - Import Layout from `../layouts/Layout.astro` and wrap page content in `<Layout title="...">` 
  - Use `client:load` directive when embedding Svelte components in Astro pages
  - Import `../styles/global.css` in pages that don't use Layout
- **API middleware**: API calls from the frontend go through `client/src/middleware.ts`, which proxies `/api/*` requests to the Flask backend at `API_SERVER_URL` (defaults to `http://localhost:5100`). Frontend components should call `/api/...` paths directly
- **Styling rules**:
  - Use Tailwind CSS utility classes exclusively — no custom CSS except in `global.css` or `<style is:global>`
  - Dark mode is the default: use `bg-slate-900`, `text-white`, `bg-slate-800/60`, `border-slate-700` palette
  - Use `backdrop-blur-sm` for glassmorphism card effects
  - Cards: `rounded-xl overflow-hidden shadow-lg border border-slate-700/50`
  - Buttons: `bg-blue-600 hover:bg-blue-700 text-white rounded-lg transition-all duration-300`
  - Interactive hover states: `hover:border-blue-500/50 hover:shadow-blue-500/10 hover:translate-y-[-6px]`
  - Loading skeletons: use `animate-pulse` with `bg-slate-700` placeholder divs
- **Test IDs**: Add `data-testid` attributes to key UI elements for E2E tests (e.g., `data-testid="game-card"`, `data-testid="game-details-title"`)
- **Dependencies**: Add new npm packages to `client/package.json` matching the existing version style

### Testing

- **Backend tests** (`server/tests/test_*.py`):
  - Use Python `unittest` module
  - Create a fresh Flask app with `sqlite:///:memory:` for each test class in `setUp()`
  - Use `init_db(self.app, testing=True)` for test database initialization
  - Always call `db.session.remove()`, `db.drop_all()`, `db.engine.dispose()` in `tearDown()`
  - Define shared `TEST_DATA` class constants for seed data
  - Include tests for both success and failure/not-found scenarios
  - Use descriptive method names: `test_<functionality>_<scenario>` (e.g., `test_get_games_success`, `test_get_game_not_found`)
  - Type annotate all test methods with `-> None` return type
  - Prototype: follow patterns in `server/tests/test_games.py`
- **E2E tests** (`client/e2e-tests/*.spec.ts`):
  - Use Playwright with TypeScript
  - Use `data-testid` selectors over CSS class selectors for stability
  - Include reasonable timeouts for async content (`timeout: 10000`)
  - Group related tests with `test.describe('Feature Name', () => { ... })`
  - Test user flows end-to-end: navigation, data display, error states
  - Prototype: follow patterns in `client/e2e-tests/games.spec.ts`
- **Load tests** (`client/e2e-tests/ui-load.spec.ts`):
  - Use the separate `playwright.load.config.ts` config — no local dev server started
  - Control concurrency with `WORKERS` and iterations with `PLAYWRIGHT_ITERATIONS` env vars
- **Test coverage targets** (per Constitution Principle III):
  - Backend ≥ 80%
  - Frontend ≥ 70%
  - E2E critical user paths: 100%

### Infrastructure as Code (Terraform)

- All changes MUST go in `infra/` with the existing module structure: `modules/networking`, `modules/compute`, `modules/acr`, `modules/aks`, `modules/monitoring`, `modules/rbac`
- Follow HashiCorp style: 2-space indentation, alphabetical resource ordering, descriptions on all variables
- Use `local.common_tags` for consistent tagging: `Environment`, `Project`, `ManagedBy=Terraform`, `Owner`, `CostCenter`
- Never hardcode credentials or Azure resource names — use variables with defaults in `variables.tf`
- OIDC is configured in `infra/providers.tf` (`use_oidc = true`) and `infra/backend.tf` — do not switch to service principal authentication
- New modules MUST include `variables.tf`, `main.tf`, and `outputs.tf`
- All outputs that contain sensitive data MUST be marked `sensitive = true`

### Kubernetes Manifests

- Place manifests in `k8s/` directory with separate files per resource type
- All deployments MUST include:
  - Resource requests AND limits for CPU and memory
  - Liveness and readiness probes with appropriate paths and timings
  - Namespace: `tail-spin`
  - Labels: `app: tailspin-<component>`
- Use the image placeholder pattern: `ghcr.io/OWNER/REPO/tailspin-<component>:latest` (CI substitutes at deploy time)
- Services: Use `ClusterIP` for internal services (server), `LoadBalancer` for external-facing services (client)

### Docker

- `server/Dockerfile`: Base image `python:3.11-slim`, expose port `5100`, CMD `python app.py`
- `client/Dockerfile`: Base image `node:lts`, expose port `4321`, CMD `node ./dist/server/entry.mjs`
- Keep images minimal — install only production dependencies
- Use `.dockerignore` to exclude `node_modules`, `dist`, `.DS_Store`

### GitHub Actions Workflows

- Every workflow MUST have an explicit `permissions:` block with least-privilege
- Use OIDC for Azure authentication (`id-token: write` permission + `azure/login@v1` with `client-id`, `tenant-id`, `subscription-id` from secrets)
- Follow naming convention: `<component>-<action>.yml` (e.g., `app-deploy.yml`, `container-build.yml`)
- Include inline comments explaining each step's purpose
- Set `timeout-minutes` on all jobs to prevent runaway builds
- Include rollback / failure notification steps

---

## Copilot Code Review Instructions

### Constitution Compliance Checks

- [ ] **IaC (Principle I)**: Any infrastructure change is defined in Terraform under `infra/`, not done manually
- [ ] **Pipeline Security (Principle II)**: Workflows have explicit `permissions:` blocks, use OIDC auth, no hardcoded secrets
- [ ] **Test-First (Principle III)**: New features include corresponding tests; tests were written before (or alongside) the implementation
- [ ] **Container Best Practices (Principle IV)**: Dockerfiles use minimal base images, K8s manifests have resource limits and health probes
- [ ] **Observability (Principle V)**: Changes that affect logging use structured JSON format with correlation IDs

### Backend Code Review Checklist

- [ ] All functions have type hints for parameters and return values
- [ ] New routes use Flask blueprints and are registered in `server/app.py`
- [ ] New models extend `BaseModel`, include validators, `to_dict()`, and `__repr__()`
- [ ] New models are imported in `server/models/__init__.py`
- [ ] `to_dict()` uses camelCase keys for JSON consistency with the frontend
- [ ] Error responses use `jsonify({"error": "..."})` with appropriate HTTP status codes
- [ ] No raw SQL — all queries use SQLAlchemy ORM
- [ ] No hardcoded file paths for the database — use `utils/database.py`
- [ ] Docstrings present on public functions and classes
- [ ] Corresponding unit tests exist in `server/tests/test_*.py`
- [ ] Tests use in-memory SQLite (`sqlite:///:memory:`) and proper `setUp/tearDown`
- [ ] Tests cover both success and failure scenarios (e.g., 404 for not found)
- [ ] Tests pass: `./scripts/run-server-tests.sh`

### Frontend Code Review Checklist

- [ ] Svelte components use `<script lang="ts">` with TypeScript interfaces for data shapes
- [ ] Components handle loading, error, and empty states gracefully
- [ ] `data-testid` attributes are present on key interactive and display elements
- [ ] Pages use the `Layout.astro` wrapper with an appropriate `title` prop
- [ ] Dynamic pages set `export const prerender = false;`
- [ ] Svelte components embedded in Astro pages use `client:load` directive
- [ ] Tailwind classes follow the dark-mode-first palette (slate-800/900, blue-500/600 accents)
- [ ] No custom CSS outside `global.css` or `<style is:global>` blocks
- [ ] Interactive elements have visible hover/focus states and transitions
- [ ] UI is responsive: uses `grid-cols-1 sm:grid-cols-2 lg:grid-cols-3` (or similar) for card layouts
- [ ] Build succeeds: `cd client && npm run build`
- [ ] E2E tests cover the new UI flow: `cd client && npm run test:e2e`
- [ ] Accessibility: semantic HTML elements, ARIA attributes where needed, color contrast sufficient

### API Change Review Checklist

- [ ] API follows RESTful conventions: proper HTTP methods, resource-based URLs under `/api/`
- [ ] Request/response schema is consistent with existing endpoints (camelCase JSON keys)
- [ ] Error responses include meaningful messages and appropriate status codes
- [ ] Middleware in `client/src/middleware.ts` correctly proxies the new route (no changes needed if under `/api/`)
- [ ] Corresponding Svelte components updated to consume the new/changed API
- [ ] API tests exist and cover edge cases (invalid IDs, missing data, empty results)

### Infrastructure & DevOps Review Checklist

- [ ] Terraform changes include `terraform validate` and `terraform plan` output in PR description
- [ ] New Terraform resources include all required tags via `local.common_tags`
- [ ] Variables have `description`, `type`, and sensible `default` values
- [ ] Sensitive outputs are marked `sensitive = true`
- [ ] Kubernetes manifests specify resource requests/limits, liveness/readiness probes
- [ ] Docker images use multi-stage builds or minimal base images
- [ ] No secrets, credentials, or connection strings in code or manifests
- [ ] Workflow files have explicit `permissions:` and use OIDC auth
- [ ] Workflow changes include inline comments documenting new steps

### Cross-Cutting Review Concerns

- [ ] `README.md` updated if new features, commands, or setup steps were added
- [ ] `copilot-instructions.md` updated if new patterns, scripts, or project structure changes were introduced
- [ ] No `console.log` / `print()` debug statements left in production code (structured logging only)
- [ ] No temporary/debug endpoints exposed without the `ENABLE_DEBUG_ENDPOINTS` guard
- [ ] File naming follows conventions: `snake_case.py` for Python, `PascalCase.svelte` for components, `kebab-case.astro` for pages, `kebab-case.yaml` for K8s manifests
- [ ] Changes don't break existing scripts (`scripts/setup-env.sh`, `scripts/run-server-tests.sh`, `scripts/start-app.sh`)
- [ ] PR description includes what was changed, why, and how to test it

### Observability

- Emit structured logs in JSON format with correlation IDs
- Integrate with Azure Application Insights for telemetry
- Configure Azure Monitor dashboards for each environment
- Set up alerts: error rate >1%, response time P95 >2s, pod crashes
- Log retention: Logs 30d, Metrics 90d, Traces 7d

## Repository Structure

- `server/`: Flask backend code
  - `models/`: SQLAlchemy ORM models
  - `routes/`: API endpoints organized by resource
  - `tests/`: Unit tests for the API
  - `utils/`: Utility functions and helpers
- `client/`: Astro/Svelte frontend code
  - `src/components/`: Reusable Svelte components
  - `src/layouts/`: Astro layout templates
  - `src/pages/`: Astro page routes
  - `src/styles/`: CSS and Tailwind configuration
- `infra/`: Terraform infrastructure as code
  - `modules/`: Reusable Terraform modules by service
  - `environments/`: Environment-specific variable files
- `k8s/`: Kubernetes manifests
  - Separate files per resource type
  - Environment-specific overlays
- `.github/workflows/`: GitHub Actions CI/CD pipelines
- `scripts/`: Development and deployment scripts
- `data/`: Database files
- `docs/`: Project documentation
- `README.md`: Project documentation
