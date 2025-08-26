
---

##  `AGENTS.md` for **Server** (`server/AGENTS.md`)

```markdown
# AI Agent Instructions — Server

This file guides AI coding agents on how to work with the **server** portion of the Tailspin-ToyStore project.

---

## Project Context & Structure

- Server-side application (likely REST API)
- Key folders:
  - `Controllers/`, `Routes/` - API endpoints
  - `Models/`, `Entities/` - data models
  - `Tests/` or `test/` - unit/integration tests
- Common commands:
  - `npm run dev` or `dotnet run` (per tech stack)
  - `npm test` or `dotnet test`

---

## Development Workflow

- **Install dependencies**:
  ```bash
  cd server/
  npm ci  # or `dotnet restore`

## Run server locally

npm run dev

## Run all tests:

npm test        # or `dotnet test`


## Run single test file:

npm test -- path/to/file.test.js
