# Code Review: Sort Games
**Ready for Production**: Yes
**Critical Issues**: 0

## Review Scope
- Backend API sorting and search handling in `GET /api/games`
- Frontend sort/search request construction in the game list UI
- Automated coverage added for sort and search behaviors

## Review Plan
- Injection and input-handling review for `search` and `sort` query parameters
- Broken access control review for the newly exposed request paths
- Client-side request construction review for user-controlled values
- Test coverage review for new success and failure paths

## Priority 1 (Must Fix) ⛔
- No must-fix security issues identified in the reviewed change set.

## Recommended Changes
- No immediate security change required.

## Notes
- The backend uses an allowlist for sortable fields, which prevents attacker-controlled `order_by` injection.
- The title search path continues to use ORM query construction rather than raw SQL, so this change does not introduce SQL injection risk.
- The frontend sends the selected sort value as a query parameter, but server-side validation remains authoritative.

## Residual Risks / Gaps
- The public games listing remains intentionally unauthenticated. That is acceptable for a catalog endpoint, but it should stay limited to non-sensitive fields.
- The endpoint is still unpaginated and accepts arbitrary search-string length. That is not introduced by this PR, but it remains the main abuse-resistance gap if traffic becomes hostile or large-scale.
- Backend tests cover valid and invalid sort options well. I did not see corresponding browser-level assertions for the new sort selector behavior.