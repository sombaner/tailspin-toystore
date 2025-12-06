## When generating a PR:

Title – summarize the change (e.g., “Add Product Controller for Toy API”)

## Description – include:

Business/feature context

Behavior changes

Dependencies or migrations

Infrastructure changes (if applicable)

## Ensure:

**Constitutional Compliance** (see [.specify/memory/constitution.md](.specify/memory/constitution.md)):
- Tests written before implementation (Principle III)
- Infrastructure defined in Terraform (Principle I)
- Pipeline uses OIDC auth and explicit permissions (Principle II)
- Structured logging with correlation IDs (Principle V)
- Container security: no HIGH/CRITICAL vulnerabilities (Principle IV)

**Testing**:
Run accessibility tests
Run automation tests 
Run performance test using playwright

API responses consistent with docs or clients

Logging and error paths are covered
npm test passes

Test coverage meets thresholds (Backend ≥80%, Frontend ≥70%)

**Code Quality**:
No formatting/style errors

Visual sanity (if UI): screenshots or video if significant change

**IaC & Deployment** (if infrastructure changes):
Terraform validate and plan reviewed
Kubernetes manifests include resource limits and health checks
Docker images scanned and tested locally

## Optionally:

Include API examples (curl/postman)

Add integration-test notes or Postman collection
