# Tailspin Toys Client Form Building Guidelines (Astro + Svelte + Tailwind)

These guidelines standardize how to build forms in the `client/src` module, aligning with existing patterns in:
- Layout + global styling: [client/src/layouts/Layout.astro](client/src/layouts/Layout.astro), [client/src/styles/global.css](client/src/styles/global.css)
- Interactive Svelte components: [client/src/components/GameDetails.svelte](client/src/components/GameDetails.svelte), [client/src/components/GameList.svelte](client/src/components/GameList.svelte), [client/src/components/MemoryLeakTool.svelte](client/src/components/MemoryLeakTool.svelte)
- Page routing: [client/src/pages/index.astro](client/src/pages/index.astro), [client/src/pages/game/[id].astro](client/src/pages/game/[id].astro)

---

## 1) Architecture & Placement

### 1.1 Use Astro for pages, Svelte for interactivity
- Pages & routing belong in `client/src/pages/**` (Astro).
- Forms that require client-side state/validation/API calls should be implemented as Svelte components in `client/src/components/**`.
- Embed the form component into the page with an appropriate hydration directive (use whichever hydration pattern is already used in the surrounding codebase).

### 1.2 Keep forms componentized and reusable
- If a form is used in more than one place, create a reusable component instead of duplicating markup.
- Prefer composition: Form, FormField, ErrorSummary, SubmitButton patterns (names optional; consistency required).

---

## 2) Styling & UI Consistency (Tailwind + Dark Theme)

### 2.1 Match the established visual system
- Maintain dark mode styling consistent with [client/src/layouts/Layout.astro](client/src/layouts/Layout.astro).
- Use rounded corners and modern UI patterns (cards, subtle borders, clear focus states).
- Prefer Tailwind utility classes over bespoke CSS; use [client/src/styles/global.css](client/src/styles/global.css) only for truly global concerns.

### 2.2 Recommended form layout patterns
- Wrap forms in a “card” container (dark background, border, padding).
- Use vertical spacing (`space-y-*`) and clear section headings.
- Align labels and inputs consistently; avoid dense layouts.

### 2.3 Button conventions
- Primary action: high-contrast button (consistent hover/transition).
- Secondary action: subdued styling.
- Disable submit button during submission (`disabled:*` states).

---

## 3) State Model & Data Flow (Svelte)

### 3.1 Use explicit state flags
Mirror the pattern used in [client/src/components/GameDetails.svelte](client/src/components/GameDetails.svelte):
- `loading` / `submitting`
- `error: string | null`
- `data` or `formValues`

### 3.2 Prefer predictable, minimal state
- Keep form state in one object (e.g., `form = { ... }`) or a small set of variables.
- Avoid deriving “truth” from the DOM; keep state as the source of truth.

### 3.3 Submission lifecycle
On submit:
1. Clear stale errors
2. Set `submitting/loading = true`
3. Perform the request
4. Handle success (reset form / navigate / show success message)
5. Handle failure (populate error + field-level errors)
6. Set `submitting/loading = false` in `finally`

---

## 4) Validation Standards

### 4.1 Validate both client-side and server-side
- Client-side validation improves UX, but server-side remains authoritative.
- Client-side validation should be fast, deterministic, and not depend on network calls.

### 4.2 Validation types
- Field-level: required, min/max length, numeric bounds, format checks.
- Cross-field: e.g., “end date after start date”.
- Submission-time: run full validation on submit; optional “on blur” validation for UX.

### 4.3 Error presentation
Provide both:
- Field-level errors near the input
- Form-level summary at top for submission errors (network, authorization, unexpected failures)

---

## 5) Accessibility (Non-Negotiable)

### 5.1 Labels and associations
- Every input must have a `<label>` with `for` bound to the input `id`, or wrap input in label.
- Use `name` attributes consistently for semantics and debugging.

### 5.2 ARIA for errors
- Use `aria-invalid="true"` when a field has an error.
- Link error text via `aria-describedby` to an element containing the error message.
- Prefer `role="alert"` for form-level error banners to announce errors to screen readers.

### 5.3 Keyboard and focus
- All fields and buttons must be keyboard reachable.
- On submit with errors: move focus to the error summary or first invalid field.
- Ensure visible focus styles (don’t remove focus outlines without a replacement).

---

## 6) Data Fetching & API Integration

### 6.1 Use relative API routes consistently
Existing components fetch via relative paths (e.g., `/api/...`) as shown in [client/src/components/GameDetails.svelte](client/src/components/GameDetails.svelte).
- Keep API calls relative (works across dev/proxy setups).
- Handle non-OK responses explicitly and surface meaningful messages.

### 6.2 Timeouts and resilience
- Provide user feedback for slow requests (spinner/loading state).
- Handle network failures gracefully with a user-actionable retry path when appropriate.

### 6.3 Don’t leak sensitive data
- Never render raw server errors if they may include stack traces or secrets.
- Display user-friendly messages.

---

## 7) Testing Hooks & E2E Reliability

### 7.1 Add `data-testid` to stable UI elements
E2E tests commonly use `data-testid` selectors. For forms, standardize:
- `data-testid="form-<name>"`
- `data-testid="field-<name>"`
- `data-testid="error-<name>"`
- `data-testid="submit-<name>"`
- `data-testid="toast-success"` / `data-testid="toast-error"` (if used)

### 7.2 Avoid brittle selectors
- Prefer `data-testid` over text selectors for critical flows.
- Don’t key tests off dynamic copy that might change.

---

## 8) Security & Input Hygiene

### 8.1 Treat all inputs as untrusted
- Validate and sanitize on the server; client-side validation is not security.
- Avoid inserting user input into HTML via unsafe methods.
- Encode user-provided strings by default.

### 8.2 Auth/error handling
- If forms mutate server state, handle 401/403 and show a clear next step to the user.

---

## 9) UX Best Practices

### 9.1 Progressive disclosure
- Keep required fields minimal.
- Hide advanced options behind expandable sections when appropriate.

### 9.2 Clear microcopy
- Labels should describe the field, not the format.
- Put format hints as helper text under the field.

### 9.3 Prevent double-submits
- Disable submit button during submission.
- Consider idempotency keys if the backend supports it (still guard UX on the client).

---

## 10) Performance Guidelines

### 10.1 Keep hydration minimal
- Only hydrate forms that need interactivity.
- Prefer smaller components and avoid large dependency bundles.

### 10.2 Avoid unnecessary re-renders
- Don’t recompute expensive derived values on every keystroke without need.
- Debounce expensive validations (never debounce required/empty checks).

---

## 11) Recommended Form Skeleton (Checklist)

- [ ] Svelte component under `client/src/components`
- [ ] Uses `loading/submitting`, `error`, and field-level error state
- [ ] Tailwind styling matches dark theme + rounded corners
- [ ] Proper labels + `aria-invalid` + `aria-describedby`
- [ ] Stable `data-testid` hooks
- [ ] Handles `response.ok` and failure cases explicitly
- [ ] Prevents double submit
- [ ] E2E-friendly: predictable DOM states (loading, error, success)

---

## 12) When to Refactor into Shared Utilities
Refactor shared behavior when at least two forms need the same:
- validation helpers
- error mapping from API responses to fields
- standardized input components (text, textarea, select, checkbox, radio)
- consistent submit button/spinner behavior

Keep shared components small and focused to maintain fast iteration in `client/src/components/**`.