# History

## Project Context
- **Project:** tailspin-toystore — Crowdfunding platform for games
- **Stack:** Astro/Svelte/TS/Tailwind frontend, Python Flask backend, SQLite, Playwright + unittest
- **Deploy:** Azure AKS, Terraform, K8s, Docker
- **User:** Somnath Banerjee

## Learnings

- Created Cart, CartItem, Payment models following existing BaseModel pattern with @validates, to_dict (camelCase), __repr__
- Added `price` column (Float, default 0.0) to Game model for cart functionality
- Cart uses `session_id` (unique string) to identify cart sessions — no user auth model yet
- Cart→CartItem is one-to-many with cascade delete-orphan; Cart→Payment is one-to-one
- CartItem snapshots game price at add time to preserve historical pricing
- Payment uses UUID transaction_id, validates card_last_four as exactly 4 digits
- All new models registered in `server/models/__init__.py`
- Key files: `server/models/cart.py`, `server/models/cart_item.py`, `server/models/payment.py`

## Recent Work (2026-04-19)

**Sprint:** Shopping Cart Feature (Team: Uma, Somnath, Abhishek, Neil)

**Outcome:** ✅ SUCCESS — Cart models, API endpoints, UI components, and test suite all complete and integrated.

**Cross-Team Context:**
- Somnath built 7 API endpoints (5 cart, 2 payment) on top of Uma's models
- Abhishek created CartButton, CartPage, CheckoutForm UI with session-based cart tracking (localStorage UUID)
- Neil wrote 21 tests (14 cart, 7 payment) — all 39 backend tests passing
- Decision log maintained: schema design, API patterns, UI session management, test strategy

**Status:** Ready for E2E test coverage and payment processor integration.
