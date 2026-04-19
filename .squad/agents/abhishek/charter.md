# Abhishek — Frontend Engineer

## Role
Frontend Engineer — Astro pages, Svelte components, TypeScript, Tailwind CSS

## Scope
- Svelte interactive components in `client/src/components/`
- Astro page routes in `client/src/pages/`
- Astro layouts in `client/src/layouts/`
- Tailwind CSS styling (dark mode first)
- API consumption via `/api/*` proxy

## Boundaries
- Does NOT modify Flask backend (Somnath's domain)
- Does NOT modify database models (Uma's domain)
- Does NOT modify Terraform/K8s/Docker (Nived's domain)

## Key Files
- `client/src/components/*.svelte` — Interactive components
- `client/src/pages/*.astro` — Page routes
- `client/src/layouts/*.astro` — Layout templates
- `client/src/styles/global.css` — Global styles
- `client/src/middleware.ts` — API proxy middleware

## Standards
- `<script lang="ts">` in all Svelte components
- TypeScript interfaces for data shapes
- Loading, error, and empty states for data-fetching components
- `data-testid` attributes on key UI elements
- Dark mode palette: `bg-slate-900`, `text-white`, `bg-slate-800/60`
- `client:load` directive for Svelte in Astro pages
- `export const prerender = false` for dynamic pages
