# History

## Project Context
- **Project:** tailspin-toystore — Crowdfunding platform for games
- **Stack:** Astro/Svelte/TS/Tailwind frontend, Python Flask backend, SQLite, Playwright + unittest
- **Deploy:** Azure AKS, Terraform, K8s, Docker
- **User:** Somnath Banerjee

## Learnings

- Created `server/routes/cart.py` (cart_bp) with 5 endpoints: GET cart, POST add item, PUT update item, DELETE remove item, GET count.
- Created `server/routes/payments.py` (payments_bp) with 2 endpoints: POST checkout, GET payment by transaction ID.
- Registered both blueprints in `server/app.py`. All 18 existing tests still pass.
- Cart uses `get_or_create_cart()` helper to lazily create carts on first access. Add-item snapshots the game price at time of addition. Checkout sums item prices, creates Payment record, and marks cart as 'checked_out'.
- The CartItem model validates quantity >= 1, so setting quantity to 0 via PUT triggers a delete instead of an update to avoid validation errors.

## Recent Work (2026-04-19)

**Sprint:** Shopping Cart Feature (Team: Uma, Somnath, Abhishek, Neil)

**Contribution:** API layer (5 cart + 2 payment endpoints) built on Uma's models with lazy cart creation, price snapshots, and atomic checkout.

**Cross-Team Context:**
- Uma created Cart, CartItem, Payment models and Game.price column
- Abhishek built UI (CartButton, CartPage, CheckoutForm) with session-based cart tracking (localStorage UUID)
- Neil wrote 21 tests (14 cart, 7 payment) — all 39 backend tests passing
- Decision log maintained: API patterns, endpoint contracts, error handling strategy

**Status:** Ready for E2E test coverage and payment processor integration.
