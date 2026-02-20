# Tailspin Toys Crowd Funding Development Guidelines

This is a crowdfunding platform for games with a developer theme. The application uses a Flask backend API with SQLAlchemy ORM for database interactions, and an Astro/Svelte frontend with Tailwind CSS for styling.

**IMPORTANT**: All development MUST comply with the [Tailspin Toys Constitution](../.specify/memory/constitution.md), which defines non-negotiable principles for IaC, pipeline security, testing, containerization, and observability. When in doubt, refer to the constitution first.

Please follow these guidelines when contributing:

## Code standards

### Required Before Each Commit

- Run Python tests to ensure backend functionality
- For frontend changes, run builds in the client directory to verify build success and the end-to-end tests, to ensure everything works correctly
- When making API changes, update and run the corresponding tests to ensure everything works correctly
- When updating models, ensure database migrations are included if needed
- When adding new functionality, make sure you update the README
- Make sure all guidance in the Copilot Instructions file is updated with any relevant changes, including to project structure and scripts, and programming guidance

### Code formatting requirements

- When writing Python, you must use type hints for return values and function parameters.

### Python and Flask Patterns

- Use SQLAlchemy models for database interactions
- Use Flask blueprints for organizing routes
- Follow RESTful API design principles

### Svelte and Astro Patterns

- Use Svelte for interactive components
- Follow Svelte's reactive programming model
- Create reusable components when functionality is used in multiple places
- Use Astro for page routing and static content

### Styling

- Use Tailwind CSS classes for styling
- Maintain dark mode theme throughout the application
- Use rounded corners for UI elements
- Follow modern UI/UX principles with clean, accessible interfaces

### GitHub Actions workflows

- Follow good security practices per Constitution Principle II
- MUST use GitHub OIDC authentication to Azure (no service principal secrets)
- MUST explicitly set the workflow permissions block
- MUST validate before applying (terraform plan, az deployment what-if)
- Add comments to document what tasks are being performed
- Include failure notifications and rollback procedures

## Scripts

- Several scripts exist in the `scripts` folder
- Use existing scripts to perform tasks rather than performing them manually
- Existing scripts:
    - `scripts/setup-env.sh`: Performs installation of all Python and Node dependencies
    - `scripts/run-server-tests.sh`: Calls setup-env, then runs all Python tests
    - `scripts/start-app.sh`: Calls setup-env, then starts both backend and frontend servers

### Infrastructure as Code (IaC)

- All Azure infrastructure MUST be defined using Terraform in the `infra/` directory
- Terraform state MUST use remote backend (Azure Storage) with locking
- Follow HashiCorp style guide for Terraform formatting
- Organize infrastructure by modules: networking, compute, data, security, monitoring
- Always run: `terraform validate` → `terraform plan` → review → `terraform apply`
- Never hardcode credentials or resource names; use variables
- Tag all Azure resources: Environment, Project, Owner, CostCenter, ManagedBy=Terraform

### Containerization & Kubernetes

- Docker images defined in `server/Dockerfile` and `client/Dockerfile`
- MUST use multi-stage builds with minimal base images (alpine, slim)
- Test Docker images locally before pushing to Azure Container Registry
- Kubernetes manifests organized under `k8s/` directory
- All K8s resources MUST specify resource requests/limits
- Include liveness and readiness probes for all deployments
- Use Azure managed identity for pod authentication (no secrets)

### Observability

- Emit structured logs in JSON format with correlation IDs
- Integrate with Azure Application Insights for telemetry
- Configure Azure Monitor dashboards for each environment
- Set up alerts: error rate >1%, response time P95 >2s, pod crashes
- Log retention: Logs 30d, Metrics 90d, Traces 7d

#### Logging Implementation

**Backend (Flask):**
- Use `utils.logging_config` module for structured JSON logging
- All logs include: timestamp (ISO 8601 UTC), level, message, service, environment, correlation_id
- Request/response logging middleware automatically tracks all API calls with duration
- Use `get_logger(__name__)` in route modules to get a logger instance
- Log levels: DEBUG (dev only), INFO (normal ops), WARN (degraded), ERROR (failures)
- Include extra context fields in logs via `extra={'correlation_id': g.correlation_id, 'field1': value1, ...}`
- All fields in `extra` dict are automatically added to the JSON output (except standard logging attrs)

**Frontend (Astro Middleware):**
- Middleware in `client/src/middleware.ts` logs all API proxy requests
- Logs structured JSON with correlation IDs for request tracing
- Automatically generates correlation IDs if not provided by client
- Correlation IDs propagate from frontend → middleware → backend for end-to-end tracing
- Logs include: timestamp, level, message, correlation_id, service, environment, method, path, status_code, duration_ms

## Repository Structure

- `server/`: Flask backend code
  - `models/`: SQLAlchemy ORM models
  - `routes/`: API endpoints organized by resource
  - `tests/`: Unit tests for the API
  - `utils/`: Utility functions and helpers
    - `logging_config.py`: Structured JSON logging configuration and middleware
- `client/`: Astro/Svelte frontend code
  - `src/components/`: Reusable Svelte components
  - `src/layouts/`: Astro layout templates
  - `src/pages/`: Astro page routes
  - `src/middleware.ts`: API proxy with structured logging
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
