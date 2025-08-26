# End-to-End Tests

This directory contains comprehensive end-to-end tests for the Tailspin Toys application that validate the integration between the UI (Astro/Svelte frontend) and API (Flask backend).

## What These Tests Cover

### API Integration Tests (`api-integration.spec.ts`)
- Validates Flask API endpoints are responsive and return correct data structures
- Tests direct API calls to `/api/games` and `/api/games/{id}`
- Verifies error handling for non-existent resources
- Tests API access through Astro middleware

### UI + API Integration Tests (`ui-api-integration.spec.ts`) 
- Tests that the frontend correctly consumes and displays API data
- Validates navigation between pages with consistent data
- Tests error handling when API calls fail
- Ensures UI components properly integrate with backend services

### Complete User Workflows (`user-workflows.spec.ts`)
- Simulates realistic user journeys through the application
- Tests complex scenarios like browsing multiple games, navigation flows
- Validates performance expectations
- Tests data consistency across page navigations

## Setup and Running

### Prerequisites
- Node.js 22+ installed
- Python 3.13+ with Flask dependencies installed
- Both backend and frontend must be available

### Installation
```bash
npm install
```

### Running Tests
```bash
# Run all E2E tests
npm test

# Run tests with browser visible (for debugging)
npm run test:headed

# Run tests in debug mode
npm run test:debug

# Run tests with Playwright UI
npm run test:ui
```

### Configuration
The tests are configured in `playwright.config.ts` to:
- Automatically start both Flask backend (port 5100) and Astro frontend (port 4321)
- Run tests against `http://localhost:4321`
- Generate traces and screenshots on failure
- Use GitHub Actions reporter in CI environments

## CI Integration
These tests run automatically in GitHub Actions via the `ci-e2e.yml` workflow on:
- Pull requests to main branch
- Pushes to main branch
- Manual workflow dispatch

## Debugging Failed Tests
When tests fail:
1. Check the console output for specific error messages
2. Review generated screenshots in `test-results/`
3. Use `npm run test:debug` to step through tests interactively
4. Run `npx playwright show-trace <path-to-trace.zip>` to view detailed execution traces