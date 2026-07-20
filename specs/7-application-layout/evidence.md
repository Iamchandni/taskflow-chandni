## Implementation summary
A reusable `AppLayout` shell (persistent sidebar + header + routed `<Outlet />` content area) was introduced using React Router v6, wrapping all authenticated placeholder pages; `/login` renders outside the shell.

## Verification
- Test output: pass — 9/9 tests across 5 files (`Header`, `Sidebar`, `AppLayout`, `Router`, `App`)
- Validation agent: pass
- Manual checks: `tsc && vite build` succeeds with strict TypeScript; `npm run dev` confirms nav clicks update URL/active state and `/login` has no sidebar

## Known limitations
- No authentication or route protection (out of scope for this issue)
- Mobile responsive navigation (drawer/hamburger) is not implemented
- `vitest.config.ts` and `src/test-polyfills.ts` were added to polyfill `globalThis.Request` for react-router v6.26 compatibility with jsdom 21 / Node 16 — these were not in the original plan but do not affect the production build

## Follow-up issues
None filed by the Judgment Panel.

## PR
https://github.com/Iamchandni/taskflow-chandni/pull/8
