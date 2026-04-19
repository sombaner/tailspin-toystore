# Squad Decisions

## Active Decisions

### 1. Shopping Cart & Payment Schema Design

**Author:** Uma (Database Engineer)  
**Date:** 2025-07-14  
**Status:** Implemented

**Decision:**
- Cart identified by `session_id` (unique string) — no user/auth model dependency yet. Can be linked to a user model later.
- CartItem snapshots `price` at time of adding to cart, so price changes don't affect existing carts.
- Cart→Payment is one-to-one (`uselist=False`) — one payment per cart checkout. If multiple payment attempts are needed, the team should discuss changing to one-to-many.
- `price` added to Game model (Float, default 0.0) — every game now has a price for cart functionality.
- Cascade delete-orphan on Cart→CartItem — deleting a cart removes its items.

**Impact:** Game model has new `price` column. Three new tables: `carts`, `cart_items`, `payments`.

---

### 2. Cart & Payment API Design

**Author:** Somnath (Backend Engineer)  
**Date:** 2025-07-15  
**Status:** Implemented

**Decision:**
- Lazy cart creation — `GET /api/cart?session_id=X` creates the cart if one doesn't exist. Frontend never needs separate "create cart" call.
- Price snapshot on add — Game's current price is copied to `CartItem.price` when adding to cart.
- Quantity 0 = delete — `PUT /api/cart/items/<id>` with `quantity: 0` deletes the item.
- Checkout is atomic — Checkout endpoint calculates total, creates Payment, and marks cart as 'checked_out' in single commit.

**Impact:** 5 cart endpoints + 2 payment endpoints. Frontend can integrate cart and checkout flows.

---

### 3. Cart UI Session Management Pattern

**Author:** Abhishek (Frontend)  
**Date:** 2025-07-16  
**Status:** Implemented

**Decision:**
- Use client-side UUID stored in `localStorage` (`cartSessionId`) passed to all cart API endpoints.
- `cart-updated` CustomEvent on `window` keeps header cart count badge in sync across components.
- Backend cart endpoints must accept `session_id` as query param (GET/DELETE) or body param (POST/PUT).

**Impact:** No auth dependency — cart works for anonymous users. Components: CartButton, CartPage, CheckoutForm, GameDetails share UUID pattern.

---

### 4. Cart & Payment Test Strategy

**Author:** Neil (Test Engineer)  
**Date:** 2025-07-18  
**Status:** Implemented

**Decision:**
- Tests assert against full cart `to_dict()` responses (not individual items), matching actual route return pattern.
- `test_checkout_already_checked_out` accepts both 400 and 404 (route returns 404 when no active cart found after first checkout).
- Test data includes explicit game prices to validate price snapshot behavior in cart items.

**Impact:** 14 cart tests + 7 payment tests (all passing). Tests serve as contract for Cart/Payment API surface.

## Governance

- All meaningful changes require team consensus
- Document architectural decisions here
- Keep history focused on work, decisions focused on direction
