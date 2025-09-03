# Tailspin Toys - Frontend Client

The frontend application for Tailspin Toys, a fictional game crowdfunding platform built with [Astro](https://astro.build/) and [Svelte](https://svelte.dev/). This application provides a responsive web interface for browsing and discovering board games.

## Architecture

This is an Astro-based static site with Svelte components for interactivity. The frontend communicates with a Flask backend API to fetch game data and handles client-side routing for dynamic content.

## Project Structure

```text
client/
├── public/
│   └── favicon.svg
├── src/
│   ├── assets/           # Static assets (images, icons)
│   ├── components/       # Svelte components
│   │   ├── GameDetails.svelte    # Individual game detail view
│   │   ├── GameList.svelte       # Games listing with filtering
│   │   ├── Header.astro          # Site header and navigation
│   │   └── MemoryLeakTool.svelte # Development debugging tool
│   ├── layouts/
│   │   └── Layout.astro  # Main page layout template
│   ├── pages/            # Astro pages (routes)
│   │   ├── index.astro   # Homepage with game list
│   │   ├── about.astro   # About page
│   │   └── game/
│   │       └── [id].astro # Dynamic game detail pages
│   ├── styles/
│   │   └── global.css    # Global CSS styles
│   └── middleware.ts     # API proxy middleware
├── e2e-tests/           # Frontend-specific E2E tests
└── Dockerfile          # Container configuration
```

## Features

- **Game Discovery**: Browse available board games with filtering capabilities
- **Game Details**: View detailed information about individual games
- **Responsive Design**: Works on desktop and mobile devices
- **Performance Optimized**: Static generation with selective hydration

## API Integration

The frontend connects to the Flask backend API through:
- **Middleware Proxy**: `src/middleware.ts` handles API routing
- **Default Backend**: `http://localhost:5100` (configurable via `API_SERVER_URL`)
- **Endpoints Used**: `/api/games`, `/api/games/{id}`

## Development Commands

All commands should be run from the `client/` directory:

| Command                   | Action                                           |
| :------------------------ | :----------------------------------------------- |
| `npm install`             | Install dependencies                             |
| `npm run dev`             | Start development server at `localhost:4321`    |
| `npm run build`           | Build production site to `./dist/`              |
| `npm run preview`         | Preview production build locally                 |
| `npm run test:e2e`        | Run frontend E2E tests                           |
| `npm run test:load`       | Run load tests                                   |

## Environment Configuration

- `API_SERVER_URL`: Backend API URL (default: `http://localhost:5100`)

## Testing

- **E2E Tests**: Located in `e2e-tests/` using Playwright
- **Load Tests**: Performance testing with custom configuration
- **Integration Tests**: Full-stack tests available in `../tests/e2e/`

## Deployment

The application can be deployed as:
- Static files (recommended for production)
- Container using the included Dockerfile
- Kubernetes deployment (see `../k8s/client-deployment.yaml`)

For workshop tutorials and setup instructions, see the [docs](../docs/) directory.
