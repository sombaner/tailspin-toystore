# Test Review Context

## Repository
- Repo: `sombaner/tailspin-toystore`
- Application type: Crowdfunding platform for games
- Stack:
  - Flask backend
  - SQLAlchemy ORM
  - Astro frontend
  - Svelte components
  - Tailwind CSS
  - Shell scripts / CI / infrastructure support

## Governing Rules
Testing review must follow the Tailspin Toys Constitution and repository instructions:
- Red-Green-Refactor is expected
- Tests should be added before implementation where feasible
- Relevant validation scripts must be run before completion

## Change Under Test
- Feature / bug fix:
- Linked issue / PR:
- Author:
- Risk category:
- Areas touched:
  - API
  - DB/model
  - UI/component
  - Integration
  - E2E
  - CI/CD
  - IaC

## Intended Behavior
- What behavior is expected after the change?
- What should never regress?
- What user-visible outcomes should be verified?

## Test Inventory
### Automated tests added/updated
- Unit tests:
- API tests:
- Model tests:
- Integration tests:
- Frontend component tests:
- E2E tests:
- Pipeline/config tests:
- Manual verification steps:

## Review Focus Areas
### 1. Coverage adequacy
- Do tests cover the happy path?
- Do tests cover key failure paths?
- Do tests cover validation and edge cases?
- Do tests cover regressions for the bug being fixed?

### 2. Test quality
- Are assertions specific and meaningful?
- Do tests verify behavior instead of implementation details?
- Are tests readable and maintainable?
- Is duplicated setup minimized?

### 3. Backend test checks
- Are API status codes and JSON responses asserted?
- Are error responses checked using expected format?
- Are model validations tested?
- Are serialization outputs (`to_dict`) tested where relevant?
- Are database query behaviors and joins tested if logic changed?

### 4. Frontend test checks
- Are loading, error, and empty states tested?
- Are important UI interactions tested?
- Are `data-testid` hooks present where E2E needs them?
- Are API-driven views tested against realistic states?

### 5. End-to-end confidence
- Does the E2E suite validate the main user journey affected?
- Are cross-boundary flows tested (frontend -> API -> persistence)?
- Are flaky or timing-sensitive assertions avoided?

### 6. Constitution / pipeline considerations
- Do tests support secure delivery?
- If infrastructure or pipeline code changed, is that validated appropriately?
- Are observability or deployment-impacting changes covered?

## Gaps / Risk-Based Questions
- What important scenario is still untested?
- What would fail silently if this change broke?
- Are there negative cases missing?
- Are permissions/authentication cases relevant?
- Are migration/backward compatibility cases relevant?

## Reviewer Checklist
- [ ] Tests align with intended behavior
- [ ] Happy path is covered
- [ ] Failure/edge cases are covered
- [ ] Regression risk is addressed
- [ ] Assertions are meaningful
- [ ] Tests are not overly coupled to implementation
- [ ] API contracts are verified
- [ ] UI states are verified
- [ ] E2E coverage exists where user journey risk justifies it
- [ ] Required scripts were run
- [ ] Residual risk is documented

## Execution Evidence
- Backend:
  - Command: `./scripts/run-server-tests.sh`
  - Status:
  - Notes:

- Frontend build:
  - Command: `cd client && npm run build`
  - Status:
  - Notes:

- E2E:
  - Command: `cd client && npm run test:e2e`
  - Status:
  - Notes:

## Test Gaps
- Known missing tests:
- Acceptable rationale:
- Follow-up needed:

## Final Assessment
- Test quality: Strong / Adequate / Weak
- Release confidence: High / Medium / Low
- Reviewer recommendation:
