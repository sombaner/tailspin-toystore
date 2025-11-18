# Tailspin Toystore - Comprehensive Documentation

## Table of Contents
- [Overview](#overview)
- [Technology Stack](#technology-stack)
- [Features and Capabilities](#features-and-capabilities)
- [Prerequisites](#prerequisites)
- [Getting Started](#getting-started)
- [Running the Application](#running-the-application)
- [Docker Containerization](#docker-containerization)
- [Testing](#testing)
- [CI/CD and GitHub Actions](#cicd-and-github-actions)
- [Deployment](#deployment)
- [GitHub Codespaces](#github-codespaces)
- [Project Structure](#project-structure)
- [Development Guidelines](#development-guidelines)
- [Additional Resources](#additional-resources)
- [License and Support](#license-and-support)

---

## Overview

**Tailspin Toystore** is a crowdfunding platform for board games with a developer theme. This application serves as a hands-on workshop project to explore GitHub Copilot Agent Mode and related AI-assisted development features in Visual Studio Code.

The application demonstrates a modern full-stack web architecture with:
- A RESTful API backend built with Flask
- A dynamic frontend built with Astro and Svelte
- SQLAlchemy ORM for database management
- Tailwind CSS for modern, responsive styling
- Comprehensive testing at multiple levels
- CI/CD pipelines using GitHub Actions
- Container-based deployment to Azure Kubernetes Service (AKS)

---

## Technology Stack

### Backend
- **[Flask](https://flask.palletsprojects.com/en/stable/)** - Python web framework for the REST API
- **[SQLAlchemy](https://www.sqlalchemy.org/)** - ORM for database interactions
- **Flask-CORS** - Cross-Origin Resource Sharing support
- **Python 3.13** - Programming language

### Frontend
- **[Astro](https://astro.build/)** - Modern static site builder with SSR support
- **[Svelte](https://svelte.dev/)** - Reactive UI framework for dynamic components
- **[Tailwind CSS](https://tailwindcss.com/)** - Utility-first CSS framework
- **TypeScript** - Type-safe JavaScript
- **Node.js 22** - JavaScript runtime

### Testing
- **unittest** - Python unit testing framework
- **[Playwright](https://playwright.dev/)** - End-to-end testing framework

### DevOps & Infrastructure
- **Docker** - Container runtime
- **Kubernetes** - Container orchestration
- **Azure Kubernetes Service (AKS)** - Managed Kubernetes platform
- **GitHub Actions** - CI/CD automation
- **GitHub Container Registry (GHCR)** - Docker image registry

---

## Features and Capabilities

### Application Features
- Browse crowdfunding campaigns for board games
- View detailed game information including categories and publishers
- Filter games by category and publisher
- Responsive dark-mode UI with modern design
- RESTful API for game data management

### GitHub Actions Workflows

#### Continuous Integration
- **Run Tests** (`run-tests.yml`) - Executes backend and frontend tests on pull requests and pushes to main
  - Backend unit tests using Python unittest
  - Frontend E2E tests using Playwright
  - Automatic test report uploads on failure

#### Continuous Deployment
- **Server Deploy to AKS** (`server-deploy-aks.yml`) - Builds and deploys Flask backend to Azure Kubernetes Service
  - Triggers on changes to `server/**` or `k8s/server-deployment.yaml`
  - Builds Docker image and pushes to GHCR
  - Deploys to AKS cluster using Azure CLI

- **Client Deploy to AKS** (`client-deploy-aks.yml`) - Builds and deploys Astro frontend to Azure Kubernetes Service
  - Triggers on changes to `client/**` or `k8s/client-deployment.yaml`
  - Builds optimized production bundle
  - Deploys to AKS cluster

#### Quality and Research
- **E2E Tests** (`ci-e2e.yml`) - Comprehensive end-to-end integration tests
- **Daily Test Improver** - Automated test improvement suggestions
- **Weekly Research** - Automated research on project improvements
- **Update Documentation** - Automated documentation updates

### Security Features
- GitHub Dependabot for dependency updates
- Explicit workflow permissions following security best practices
- Container image scanning
- Secrets management through Azure Key Vault integration

---

## Prerequisites

Before running the application locally, ensure you have:

- **Python 3.13 or higher** installed
- **Node.js 22 or higher** and npm installed
- **Git** for version control
- **Docker** (optional, for containerized deployment)
- **Azure CLI** (optional, for AKS deployment)

For the full workshop experience, you'll also need:
- **Visual Studio Code** with GitHub Copilot extensions
- **GitHub Copilot subscription** (Individual, Business, or Enterprise)

---

## Getting Started

### Clone the Repository

```bash
git clone https://github.com/sombaner/tailspin-toystore.git
cd tailspin-toystore
```

### Setup Development Environment

The repository includes a setup script that installs all necessary dependencies:

```bash
./scripts/setup-env.sh
```

This script will:
1. Create and activate a Python virtual environment
2. Install Python dependencies from `server/requirements.txt`
3. Install Node.js dependencies from `client/package.json`
4. Verify the installation

---

## Running the Application

### Quick Start (Recommended)

Use the provided startup script to launch both backend and frontend servers:

```bash
./scripts/start-app.sh
```

This will:
1. Run the environment setup
2. Start the Flask backend on `http://localhost:5100`
3. Start the Astro frontend on `http://localhost:4321`

Navigate to **http://localhost:4321** in your browser to view the application.

### Manual Setup

#### Start Backend Server

```bash
# Activate virtual environment
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Navigate to server directory
cd server

# Run Flask application
python app.py
```

The API will be available at `http://localhost:5100`.

#### Start Frontend Server

In a new terminal:

```bash
# Navigate to client directory
cd client

# Install dependencies (if not already done)
npm install

# Start development server
npm run dev
```

The frontend will be available at `http://localhost:4321`.

---

## Docker Containerization

### Backend Container

Build the server Docker image:

```bash
docker build -f server/Dockerfile -t tailspin-server:latest .
```

Run the server container:

```bash
docker run -p 5100:5100 tailspin-server:latest
```

### Frontend Container

Build the client Docker image:

```bash
cd client
docker build -t tailspin-client:latest .
```

Run the client container:

```bash
docker run -p 4321:4321 tailspin-client:latest
```

### Docker Compose (Optional)

For running both services together, you can create a `docker-compose.yml`:

```yaml
version: '3.8'
services:
  backend:
    build:
      context: .
      dockerfile: server/Dockerfile
    ports:
      - "5100:5100"
    
  frontend:
    build:
      context: ./client
      dockerfile: Dockerfile
    ports:
      - "4321:4321"
    environment:
      - API_URL=http://backend:5100
    depends_on:
      - backend
```

---

## Testing

The project includes comprehensive testing at multiple levels to ensure code quality and functionality.

### Backend Unit Tests

Test the Flask API endpoints:

```bash
./scripts/run-server-tests.sh
```

Or manually:

```bash
source venv/bin/activate
cd server
python -m unittest discover tests
```

The backend tests cover:
- API endpoint functionality
- Database operations
- Data validation
- Error handling

### Frontend E2E Tests

Test the Astro/Svelte UI components:

```bash
cd client
npm run test:e2e
```

The frontend tests validate:
- Component rendering
- User interactions
- Navigation flows
- UI responsiveness

### Comprehensive End-to-End Tests

Full-stack integration tests that validate the entire application:

```bash
cd tests/e2e
npm install
npm test
```

These E2E tests:
- Validate API endpoints return expected data
- Test UI components consume and display API data correctly
- Simulate complete user workflows (browsing games, viewing details)
- Ensure error handling works across the full stack
- Test performance and data consistency
- Automatically spin up both backend and frontend servers

### Load Testing

Performance testing with Playwright:

```bash
cd client
npm run test:ui:load
```

---

## CI/CD and GitHub Actions

### Continuous Integration Pipeline

The `run-tests.yml` workflow executes on:
- Pull requests to the `main` branch
- Pushes to the `main` branch
- Manual workflow dispatch

**Jobs:**
1. **backend-tests**
   - Sets up Python 3.13 environment (matching local development)
   - Installs dependencies using the setup script
   - Runs Flask unit tests
   - Fails the build if tests don't pass

2. **frontend-tests**
   - Sets up Node.js 22 environment
   - Installs npm dependencies
   - Installs Playwright browsers
   - Runs E2E tests with Playwright
   - Uploads test reports on failure (retained for 30 days)

### Continuous Deployment Pipeline

#### Server Deployment (`server-deploy-aks.yml`)

Triggers on:
- Changes to `server/**` directory
- Changes to `k8s/server-deployment.yaml`
- Manual workflow dispatch

**Workflow Steps:**
1. Build Docker image from `server/Dockerfile`
2. Push image to GitHub Container Registry (GHCR)
3. Authenticate with Azure using OIDC
4. Deploy to Azure Kubernetes Service
5. Apply Kubernetes manifests
6. Verify deployment health

#### Client Deployment (`client-deploy-aks.yml`)

Triggers on:
- Changes to `client/**` directory
- Changes to `k8s/client-deployment.yaml`
- Manual workflow dispatch

**Workflow Steps:**
1. Build optimized production bundle
2. Create Docker image
3. Push to GHCR
4. Deploy to AKS cluster
5. Update Kubernetes resources

### Security Best Practices

All workflows follow security guidelines:
- **Explicit permissions** - Each job declares minimum required permissions
- **OIDC authentication** - Passwordless Azure authentication
- **Secrets management** - Sensitive data stored in GitHub Secrets or Azure Key Vault
- **Dependency scanning** - Dependabot monitors for vulnerabilities

---

## Deployment

### Kubernetes Deployment

The application is designed for deployment to Azure Kubernetes Service (AKS).

#### Prerequisites
- Azure subscription
- AKS cluster provisioned
- Azure CLI installed and configured
- kubectl installed

#### Kubernetes Resources

The `k8s/` directory contains:

1. **namespace.yaml** - Creates the `toyspin` namespace
2. **server-deployment.yaml** - Backend deployment and service
3. **client-deployment.yaml** - Frontend deployment and service

#### Manual Deployment

```bash
# Set kubectl context to your AKS cluster
az aks get-credentials --resource-group <resource-group> --name <cluster-name>

# Create namespace
kubectl apply -f k8s/namespace.yaml

# Deploy backend
kubectl apply -f k8s/server-deployment.yaml

# Deploy frontend
kubectl apply -f k8s/client-deployment.yaml

# Verify deployments
kubectl get pods -n toyspin
kubectl get services -n toyspin
```

#### Automated Deployment

Deployments are automated through GitHub Actions workflows when changes are pushed to the `main` branch. The workflows:
1. Build Docker images
2. Push to GitHub Container Registry
3. Authenticate with Azure
4. Apply Kubernetes manifests
5. Verify deployment health

---

## GitHub Codespaces

The repository is configured for GitHub Codespaces, providing a pre-configured cloud development environment.

### Features

The Codespaces environment includes:
- **Base Image:** `mcr.microsoft.com/devcontainers/universal:latest`
- **Python 3.13** with pip
- **Node.js 22** with npm
- **.NET 9.0** SDK
- **Git** and GitHub CLI

### VS Code Extensions

Pre-installed extensions:
- GitHub Copilot
- GitHub Copilot Chat
- Python (Pylance)
- Svelte for VS Code
- Astro

### Getting Started with Codespaces

1. Navigate to the repository on GitHub
2. Click the **Code** button
3. Select **Codespaces** tab
4. Click **Create codespace on main**

The environment will:
- Clone the repository
- Run `./scripts/setup-env.sh` automatically (via `postCreateCommand`)
- Install all dependencies
- Be ready for development in minutes

### Running in Codespaces

Once the Codespace is ready:

```bash
# Start the application
./scripts/start-app.sh
```

Codespaces will automatically forward ports 4321 and 5100, allowing you to access the application through your browser.

---

## Project Structure

```
tailspin-toystore/
├── .devcontainer/          # Codespaces and Dev Container configuration
│   └── devcontainer.json
├── .github/
│   ├── agents/            # Custom agent configurations
│   ├── instructions/      # Repository-specific instructions
│   ├── workflows/         # GitHub Actions CI/CD pipelines
│   ├── copilot-instructions.md
│   └── dependabot.yml
├── .vscode/               # VS Code workspace settings
├── client/                # Astro/Svelte frontend
│   ├── e2e-tests/         # Frontend E2E tests
│   ├── public/            # Static assets
│   ├── src/
│   │   ├── components/    # Reusable Svelte components
│   │   ├── layouts/       # Astro layout templates
│   │   ├── pages/         # Astro page routes
│   │   └── styles/        # CSS and Tailwind configuration
│   ├── astro.config.mjs   # Astro configuration
│   ├── Dockerfile         # Frontend container image
│   ├── package.json       # Node.js dependencies
│   └── playwright.config.ts
├── data/                  # Database files
│   └── tailspin-toys.db   # SQLite database
├── docs/                  # Workshop documentation
│   ├── 0-prereqs.md
│   ├── 1-copilot-coding-agent.md
│   ├── 2-mcp.md
│   ├── 3-custom-instructions.md
│   ├── 4-copilot-agent-mode-vscode.md
│   ├── 5-reviewing-coding-agent.md
│   ├── README.md          # Workshop overview
│   └── images/
├── k8s/                   # Kubernetes manifests
│   ├── namespace.yaml
│   ├── server-deployment.yaml
│   └── client-deployment.yaml
├── loadtest/              # Load testing configuration
├── scripts/               # Development scripts
│   ├── setup-env.sh       # Environment setup
│   ├── run-server-tests.sh # Backend test runner
│   └── start-app.sh       # Application launcher
├── server/                # Flask backend
│   ├── models/            # SQLAlchemy ORM models
│   │   ├── base.py
│   │   ├── category.py
│   │   ├── game.py
│   │   └── publisher.py
│   ├── routes/            # API endpoints
│   │   ├── debug.py       # Debug endpoints
│   │   ├── games.py       # Game CRUD operations
│   │   └── publishers.py  # Publisher operations
│   ├── tests/             # Backend unit tests
│   ├── utils/             # Utility functions
│   │   └── database.py    # Database initialization
│   ├── app.py             # Flask application entry point
│   ├── Dockerfile         # Backend container image
│   └── requirements.txt   # Python dependencies
├── tests/
│   └── e2e/               # Full-stack integration tests
├── venv/                  # Python virtual environment
├── .gitignore
├── AGENTS.md              # Agent usage documentation
├── CODE_OF_CONDUCT.md     # Community guidelines
├── CONTRIBUTING.md        # Contribution guidelines
├── LICENSE                # MIT License
├── README.md              # Project overview
├── SECURITY.md            # Security policy
└── SUPPORT.md             # Support information
```

### Key Directories Explained

#### `/server` - Backend API
- **models/** - SQLAlchemy ORM models define the database schema
- **routes/** - Flask blueprints organize API endpoints by resource
- **tests/** - Unit tests for API functionality
- **utils/** - Helper functions and database initialization

#### `/client` - Frontend Application
- **src/components/** - Reusable Svelte components for UI elements
- **src/layouts/** - Astro layout templates for page structure
- **src/pages/** - Astro file-based routing (each file = a route)
- **src/styles/** - Tailwind CSS configuration and custom styles

#### `/docs` - Workshop Materials
- Step-by-step guides for learning GitHub Copilot features
- Instructions for hands-on exercises
- Screenshots and examples

#### `/k8s` - Kubernetes Configuration
- Deployment manifests for AKS
- Service definitions
- Namespace configuration

#### `/scripts` - Automation
- Environment setup
- Test execution
- Application startup

---

## Development Guidelines

### Code Standards

#### Required Before Each Commit
- Run Python tests to ensure backend functionality
- For frontend changes, run builds and E2E tests
- When making API changes, update corresponding tests
- When updating models, ensure database migrations are included
- When adding new functionality, update the README
- Update Copilot Instructions with relevant changes

#### Python and Flask Patterns
- **Use type hints** for all function parameters and return values
- Use SQLAlchemy models for database interactions
- Use Flask blueprints for organizing routes
- Follow RESTful API design principles

Example:
```python
from flask import Blueprint, jsonify
from typing import Dict, Any

games_bp = Blueprint('games', __name__)

@games_bp.route('/api/games/<int:game_id>')
def get_game(game_id: int) -> Dict[str, Any]:
    # Implementation
    return jsonify({"id": game_id})
```

#### Svelte and Astro Patterns
- Use Svelte for interactive components
- Follow Svelte's reactive programming model
- Create reusable components for shared functionality
- Use Astro for page routing and static content

#### Styling Guidelines
- Use Tailwind CSS classes for styling
- Maintain dark mode theme throughout
- Use rounded corners for UI elements
- Follow modern UI/UX principles with clean, accessible interfaces

#### Testing Guidelines
- Create tests using the `unittest` module
- Include tests for both success and error cases
- Use in-memory SQLite for testing
- Utilize setup/teardown functions
- Ensure database is properly closed with `db.engine.dispose()`

### API Endpoint Creation

When creating new endpoints:

1. **Create the route** in the appropriate blueprint file
2. **Create a centralized function** for data access
3. **Write comprehensive tests** covering success and error cases
4. **Update documentation** to reflect new endpoints
5. **Register blueprints** in `server/app.py`

### GitHub Actions Workflow Guidelines
- Follow security best practices
- Explicitly set workflow permissions
- Add comments to document tasks
- Test workflows in feature branches

---

## Additional Resources

### Workshop Guides

The `/docs` folder contains detailed workshop materials:

1. **[Prerequisites](./docs/0-prereqs.md)** - Environment setup
2. **[Copilot Coding Agent](./docs/1-copilot-coding-agent.md)** - Assign issues to Copilot
3. **[Model Context Protocol](./docs/2-mcp.md)** - External service integration
4. **[Custom Instructions](./docs/3-custom-instructions.md)** - Provide context to Copilot
5. **[Agent Mode in VS Code](./docs/4-copilot-agent-mode-vscode.md)** - Site-wide updates
6. **[Reviewing Copilot's Work](./docs/5-reviewing-coding-agent.md)** - Quality assurance

### Community Guidelines

- **[Contributing](./CONTRIBUTING.md)** - How to contribute to the project
- **[Code of Conduct](./CODE_OF_CONDUCT.md)** - Community standards
- **[Security Policy](./SECURITY.md)** - Reporting security issues
- **[Support](./SUPPORT.md)** - Getting help

### External Documentation

- [Flask Documentation](https://flask.palletsprojects.com/)
- [SQLAlchemy Documentation](https://docs.sqlalchemy.org/)
- [Astro Documentation](https://docs.astro.build/)
- [Svelte Documentation](https://svelte.dev/docs)
- [Tailwind CSS Documentation](https://tailwindcss.com/docs)
- [Playwright Documentation](https://playwright.dev/docs/intro)
- [Azure Kubernetes Service Documentation](https://learn.microsoft.com/en-us/azure/aks/)

---

## License and Support

### License

This project is licensed under the **MIT License**. This is a permissive license that allows you to:
- Use the software for any purpose
- Modify the software
- Distribute the software
- Use it in proprietary software

See the [LICENSE](./LICENSE) file for full terms.

### Maintainers

You can find the list of maintainers in [.github/CODEOWNERS](./.github/CODEOWNERS).

### Support

This project is provided **as-is** and may be updated over time. For questions or issues:

1. **Check existing documentation** in the `/docs` folder
2. **Review closed issues** on GitHub for similar problems
3. **Open a new issue** if your question hasn't been answered

See [SUPPORT.md](./SUPPORT.md) for more details on getting help.

---

## Quick Reference

### Common Commands

```bash
# Setup environment
./scripts/setup-env.sh

# Run application
./scripts/start-app.sh

# Run backend tests
./scripts/run-server-tests.sh

# Run frontend tests
cd client && npm run test:e2e

# Run E2E tests
cd tests/e2e && npm install && npm test

# Build Docker images
docker build -f server/Dockerfile -t tailspin-server:latest .
cd client && docker build -t tailspin-client:latest .

# Deploy to Kubernetes
kubectl apply -f k8s/
```

### Port Reference

- **Frontend (Astro):** http://localhost:4321
- **Backend (Flask API):** http://localhost:5100

### Environment Variables

- `ENABLE_DEBUG_ENDPOINTS` - Enable debug routes (default: false)
- `DATABASE_URL` - Database connection string (default: SQLite in `/data`)
- `API_URL` - Backend API URL for frontend (default: http://localhost:5100)

---

## Troubleshooting

### Common Issues

**Port already in use:**
```bash
# Kill process on port 4321 or 5100
lsof -ti:4321 | xargs kill -9
lsof -ti:5100 | xargs kill -9
```

**Python dependencies not found:**
```bash
# Ensure virtual environment is activated
source venv/bin/activate
pip install -r server/requirements.txt
```

**Frontend build fails:**
```bash
# Clear cache and reinstall
cd client
rm -rf node_modules package-lock.json
npm install
npm run build
```

**Database issues:**
- Ensure `data/tailspin-toys.db` exists
- Check file permissions
- Verify SQLAlchemy connection string

---

**For questions or contributions, please refer to [CONTRIBUTING.md](./CONTRIBUTING.md) and open an issue on GitHub.**
