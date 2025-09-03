# Tailspin Toys - Architecture Overview

This document provides a comprehensive overview of the Tailspin Toys application architecture, including system components, data flow, and deployment strategies.

## System Architecture

Tailspin Toys is a modern web application built using a decoupled frontend-backend architecture optimized for performance, scalability, and developer experience.

### High-Level Architecture

```
┌─────────────────┐     ┌─────────────────┐     ┌─────────────────┐
│                 │     │                 │     │                 │
│   Frontend      │────▶│   Backend API   │────▶│   Database      │
│   (Astro/Svelte)│     │   (Flask)       │     │   (SQLite)      │
│                 │     │                 │     │                 │
└─────────────────┘     └─────────────────┘     └─────────────────┘
       :4321                   :5100                   .db file
```

## Frontend Architecture

### Technology Stack
- **Framework**: [Astro](https://astro.build/) - Static site generator with selective hydration
- **Components**: [Svelte](https://svelte.dev/) - Reactive UI components
- **Build Tool**: Vite (integrated with Astro)
- **Styling**: CSS with global styles
- **Testing**: Playwright for E2E testing

### Component Structure

```
src/
├── pages/          # Route-based pages (Astro)
│   ├── index.astro      # Homepage with game listing
│   ├── about.astro      # Static about page
│   └── game/[id].astro  # Dynamic game detail pages
├── components/     # Reusable UI components (Svelte)
│   ├── GameList.svelte     # Interactive games list with filtering
│   ├── GameDetails.svelte  # Game information display
│   ├── Header.astro        # Site navigation
│   └── MemoryLeakTool.svelte # Development debugging tool
├── layouts/        # Page layouts (Astro)
│   └── Layout.astro        # Main site layout wrapper
└── middleware.ts   # API proxy and routing logic
```

### Rendering Strategy
- **Static Generation**: Pages are pre-built at build time for optimal performance
- **Selective Hydration**: Only interactive Svelte components are hydrated on the client
- **API Proxy**: Middleware handles API requests to avoid CORS issues

## Backend Architecture

### Technology Stack
- **Framework**: [Flask](https://flask.palletsprojects.com/) - Lightweight Python web framework
- **ORM**: [SQLAlchemy](https://www.sqlalchemy.org/) - Database abstraction layer
- **Database**: SQLite - File-based database for simplicity
- **Testing**: pytest for unit testing

### API Structure

```
server/
├── app.py          # Application entry point and configuration
├── models/         # Data models and database schema
│   ├── base.py         # Base model with common functionality
│   ├── game.py         # Game model with relationships
│   ├── category.py     # Category model
│   └── publisher.py    # Publisher model
├── routes/         # API endpoint definitions
│   ├── games.py        # Game-related endpoints
│   └── debug.py        # Development/debugging endpoints
├── utils/          # Utility functions and database operations
│   ├── database.py     # Database initialization and utilities
│   └── seed_data/      # Sample data for development
└── tests/          # Unit tests for API endpoints
```

### Database Schema

```sql
-- Core entities with relationships
Categories (1) ──< Games >── (1) Publishers

Categories:
- id (INTEGER PRIMARY KEY)
- name (VARCHAR)

Publishers:  
- id (INTEGER PRIMARY KEY)
- name (VARCHAR)

Games:
- id (INTEGER PRIMARY KEY) 
- title (VARCHAR NOT NULL)
- description (TEXT NOT NULL)
- star_rating (FLOAT)
- category_id (INTEGER FOREIGN KEY)
- publisher_id (INTEGER FOREIGN KEY)
```

## Data Flow

### Request Flow
1. **Client Request**: Browser requests page or makes API call
2. **Frontend Routing**: Astro handles page routing, middleware handles API proxying
3. **API Processing**: Flask receives request, queries database via SQLAlchemy
4. **Data Transformation**: Models convert database records to JSON via `to_dict()` methods
5. **Response**: JSON data returned to frontend for rendering

### Example: Game Detail Page Flow
```
User visits /game/1
    ↓
Astro renders [id].astro page
    ↓
Svelte component makes API call
    ↓
Middleware proxies to /api/games/1
    ↓
Flask queries database for game ID 1
    ↓
SQLAlchemy joins Game, Category, Publisher tables
    ↓
Game.to_dict() serializes data to JSON
    ↓
JSON returned to frontend
    ↓
Svelte component renders game details
```

## Development Environment

### Local Development Setup
1. **Backend**: Flask dev server on `localhost:5100`
2. **Frontend**: Astro dev server on `localhost:4321` 
3. **Database**: SQLite file at `data/tailspin-toys.db`
4. **Hot Reload**: Both servers support hot reload for development

### Development Tools
- **Scripts**: Automated setup and testing scripts in `scripts/`
- **Docker**: Containerized deployment configuration
- **Testing**: Multi-level testing strategy (unit, integration, E2E)

## Testing Architecture

### Test Levels
1. **Unit Tests**: Backend API endpoints (`server/tests/`)
2. **Frontend E2E**: Component and page tests (`client/e2e-tests/`)  
3. **Integration Tests**: Full-stack user workflows (`tests/e2e/`)
4. **Load Tests**: Performance and stress testing (`loadtest/`)

### Test Execution
- **Local**: Independent test runners for each layer
- **CI/CD**: GitHub Actions orchestrates all test suites
- **Coverage**: Comprehensive test coverage across frontend and backend

## Deployment Architecture

### Container Strategy
- **Frontend Container**: Nginx serving static Astro build
- **Backend Container**: Python Flask application with Gunicorn
- **Database**: Shared volume for SQLite database file

### Kubernetes Deployment
```yaml
# Simplified deployment structure
Namespace: tailspin-toys
├── client-deployment (Frontend)
├── server-deployment (Backend)  
└── Shared PVC for database
```

### Production Considerations
- **Scalability**: Frontend scales horizontally, backend can scale with load balancer
- **Database**: SQLite suitable for demo/workshop; consider PostgreSQL for production
- **CDN**: Static assets can be served from CDN for global performance
- **Security**: HTTPS termination at load balancer, environment-based configuration

## Security Considerations

### Current Security Model
- **No Authentication**: Public API for workshop/demo purposes
- **CORS Enabled**: All origins allowed for development flexibility
- **Input Validation**: SQLAlchemy models include basic validation

### Production Security Recommendations
- Implement authentication and authorization
- Restrict CORS to specific domains
- Add rate limiting and request validation
- Use HTTPS for all communications
- Implement proper error handling without exposing internals

## Performance Characteristics

### Frontend Performance
- **Static Generation**: Near-instant page loads
- **Selective Hydration**: Minimal JavaScript bundle size
- **Image Optimization**: Astro's built-in optimization features

### Backend Performance  
- **Simple Queries**: Efficient SQLAlchemy joins for related data
- **Caching**: Potential for Redis caching layer in production
- **Database**: SQLite performs well for read-heavy workloads

## Development Workflow

### Workshop Integration
This application is designed specifically for GitHub Copilot workshops, featuring:
- **Agent-Friendly Structure**: Clear separation of concerns
- **Comprehensive Documentation**: Extensive documentation for AI agents
- **Test Coverage**: Multiple testing approaches for validation
- **Realistic Complexity**: Enough complexity to demonstrate real-world scenarios

For workshop instructions and tutorials, see the main [workshop documentation](./README.md).