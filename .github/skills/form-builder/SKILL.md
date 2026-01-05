---
compatibility: Astro + Svelte (TypeScript optional)
description: Build accessible forms with Astro + Svelte + Tailwind
license: MIT
metadata:
  apm_commit: bb6549bfcc3ccafe71f5313c7da1300585085f77
  apm_installed_at: '2026-01-01T21:07:59.784487'
  apm_package: sombaner/form-builder
  apm_version: 1.0.0
  author: danielmeppiel
  version: 1.0.0
name: form-builder
---

# Form Builder

Build accessible, production-ready forms using Astro pages + interactive Svelte components.

## When to Use

Activate when user asks to:
- Create any form (contact, signup, login, checkout, etc.)
- Add form validation
- Handle form submission
- Implement accessible error handling and focus management
- Add stable `data-testid` hooks for E2E tests

## Stack

- **Astro** — pages/routing/layout
- **Svelte** — client-side form state + validation + API calls
- **Tailwind CSS** — consistent styling (dark theme)

## Examples

- [Svelte form component](examples/form.svelte) — full client-side pattern (validation, focus, submit lifecycle)
- [Astro embedding](examples/astro-layout) — how to render and hydrate the form from an Astro page

## Install

No additional libraries are required by this skill.

Use it in projects that already have Astro + Svelte set up; then follow these conventions:
- Astro pages embed interactive forms as Svelte components with a hydration directive (e.g. `client:load`).
- Svelte components manage their own `form` state, `fieldErrors`, and `submitting` state.
- Validate client-side for UX, but assume server-side validation remains authoritative.
- Use accessible error patterns (`aria-invalid`, `aria-describedby`, `role="alert"`) and focus the first invalid field on submit.
- Add stable `data-testid` attributes for E2E tests.