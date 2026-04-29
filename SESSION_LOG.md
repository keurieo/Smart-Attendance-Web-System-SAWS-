# Session Log — Production Upgrade

## Block A — Critical
- [✓] A1 — Fix unconditional production settings (wsgi.py / asgi.py)

## Block B — High
- [✓] B1 — Fix role field mismatch (numeric ID vs string)
- [✓] B2 — Fix edit form reading wrong role field
- [✓] B3 — Fix enrollment fetch using wrong endpoint

## Block C — Medium
- [✓] C1 — Normalize error handling in ScanPage
- [✓] C2 — Fix broken qr_url field (Option A: removed qr_url)
- [✓] C3 — Fix React Query cache invalidation mismatch
- [✓] C4 — Remove hardcoded role IDs from dropdown

## Block D — Low
- [✓] D1 — Reorder attendance token validation
- [✓] D2 — Harden X-Forwarded-For IP handling
- [✓] D3 — Surface session-expired feedback

## Block E — Architectural
- [ ] E1 — Centralize audit logging helper
- [ ] E2 — Standardize and document API endpoint paths
- [ ] E3 — Single error parsing path across frontend
- [ ] E4 — Pin frontend dependencies, enforce lockfile in CI
- [ ] E5 — Add CI lint/format checks (backend + frontend)
- [ ] E6 — Add missing test coverage

## Documentation
- [ ] Update README.md endpoint paths
- [ ] Update SETUP.md health endpoint note
- [ ] Create API_REFERENCE.md
- [ ] Add DEPLOYMENT.md proxy config section
- [ ] Update CHANGELOG.md
