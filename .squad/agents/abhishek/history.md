# History

## Project Context
- **Project:** tailspin-toystore — Crowdfunding platform for games
- **Stack:** Astro/Svelte/TS/Tailwind frontend, Python Flask backend, SQLite, Playwright + unittest
- **Deploy:** Azure AKS, Terraform, K8s, Docker
- **User:** Somnath Banerjee

## Learnings
- Cart session ID pattern: generate UUID via `crypto.randomUUID()`, store in localStorage key `cartSessionId`, reuse across all cart API calls.
- Use `window.dispatchEvent(new CustomEvent("cart-updated"))` to sync cart count in header when items change from other components.
- CheckoutForm uses Svelte `createEventDispatcher` for back-navigation to CartPage parent.
- The `client:load` directive is needed for Svelte components in Astro `.astro` files (not `client:only`).

## Recent Work (2026-04-19)

**Sprint:** Shopping Cart Feature (Team: Uma, Somnath, Abhishek, Neil)

**Contribution:** UI layer (CartButton, CartPage, CheckoutForm components, cart.astro page) with session-based cart tracking and real-time state sync via CustomEvent.

**Cross-Team Context:**
- Uma created Cart, CartItem, Payment models and Game.price column
- Somnath built 7 API endpoints (5 cart, 2 payment) with lazy cart creation and atomic checkout
- Neil wrote 21 tests (14 cart, 7 payment) — all 39 backend tests passing
- Decision log maintained: UI session management pattern, event-driven state sync, component integration points

**Status:** Ready for E2E test coverage and payment processor integration.
