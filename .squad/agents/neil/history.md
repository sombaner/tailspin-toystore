# History

## Project Context
- **Project:** tailspin-toystore — Crowdfunding platform for games
- **Stack:** Astro/Svelte/TS/Tailwind frontend, Python Flask backend, SQLite, Playwright + unittest
- **Deploy:** Azure AKS, Terraform, K8s, Docker
- **User:** Somnath Banerjee

## Learnings

- Cart add/update/delete routes return the full cart `to_dict()`, not individual CartItem objects. Tests must extract items from `data["items"]` array.
- Checkout of an already-checked-out cart returns 404 ("No active cart found") rather than 400, because the route filters by `status='active'`.
- All 39 tests (18 existing + 14 cart + 7 payment) pass as of this session.
- Game model now has a `price` field (Float, default 0.0) — tests must seed games with explicit prices.

## Recent Work (2026-04-19)

**Sprint:** Shopping Cart Feature (Team: Uma, Somnath, Abhishek, Neil)

**Contribution:** Test suite (14 cart + 7 payment tests) written test-first and validated against Somnath's implementations. All 39 backend tests passing.

**Cross-Team Context:**
- Uma created Cart, CartItem, Payment models and Game.price column
- Somnath built 7 API endpoints (5 cart, 2 payment) with lazy cart creation and atomic checkout
- Abhishek created UI (CartButton, CartPage, CheckoutForm) with session-based cart tracking (localStorage UUID)
- Decision log maintained: test response format contracts, error code handling, price snapshot validation in fixtures

**Status:** Ready for E2E test coverage and payment processor integration.
