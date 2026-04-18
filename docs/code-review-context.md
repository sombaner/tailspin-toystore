# Code Review Context

## Repository
- Repo: `sombaner/tailspin-toystore`
- Project: Tailspin Toys Crowd Funding platform
- Backend: Flask + SQLAlchemy
- Frontend: Astro + Svelte + Tailwind CSS
- Other stack areas: Shell scripts, Terraform/HCL, CI/CD automation

## Governing Rules
This review must comply with the Tailspin Toys Constitution:
- IaC standards
- Pipeline security
- Testing requirements
- Containerization requirements
- Observability requirements

If any implementation conflicts with the constitution, the constitution takes precedence.

## Change Summary
- Feature / fix:
- Linked issue / PR:
- Author:
- Review date:
- Relevant environments affected:
  - Backend
  - Frontend
  - Infrastructure
  - CI/CD

## Business / User Intent
- What user or business problem does this change solve?
- What behavior should be improved, added, removed, or protected?

## Scope of Review
### Files / Areas Changed
- Backend routes:
- Backend models:
- Backend utilities:
- Frontend pages:
- Frontend components:
- Middleware / API proxy:
- Tests:
- Scripts:
- Infrastructure / HCL:
- CI/CD workflows:

### Out of Scope
- Explicitly list areas reviewers do not need to re-review deeply

## Architecture Context
### Backend expectations
- Flask routes should use blueprints in `server/routes/`
- New blueprints must be registered in `server/app.py`
- SQLAlchemy models must extend `BaseModel`
- New models must be imported in `server/models/__init__.py`
- Error responses must use:
  `jsonify({"error": "<message>"}), <status_code>`
- Database setup should use `server/utils/database.py`
- Query patterns should follow reusable base-query patterns

### Frontend expectations
- Svelte components use `<script lang="ts">`
- Astro pages use `Layout.astro`
- Dynamic Astro pages should set `export const prerender = false;` where needed
- Frontend API calls should use `/api/...` and rely on middleware proxying
- Tailwind utility classes only, except approved global styling locations
- Dark mode styling conventions should be preserved
- Key UI elements should include `data-testid` where relevant

## Review Focus Areas
### Correctness
- Does the code do what the change claims?
- Are edge cases handled?
- Are error paths implemented correctly?

### Design / Maintainability
- Is the change small and focused?
- Does it preserve existing patterns in the touched files?
- Are reusable abstractions used appropriately?
- Are there any hidden side effects?

### Backend-specific checks
- Are all public functions/classes documented?
- Are all parameters and return values type annotated?
- Are validations implemented with existing validation helpers?
- Does `to_dict()` use camelCase JSON keys?
- Are joins explicit and optional relationships marked appropriately?

### Frontend-specific checks
- Are loading, error, and empty states present?
- Is `onMount` used appropriately for data fetching?
- Are props typed with sensible defaults?
- Does styling match project conventions?
- Are accessibility and interaction states reasonable?

### Security / Compliance
- Does the change expose secrets, unsafe defaults, or trust client input improperly?
- Does it violate constitution requirements around pipelines, IaC, or observability?
- Are auth, input validation, and API boundaries handled safely?

### Operational Readiness
- Are logs, metrics, or observability implications considered?
- Could this impact deployability, migrations, or runtime stability?

## Reviewer Checklist
- [ ] Change purpose is clear
- [ ] Implementation matches repo conventions
- [ ] Constitution requirements are respected
- [ ] Public Python functions/classes have docstrings
- [ ] Python typing is complete
- [ ] Routes/models are placed in correct locations
- [ ] API responses and errors are consistent
- [ ] Frontend uses approved component/page patterns
- [ ] Styling follows Tailwind + dark theme conventions
- [ ] No placeholder/TODO production code introduced
- [ ] Relevant tests were added/updated
- [ ] Required scripts were run
- [ ] Risk level is acceptable

## Validation Evidence
- Backend tests:
  - `./scripts/run-server-tests.sh`
  - Result:
- Frontend build:
  - `cd client && npm run build`
  - Result:
- E2E tests:
  - `cd client && npm run test:e2e`
  - Result:

## Risk Assessment
- Risk level: Low / Medium / High
- Main risks:
- Rollback plan:
- Follow-up work needed:

## Reviewer Notes
- Concerns:
- Suggested changes:
- Questions for author:
- Approval status:
