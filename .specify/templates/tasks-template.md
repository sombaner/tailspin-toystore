---

description: "Task list template for feature implementation"
---

# Tasks: [FEATURE NAME]

**Input**: Design documents from `/specs/[###-feature-name]/`
**Prerequisites**: plan.md (required), spec.md (required for user stories), research.md, data-model.md, contracts/

**Tests**: The examples below include test tasks. Tests are OPTIONAL - only include them if explicitly requested in the feature specification.

**Organization**: Tasks are grouped by user story to enable independent implementation and testing of each story.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g., US1, US2, US3)
- Include exact file paths in descriptions

## Path Conventions

- **Single project**: `src/`, `tests/` at repository root
- **Web app**: `backend/src/`, `frontend/src/`
- **Mobile**: `api/src/`, `ios/src/` or `android/src/`
- Paths shown below assume single project - adjust based on plan.md structure

<!-- 
  ============================================================================
  IMPORTANT: The tasks below are SAMPLE TASKS for illustration purposes only.
  
  The /speckit.tasks command MUST replace these with actual tasks based on:
  - User stories from spec.md (with their priorities P1, P2, P3...)
  - Feature requirements from plan.md
  - Entities from data-model.md
  - Endpoints from contracts/
  
  Tasks MUST be organized by user story so each story can be:
  - Implemented independently
  - Tested independently
  - Delivered as an MVP increment
  
  DO NOT keep these sample tasks in the generated tasks.md file.
  ============================================================================
-->

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Project initialization and basic structure

- [ ] T001 Create project structure per implementation plan
- [ ] T002 Initialize [language] project with [framework] dependencies
- [ ] T003 [P] Configure linting and formatting tools
- [ ] T004 [P] Setup Terraform backend configuration in infra/backend.tf (if IaC required)
- [ ] T005 [P] Configure GitHub Actions OIDC federation with Azure (if deployment required)

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Core infrastructure that MUST be complete before ANY user story can be implemented

**⚠️ CRITICAL**: No user story work can begin until this phase is complete

Examples of foundational tasks (adjust based on your project):

- [ ] T006 Setup database schema and migrations framework
- [ ] T007 [P] Implement authentication/authorization framework
- [ ] T008 [P] Setup API routing and middleware structure
- [ ] T009 Create base models/entities that all stories depend on
- [ ] T010 Configure error handling and structured logging infrastructure (JSON format with correlation IDs)
- [ ] T011 Setup environment configuration management
- [ ] T012 [P] Create Terraform modules for core infrastructure (networking, AKS, ACR) in infra/ (if IaC required)
- [ ] T013 [P] Setup Application Insights and Azure Monitor integration (if observability required)
- [ ] T014 [P] Create Dockerfiles with multi-stage builds (server/Dockerfile, client/Dockerfile) (if containerization required)
- [ ] T015 [P] Create Kubernetes base manifests with resource limits and health checks in k8s/ (if K8s deployment required)

**Checkpoint**: Foundation ready - user story implementation can now begin in parallel

---

## Phase 3: User Story 1 - [Title] (Priority: P1) 🎯 MVP

**Goal**: [Brief description of what this story delivers]

**Independent Test**: [How to verify this story works on its own]

### Tests for User Story 1 (OPTIONAL - only if tests requested) ⚠️

> **NOTE: Write these tests FIRST, ensure they FAIL before implementation**

- [ ] T010 [P] [US1] Contract test for [endpoint] in tests/contract/test_[name].py
- [ ] T011 [P] [US1] Integration test for [user journey] in tests/integration/test_[name].py

### Implementation for User Story 1

- [ ] T012 [P] [US1] Create [Entity1] model in src/models/[entity1].py
- [ ] T013 [P] [US1] Create [Entity2] model in src/models/[entity2].py
- [ ] T014 [US1] Implement [Service] in src/services/[service].py (depends on T012, T013)
- [ ] T015 [US1] Implement [endpoint/feature] in src/[location]/[file].py
- [ ] T016 [US1] Add validation and error handling
- [ ] T017 [US1] Add logging for user story 1 operations

**Checkpoint**: At this point, User Story 1 should be fully functional and testable independently

---

## Phase 4: User Story 2 - [Title] (Priority: P2)

**Goal**: [Brief description of what this story delivers]

**Independent Test**: [How to verify this story works on its own]

### Tests for User Story 2 (OPTIONAL - only if tests requested) ⚠️

- [ ] T018 [P] [US2] Contract test for [endpoint] in tests/contract/test_[name].py
- [ ] T019 [P] [US2] Integration test for [user journey] in tests/integration/test_[name].py

### Implementation for User Story 2

- [ ] T020 [P] [US2] Create [Entity] model in src/models/[entity].py
- [ ] T021 [US2] Implement [Service] in src/services/[service].py
- [ ] T022 [US2] Implement [endpoint/feature] in src/[location]/[file].py
- [ ] T023 [US2] Integrate with User Story 1 components (if needed)

**Checkpoint**: At this point, User Stories 1 AND 2 should both work independently

---

## Phase 5: User Story 3 - [Title] (Priority: P3)

**Goal**: [Brief description of what this story delivers]

**Independent Test**: [How to verify this story works on its own]

### Tests for User Story 3 (OPTIONAL - only if tests requested) ⚠️

- [ ] T024 [P] [US3] Contract test for [endpoint] in tests/contract/test_[name].py
- [ ] T025 [P] [US3] Integration test for [user journey] in tests/integration/test_[name].py

### Implementation for User Story 3

- [ ] T026 [P] [US3] Create [Entity] model in src/models/[entity].py
- [ ] T027 [US3] Implement [Service] in src/services/[service].py
- [ ] T028 [US3] Implement [endpoint/feature] in src/[location]/[file].py

**Checkpoint**: All user stories should now be independently functional

---

[Add more user story phases as needed, following the same pattern]

---

## Phase N: Infrastructure as Code (IaC) *(include if deployment automation required)*

**Purpose**: Define and provision Azure infrastructure using Terraform

**⚠️ PREREQUISITE**: Requires foundational Terraform setup (T012 from Phase 2)

- [ ] TXXX [P] Create Terraform variables file for environment configuration (infra/variables.tf)
- [ ] TXXX [P] Define AKS cluster module with node pools and networking (infra/modules/aks/)
- [ ] TXXX [P] Define Azure Container Registry module with RBAC (infra/modules/acr/)
- [ ] TXXX [P] Define Azure Monitor and Application Insights module (infra/modules/monitoring/)
- [ ] TXXX [P] Define networking module with virtual network and subnets (infra/modules/networking/)
- [ ] TXXX Create main Terraform configuration linking all modules (infra/main.tf)
- [ ] TXXX Create Terraform outputs for deployment values (infra/outputs.tf)
- [ ] TXXX Validate Terraform configuration locally: `terraform validate`
- [ ] TXXX Generate Terraform plan and review: `terraform plan -out=tfplan`
- [ ] TXXX Document infrastructure architecture and module dependencies

**Checkpoint**: IaC defined and validated - ready for pipeline integration

---

## Phase N+1: CI/CD Pipeline Configuration *(include if deployment automation required)*

**Purpose**: Automate deployment using GitHub Actions with security best practices

**⚠️ PREREQUISITE**: Requires IaC completion (Phase N) and containerization setup (T014 from Phase 2)

- [ ] TXXX Create GitHub Actions workflow for infrastructure deployment (.github/workflows/infra-deploy.yml)
  - Use OIDC authentication to Azure (no service principal secrets)
  - Set explicit workflow permissions
  - Run terraform validate → plan → apply workflow
  - Include approval gate for production deployments
- [ ] TXXX [P] Create GitHub Actions workflow for Docker image build and scan (.github/workflows/docker-build.yml)
  - Build multi-stage Docker images for server and client
  - Scan images with Trivy for vulnerabilities
  - Push to Azure Container Registry with semantic version tags
  - Block on HIGH/CRITICAL vulnerabilities
- [ ] TXXX [P] Create GitHub Actions workflow for application deployment (.github/workflows/app-deploy.yml)
  - Deploy Kubernetes manifests to AKS
  - Run smoke tests post-deployment
  - Include automated rollback on health check failure
- [ ] TXXX [P] Create GitHub Actions workflow for IaC security scanning (.github/workflows/iac-scan.yml)
  - Scan Terraform files with Checkov or tfsec
  - Block on security violations
- [ ] TXXX Configure GitHub Environments (dev, staging, prod) with approval requirements
- [ ] TXXX Setup GitHub Secrets for non-sensitive configuration (Azure subscription ID, resource group names)
- [ ] TXXX Document deployment process and rollback procedures in docs/

**Checkpoint**: CI/CD pipelines configured and tested - ready for production deployment

---

## Phase N+2: Polish & Cross-Cutting Concerns

**Purpose**: Improvements that affect multiple user stories

- [ ] TXXX [P] Documentation updates in docs/
- [ ] TXXX Code cleanup and refactoring
- [ ] TXXX Performance optimization across all stories
- [ ] TXXX [P] Additional unit tests (if requested) in tests/unit/
- [ ] TXXX Security hardening
- [ ] TXXX Configure Azure Monitor dashboards for each environment
- [ ] TXXX Setup alert rules for critical metrics (error rate, response time, resource utilization)
- [ ] TXXX Validate infrastructure drift detection (scheduled Terraform plan in CI)
- [ ] TXXX Run quickstart.md validation

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies - can start immediately
- **Foundational (Phase 2)**: Depends on Setup completion - BLOCKS all user stories
- **User Stories (Phase 3+)**: All depend on Foundational phase completion
  - User stories can then proceed in parallel (if staffed)
  - Or sequentially in priority order (P1 → P2 → P3)
- **IaC (Phase N)**: Can proceed in parallel with user story development; depends on foundational IaC setup (T012)
- **CI/CD Pipelines (Phase N+1)**: Depends on IaC completion and containerization setup
- **Polish (Final Phase)**: Depends on all desired user stories and deployment automation being complete

### User Story Dependencies

- **User Story 1 (P1)**: Can start after Foundational (Phase 2) - No dependencies on other stories
- **User Story 2 (P2)**: Can start after Foundational (Phase 2) - May integrate with US1 but should be independently testable
- **User Story 3 (P3)**: Can start after Foundational (Phase 2) - May integrate with US1/US2 but should be independently testable

### Within Each User Story

- Tests (if included) MUST be written and FAIL before implementation
- Models before services
- Services before endpoints
- Core implementation before integration
- Story complete before moving to next priority

### Parallel Opportunities

- All Setup tasks marked [P] can run in parallel
- All Foundational tasks marked [P] can run in parallel (within Phase 2)
- Once Foundational phase completes, all user stories can start in parallel (if team capacity allows)
- All tests for a user story marked [P] can run in parallel
- Models within a story marked [P] can run in parallel
- Different user stories can be worked on in parallel by different team members

---

## Parallel Example: User Story 1

```bash
# Launch all tests for User Story 1 together (if tests requested):
Task: "Contract test for [endpoint] in tests/contract/test_[name].py"
Task: "Integration test for [user journey] in tests/integration/test_[name].py"

# Launch all models for User Story 1 together:
Task: "Create [Entity1] model in src/models/[entity1].py"
Task: "Create [Entity2] model in src/models/[entity2].py"
```

---

## Implementation Strategy

### MVP First (User Story 1 Only)

1. Complete Phase 1: Setup
2. Complete Phase 2: Foundational (CRITICAL - blocks all stories)
3. Complete Phase 3: User Story 1
4. **STOP and VALIDATE**: Test User Story 1 independently
5. Deploy/demo if ready

### Incremental Delivery

1. Complete Setup + Foundational → Foundation ready
2. Add User Story 1 → Test independently → Deploy/Demo (MVP!)
3. Add User Story 2 → Test independently → Deploy/Demo
4. Add User Story 3 → Test independently → Deploy/Demo
5. Each story adds value without breaking previous stories

### Parallel Team Strategy

With multiple developers:

1. Team completes Setup + Foundational together
2. Once Foundational is done:
   - Developer A: User Story 1
   - Developer B: User Story 2
   - Developer C: User Story 3
3. Stories complete and integrate independently

---

## Notes

- [P] tasks = different files, no dependencies
- [Story] label maps task to specific user story for traceability
- Each user story should be independently completable and testable
- Verify tests fail before implementing
- Commit after each task or logical group
- Stop at any checkpoint to validate story independently
- Avoid: vague tasks, same file conflicts, cross-story dependencies that break independence
