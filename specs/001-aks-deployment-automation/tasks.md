# Tasks: AKS Deployment Automation

**Input**: Design documents from `/specs/001-aks-deployment-automation/`  
**Prerequisites**: plan.md ✅, spec.md ✅, research.md ✅, data-model.md ✅, contracts/ ✅

**Tests**: Post-deployment smoke tests are included as they are specified in the feature requirements (Constitution Principle III).

**Organization**: Tasks are grouped by user story to enable independent implementation and testing of each story.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g., US1, US2, US3)
- Include exact file paths in descriptions

## Path Conventions

Repository follows web application structure:
- Infrastructure: `infra/` (Terraform)
- CI/CD: `.github/workflows/` (GitHub Actions)
- Kubernetes: `k8s/` (manifests)
- Application: `server/` (Flask), `client/` (Astro)
- Testing: `tests/e2e/` (Playwright smoke tests)

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Project initialization and Azure/GitHub configuration

- [ ] T001 Create Terraform backend configuration in infra/backend.tf for Azure Storage state
- [ ] T002 Create Terraform providers configuration in infra/providers.tf with Azure provider and OIDC authentication
- [ ] T003 [P] Create root Terraform main.tf with module orchestration
- [ ] T004 [P] Create Terraform variables.tf for environment inputs (region, resource group, cluster name)
- [ ] T005 [P] Create Terraform outputs.tf for cluster endpoint, ACR URL, workspace IDs
- [ ] T006 [P] Create terraform.tfvars with Central India region and rg-sb-aks-01 resource group
- [ ] T007 [P] Document one-time Azure AD application setup for GitHub OIDC in README or docs/
- [ ] T008 [P] Document Azure Storage account creation for Terraform state in README or docs/
- [ ] T009 Configure GitHub Secrets documentation (AZURE_CLIENT_ID, AZURE_TENANT_ID, AZURE_SUBSCRIPTION_ID)

**Checkpoint**: Terraform foundation and documentation ready

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Core Terraform modules and Kubernetes base configuration

**⚠️ CRITICAL**: No user story work can begin until this phase is complete

- [ ] T010 [P] Create networking module in infra/modules/networking/ with main.tf, variables.tf, outputs.tf
- [ ] T011 [P] Create monitoring module in infra/modules/monitoring/ with Log Analytics and Application Insights resources
- [ ] T012 [P] Create ACR module in infra/modules/acr/ with Premium SKU and RBAC configuration
- [ ] T013 [P] Create RBAC module in infra/modules/rbac/ for AKS to ACR managed identity role assignment
- [ ] T014 Create AKS module in infra/modules/aks/ with automatic cluster configuration, system node pool, managed identity
- [ ] T015 Update Kubernetes namespace manifest k8s/namespace.yaml with tail-spin namespace and labels
- [ ] T016 [P] Update server deployment k8s/server-deployment.yaml with resource limits (cpu: 250m-1000m, memory: 512Mi-1Gi) and health probes
- [ ] T017 [P] Update client deployment k8s/client-deployment.yaml with resource limits (cpu: 100m-500m, memory: 256Mi-512Mi) and health probes
- [ ] T018 Create client LoadBalancer service k8s/client-service.yaml with type LoadBalancer exposing port 80 to targetPort 4321

**Checkpoint**: Foundation ready - user story implementation can now begin in parallel

---

## Phase 3: User Story 1 - Infrastructure Provisioning (Priority: P1) 🎯 MVP

**Goal**: Automatically provision AKS cluster in Azure Central India region with ACR, networking, and monitoring

**Independent Test**: Trigger infrastructure deployment workflow; verify AKS cluster status "Running", kubectl can authenticate, ACR exists, all resources in rg-sb-aks-01

### Implementation for User Story 1

- [ ] T019 [P] [US1] Implement networking module main.tf creating Virtual Network (10.0.0.0/16) and AKS subnet (10.0.1.0/24)
- [ ] T020 [P] [US1] Implement networking module variables.tf with vnet_name, vnet_address_space, aks_subnet_address_prefix
- [ ] T021 [P] [US1] Implement networking module outputs.tf exposing vnet_id, aks_subnet_id, aks_subnet_address_prefix
- [ ] T022 [P] [US1] Implement monitoring module main.tf creating Log Analytics workspace (30-day retention) and Application Insights (web type)
- [ ] T023 [P] [US1] Implement monitoring module variables.tf with workspace_name, appinsights_name, retention_in_days, tags
- [ ] T024 [P] [US1] Implement monitoring module outputs.tf exposing workspace_id, workspace_key, appinsights_instrumentation_key, appinsights_connection_string
- [ ] T025 [P] [US1] Implement ACR module main.tf creating Azure Container Registry with Premium SKU, admin disabled
- [ ] T026 [P] [US1] Implement ACR module variables.tf with acr_name, sku, admin_enabled, location, resource_group_name, tags
- [ ] T027 [P] [US1] Implement ACR module outputs.tf exposing acr_id, acr_name, acr_login_server
- [ ] T028 [US1] Implement AKS module main.tf creating AKS automatic cluster with public API server, system node pool (1-3 nodes, auto-scaling), managed identity, OMS agent integration
- [ ] T029 [US1] Implement AKS module variables.tf with cluster_name, dns_prefix, node_pool_vm_size, node_pool_min_count, node_pool_max_count, subnet_id, log_analytics_workspace_id, tags
- [ ] T030 [US1] Implement AKS module outputs.tf exposing cluster_id, cluster_name, cluster_fqdn, kubelet_identity_object_id, kube_config (sensitive), cluster_endpoint
- [ ] T031 [US1] Implement RBAC module main.tf assigning AcrPull role to AKS kubelet managed identity on ACR scope
- [ ] T032 [US1] Implement RBAC module variables.tf with aks_cluster_name, acr_id, resource_group_name
- [ ] T033 [US1] Update root infra/main.tf to call all modules with correct dependencies (networking → monitoring/ACR/AKS → RBAC)
- [ ] T034 [US1] Add resource tagging to all modules (Environment, Project=Tailspin, ManagedBy=Terraform, Owner, CostCenter)
- [ ] T035 [US1] Create GitHub Actions workflow .github/workflows/infra-deploy.yml with OIDC Azure login, Terraform init/validate/plan/apply, explicit permissions (id-token: write, contents: read)
- [ ] T036 [US1] Add Terraform plan review step and manual approval gate in infra-deploy.yml workflow
- [ ] T037 [US1] Add workflow outputs for cluster name and ACR login server in infra-deploy.yml
- [ ] T038 [US1] Add inline comments documenting workflow steps in infra-deploy.yml per Constitution Principle II
- [ ] T039 [US1] Validate Terraform configuration locally: terraform init && terraform validate
- [ ] T040 [US1] Generate and review Terraform plan: terraform plan -out=tfplan

**Checkpoint**: At this point, User Story 1 should be fully functional - infrastructure can be provisioned via workflow and verified accessible

---

## Phase 4: User Story 2 - Container Image Management (Priority: P2)

**Goal**: Automatically build, scan, and push Docker images for Tailspin server and client to ACR with semantic versioning

**Independent Test**: Trigger container build workflow; verify both server and client images exist in ACR with semantic version and commit SHA tags, Trivy scan passes with no HIGH/CRITICAL vulnerabilities

### Implementation for User Story 2

- [ ] T041 [P] [US2] Create GitHub Actions workflow .github/workflows/docker-build.yml for container builds
- [ ] T042 [P] [US2] Add workflow triggers (push to server/**, client/**, workflow_dispatch, infra-deploy completion) in docker-build.yml
- [ ] T043 [P] [US2] Set explicit workflow permissions (contents: read, security-events: write, id-token: write) in docker-build.yml
- [ ] T044 [P] [US2] Create build-server job in docker-build.yml: checkout, Azure OIDC login, build server Docker image with commit SHA tag
- [ ] T045 [P] [US2] Add Trivy vulnerability scan step in build-server job with SARIF output, severity CRITICAL,HIGH, exit-code 1 (fail on vulnerabilities)
- [ ] T046 [P] [US2] Upload Trivy scan results to GitHub Security tab using codeql-action/upload-sarif in build-server job
- [ ] T047 [P] [US2] Add ACR login and push steps in build-server job: az acr login, docker tag with semantic version, docker push to ACR
- [ ] T048 [P] [US2] Create build-client job in docker-build.yml: checkout, Azure OIDC login, build client Docker image with commit SHA tag
- [ ] T049 [P] [US2] Add Trivy vulnerability scan step in build-client job with SARIF output, severity CRITICAL,HIGH, exit-code 1
- [ ] T050 [P] [US2] Upload Trivy scan results to GitHub Security tab in build-client job
- [ ] T051 [P] [US2] Add ACR login and push steps in build-client job: az acr login, docker tag with semantic version, docker push to ACR
- [ ] T052 [US2] Add workflow summary step displaying image tags and ACR repository URLs for both images
- [ ] T053 [US2] Add inline comments documenting scan thresholds and security requirements per Constitution Principle II
- [ ] T054 [US2] Verify existing server/Dockerfile uses multi-stage build with python:3.11-slim base image
- [ ] T055 [US2] Verify existing client/Dockerfile uses multi-stage build with node:20-alpine base image
- [ ] T056 [US2] Test Docker image builds locally: docker build -t tailspin-server:test ./server && docker build -t tailspin-client:test ./client
- [ ] T057 [US2] Test Trivy scans locally: trivy image tailspin-server:test --severity HIGH,CRITICAL && trivy image tailspin-client:test --severity HIGH,CRITICAL

**Checkpoint**: At this point, User Stories 1 AND 2 should both work independently - infrastructure exists and container images are built, scanned, and stored in ACR

---

## Phase 5: User Story 3 - Application Deployment to AKS (Priority: P3)

**Goal**: Deploy Tailspin server and client applications to AKS "tail-spin" namespace with external client access via LoadBalancer

**Independent Test**: Trigger application deployment workflow; verify pods running in tail-spin namespace, health checks passing, client accessible via external LoadBalancer IP, smoke tests pass

### Tests for User Story 3

> **NOTE: Write these tests FIRST, ensure they FAIL before deployment implementation**

- [ ] T058 [P] [US3] Create post-deployment smoke test tests/e2e/deployment-smoke.spec.ts for client external IP accessibility
- [ ] T059 [P] [US3] Add smoke test for server health endpoint (/health) via internal cluster IP
- [ ] T060 [P] [US3] Add smoke test for client-to-server API connectivity through Kubernetes service

### Implementation for User Story 3

- [ ] T061 [P] [US3] Create GitHub Actions workflow .github/workflows/app-deploy.yml for Kubernetes deployment
- [ ] T062 [P] [US3] Add workflow triggers (workflow_run on docker-build completion with success condition, workflow_dispatch) in app-deploy.yml
- [ ] T063 [P] [US3] Set explicit workflow permissions (contents: read, id-token: write) in app-deploy.yml
- [ ] T064 [US3] Add deploy job in app-deploy.yml: checkout, Azure OIDC login, get AKS credentials (az aks get-credentials)
- [ ] T065 [US3] Add dynamic image tag substitution step in deploy job: update k8s manifests with latest ACR image tags from docker-build workflow outputs
- [ ] T066 [US3] Add kubectl apply steps in deploy job: apply namespace, server deployment, client deployment, client LoadBalancer service
- [ ] T067 [US3] Add rollout status wait steps in deploy job: kubectl rollout status for both server and client deployments (timeout 300s)
- [ ] T068 [US3] Add external IP wait step in deploy job: wait for LoadBalancer service EXTERNAL-IP (kubectl get svc with --watch until IP assigned)
- [ ] T069 [US3] Add smoke test execution step in deploy job: run Playwright smoke tests from tests/e2e/deployment-smoke.spec.ts
- [ ] T070 [US3] Add rollback step in deploy job with if: failure() condition: kubectl rollout undo for both deployments if smoke tests fail
- [ ] T071 [US3] Add post-rollback verification step: kubectl rollout status after rollback to confirm successful recovery
- [ ] T072 [US3] Add workflow outputs for external IP address and deployment status
- [ ] T073 [US3] Add inline comments documenting rollback logic and health check validation per Constitution Principle II
- [ ] T074 [US3] Configure workflow timeout (30 minutes) to prevent hung deployments
- [ ] T075 [US3] Add failure notification step (GitHub Issue creation or comment) for deployment failures

**Checkpoint**: All user stories should now be independently functional - complete end-to-end automation from infrastructure → containers → deployed application

---

## Phase 6: Polish & Cross-Cutting Concerns

**Purpose**: Improvements, monitoring, and validation across all user stories

- [ ] T076 [P] Update README.md with deployment automation overview, prerequisites, and quick start guide
- [ ] T077 [P] Create docs/deployment-guide.md referencing quickstart.md with detailed operational procedures
- [ ] T078 [P] Create docs/troubleshooting.md with common issues and resolutions from quickstart.md
- [ ] T079 [P] Create docs/rollback-procedures.md with manual rollback steps for Kubernetes and Terraform
- [ ] T080 [P] Validate infra-deploy.yml workflow with terraform plan (no actual apply) on feature branch
- [ ] T081 [P] Validate docker-build.yml workflow with test image builds and Trivy scans
- [ ] T082 [P] Validate app-deploy.yml workflow with dry-run deployment (kubectl apply --dry-run=server)
- [ ] T083 [P] Add Azure Monitor dashboard configuration in infra/modules/monitoring/ for service health, request rate, error rate
- [ ] T084 [P] Configure alert rules in monitoring module: error rate >1% (5min), response time P95 >2s (5min), pod crash loops
- [ ] T085 [P] Add infrastructure drift detection workflow .github/workflows/drift-check.yml with scheduled Terraform plan (no apply)
- [ ] T086 [P] Add IaC security scanning workflow .github/workflows/iac-scan.yml with Checkov or tfsec scanning Terraform files
- [ ] T087 [P] Verify structured logging in GitHub Actions workflows (JSON format output where applicable)
- [ ] T088 [P] Add workflow correlation IDs for tracing deployment operations across workflows
- [ ] T089 Validate Constitution compliance checklist in plan.md against implemented code
- [ ] T090 Run complete quickstart.md walkthrough as end-to-end validation
- [ ] T091 Document multi-environment expansion path (dev/staging/prod) for Phase 2 future work
- [ ] T092 Create architectural diagram showing Azure resources and deployment flow in docs/architecture.md

**Checkpoint**: Feature complete with documentation, monitoring, and operational procedures

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies - can start immediately
- **Foundational (Phase 2)**: Depends on Setup completion - BLOCKS all user stories
- **User Story 1 - Infrastructure Provisioning (Phase 3)**: Depends on Foundational phase completion (Terraform modules defined)
- **User Story 2 - Container Image Management (Phase 4)**: Depends on Foundational completion; can proceed in parallel with US1 once ACR module exists (T012)
- **User Story 3 - Application Deployment (Phase 5)**: Depends on US1 (AKS cluster exists) AND US2 (container images in ACR) completion
- **Polish (Phase 6)**: Depends on all user stories being complete

### User Story Dependencies

- **User Story 1 (P1)**: Can start after Foundational (Phase 2) - No dependencies on other stories
- **User Story 2 (P2)**: Can start after Foundational (Phase 2) - Minimal dependency on US1 (ACR must exist, provisioned by US1 or separately)
- **User Story 3 (P3)**: DEPENDS on US1 (cluster exists) AND US2 (images available) - Final integration story

### Within Each User Story

- **US1**: Terraform modules can be implemented in parallel ([P] tasks T019-T027), then orchestrated in main.tf (T033), finally workflow (T035-T040)
- **US2**: Both build jobs (server and client) are independent and can run in parallel within the workflow
- **US3**: Tests written first (T058-T060), then workflow implementation (T061-T075)

### Parallel Opportunities

- All Setup tasks (T001-T009) marked [P] can run in parallel
- All Foundational module tasks (T010-T013, T016-T018) marked [P] can run in parallel (T014 depends on networking)
- Within US1: All module implementations (T019-T027) marked [P] can run in parallel
- Within US2: All workflow job tasks marked [P] can run in parallel
- Within US3: All test tasks (T058-T060) marked [P] can run in parallel
- All Polish documentation and validation tasks (T076-T088) marked [P] can run in parallel

---

## Parallel Example: User Story 1

```bash
# Launch all Terraform modules for User Story 1 together:
Task: "Implement networking module main.tf" (infra/modules/networking/main.tf)
Task: "Implement monitoring module main.tf" (infra/modules/monitoring/main.tf)
Task: "Implement ACR module main.tf" (infra/modules/acr/main.tf)

# Each module has variables.tf and outputs.tf:
Task: "Implement networking module variables.tf" (infra/modules/networking/variables.tf)
Task: "Implement monitoring module variables.tf" (infra/modules/monitoring/variables.tf)
Task: "Implement ACR module variables.tf" (infra/modules/acr/variables.tf)

Task: "Implement networking module outputs.tf" (infra/modules/networking/outputs.tf)
Task: "Implement monitoring module outputs.tf" (infra/modules/monitoring/outputs.tf)
Task: "Implement ACR module outputs.tf" (infra/modules/acr/outputs.tf)
```

---

## Implementation Strategy

### MVP First (User Story 1 Only)

1. Complete Phase 1: Setup → Terraform foundation ready
2. Complete Phase 2: Foundational → Terraform modules and K8s base manifests defined
3. Complete Phase 3: User Story 1 → Infrastructure provisioning automated
4. **STOP and VALIDATE**: Trigger infra-deploy workflow, verify AKS cluster accessible
5. **MVP DELIVERED**: Infrastructure automation working, ready for container deployment

### Incremental Delivery

1. Complete Setup + Foundational → Foundation ready
2. Add User Story 1 → Test independently → Deploy infrastructure (MVP!)
3. Add User Story 2 → Test independently → Build and store container images
4. Add User Story 3 → Test independently → Deploy applications to AKS → **FULL AUTOMATION COMPLETE**
5. Add Polish → Documentation, monitoring, operational excellence

### Parallel Team Strategy

With multiple developers:

1. Team completes Setup + Foundational together (critical path)
2. Once Foundational is done:
   - **Developer A**: User Story 1 (Infrastructure provisioning)
   - **Developer B**: User Story 2 (Container builds) - starts after ACR module ready
   - **Developer C**: Polish documentation tasks (can start early)
3. **All developers converge on User Story 3** (final integration) after US1 and US2 complete
4. Final validation and documentation polish together

---

## Task Count Summary

- **Phase 1 (Setup)**: 9 tasks
- **Phase 2 (Foundational)**: 9 tasks
- **Phase 3 (User Story 1)**: 22 tasks
- **Phase 4 (User Story 2)**: 17 tasks
- **Phase 5 (User Story 3)**: 18 tasks (including 3 smoke tests)
- **Phase 6 (Polish)**: 17 tasks
- **Total**: 92 tasks

**Parallel Opportunities**: 48 tasks marked [P] (52% parallelizable)

**Story Distribution**:
- User Story 1: 22 tasks (Infrastructure Provisioning)
- User Story 2: 17 tasks (Container Image Management)
- User Story 3: 18 tasks (Application Deployment)

**MVP Scope**: Phase 1 + Phase 2 + Phase 3 (40 tasks) delivers infrastructure automation

**Estimated Implementation Time**:
- MVP (US1): 12-16 hours
- US2 addition: 6-8 hours
- US3 addition: 8-10 hours
- Polish: 4-6 hours
- **Total**: 30-40 hours (4-5 sprints at 8 hours/sprint)

---

## Notes

- [P] tasks = different files, no dependencies within the same phase
- [Story] label maps task to specific user story for traceability (US1, US2, US3)
- Each user story should be independently completable and testable
- Tests for US3 (smoke tests) must fail before deployment implementation
- Commit after each task or logical group of related tasks
- Stop at each checkpoint to validate story independently
- Constitution compliance verified throughout: IaC modules, OIDC auth, resource limits, monitoring, security scanning
- All workflows include inline comments per Constitution Principle II
- All Kubernetes manifests specify resource limits per Constitution Principle IV
- Vulnerability scanning blocks deployment per Constitution security standards
