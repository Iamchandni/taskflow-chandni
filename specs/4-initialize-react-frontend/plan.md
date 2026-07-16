## Summary
Finalize the already-scaffolded React + TypeScript + Vite frontend under `frontend/` so it renders BOTH required placeholder strings, and verify it installs, tests, builds, and serves without touching any backend code.

## Source issues
- #4: Initialize React Frontend Application using Vite and TypeScript

## Current state (read before doing anything)
The Vite + React + TypeScript scaffold already exists and is committed on this branch (tests in `476d78f`, implementation in `795f339`, favicon in `9febcc6`). Do NOT re-scaffold with `npm create vite` — that would clobber working files. Confirmed present and correct:
- `frontend/package.json` — name `taskflow-frontend`, scripts `dev`/`build`/`preview`/`test`/`test:watch`; deps `react@^18.3.1`, `react-dom@^18.3.1`; devDeps Vite 4, Vitest 0.34, Testing Library, jsdom, TypeScript 5.
- `frontend/vite.config.ts` — `@vitejs/plugin-react`, `server.port: 5173`, Vitest block (`globals: true`, `environment: 'jsdom'`, `setupFiles: './src/setupTests.ts'`).
- `frontend/tsconfig.json`, `frontend/tsconfig.node.json` — strict TS, `jsx: react-jsx`, test type globals wired.
- `frontend/index.html` — mounts `/src/main.tsx` into `#root`, `<link rel="icon" href="/vite.svg" />`.
- `frontend/src/main.tsx` — React 18 `createRoot` in `StrictMode`, imports `./index.css`.
- `frontend/src/App.css`, `frontend/src/index.css` — minimal styling.
- `frontend/src/App.test.tsx`, `frontend/src/setupTests.ts` (`import '@testing-library/jest-dom'`), `frontend/src/vite-env.d.ts`.
- `frontend/public/vite.svg` — exists; favicon reference resolves, no 404.
- `frontend/node_modules/` — dependencies already installed.

**Open discrepancy this plan resolves:** Issue #4's *In Scope* requires the exact on-screen text `----Created this frontend for taskflow using Nightshift pipeline----`, while its *Acceptance Criteria* (listed twice) requires `TaskFlow Frontend Initialized`. The committed `frontend/src/App.tsx:6-7` renders only the `<h1>TaskFlow Frontend Initialized</h1>` plus a generic paragraph "The frontend application is running successfully." The Nightshift string is currently MISSING from the rendered page. Both strings are required by the issue, so the placeholder must display both. Resolution: keep the existing `<h1>` (satisfies Acceptance Criteria and the existing tests) and replace the generic paragraph with the exact Nightshift string (satisfies In Scope).

## Files to create or modify
- `frontend/src/App.tsx` — MODIFY. Keep `<h1>TaskFlow Frontend Initialized</h1>` unchanged. Replace the paragraph text `The frontend application is running successfully.` with the exact string `----Created this frontend for taskflow using Nightshift pipeline----`. No other structural changes. This is the only implementation change.
- `frontend/src/App.test.tsx` — MODIFY (add one test only; do not alter the three existing tests). Add a fourth test asserting the Nightshift string renders on the page (see Test plan item 4).
- `frontend/public/vite.svg` — REFERENCE ONLY, already committed. Do not modify.
- All other `frontend/**` files listed under "Current state" — REFERENCE ONLY, DO NOT MODIFY unless a verification step fails and traces to a defect in that specific file.

## Test plan (write these first)
Tests 1–3 already exist in `frontend/src/App.test.tsx` and were authored test-first. Do not rewrite them; confirm they still pass. Add test 4 BEFORE editing `App.tsx` (it must fail first, proving the Nightshift string is absent, then pass after the edit).

1. Test `App renders the initialization message` → valid render: `render(<App />)`, then `screen.getByText('TaskFlow Frontend Initialized')` resolves to an in-document element.
2. Test `App exposes the message as a level-1 heading` → semantic contract: `screen.getByRole('heading', { level: 1 })` has text content `TaskFlow Frontend Initialized`. Guards against an always-passing text-only check.
3. Test `App renders without throwing` → stability: `expect(() => render(<App />)).not.toThrow()`.
4. Test `App displays the Nightshift pipeline message` → NEW: `render(<App />)`, then `expect(screen.getByText('----Created this frontend for taskflow using Nightshift pipeline----')).toBeInTheDocument()`. Use the exact literal string including leading/trailing `----` and no surrounding whitespace. This covers the In-Scope on-screen-message requirement. Note: Testing Library's default text matcher trims and collapses whitespace, so ensure the JSX contains no interpolation that would inject extra nodes; render the string as a single text child of the paragraph.

No invalid-input or permission-failure tests apply: this issue has no inputs, no auth, and no API calls (all explicitly out of scope). The failure mode under test is "placeholder does not render a required string," covered by tests 1–4.

## Implementation steps
1. From `frontend/`, run `npm install`; confirm exit code 0 with no `ERESOLVE`/peer-dependency errors. If it fails, STOP and surface the exact npm error verbatim — do not edit backend code or downgrade unrelated packages to work around it.
2. Add test 4 to `frontend/src/App.test.tsx` inside the existing `describe('App', ...)` block, exactly:
   ```tsx
   test('App displays the Nightshift pipeline message', () => {
     render(<App />)
     expect(
       screen.getByText('----Created this frontend for taskflow using Nightshift pipeline----')
     ).toBeInTheDocument()
   })
   ```
3. Run `npm run test` and confirm test 4 FAILS (string not yet present) while tests 1–3 pass — this proves the test is meaningful (TDD red step).
4. Edit `frontend/src/App.tsx`: change line 7 from
   `<p>The frontend application is running successfully.</p>`
   to
   `<p>----Created this frontend for taskflow using Nightshift pipeline----</p>`
   Leave `import './App.css'`, the `<main className="app">` wrapper, and the `<h1>` line unchanged. Final component:
   ```tsx
   import './App.css'

   function App() {
     return (
       <main className="app">
         <h1>TaskFlow Frontend Initialized</h1>
         <p>----Created this frontend for taskflow using Nightshift pipeline----</p>
       </main>
     )
   }

   export default App
   ```
5. Run `npm run test` (`vitest run`) and confirm 4 passed, 0 failed (TDD green step).
6. Run `npm run build` (`tsc && vite build`); confirm exit 0 — TypeScript type-checks `src/` (including `App.test.tsx`, covered by the `types` in `tsconfig.json`) with no errors and Vite emits `dist/`. `dist/` is gitignored — do not commit it.
7. Run `npm run dev`; confirm Vite prints `Local: http://localhost:5173/` and starts without errors, then stop the process. It is long-running — confirm the startup banner, do not await/block on it.
8. Confirm no backend files changed: run `git status --short` and verify no paths under `app/`, `alembic/`, `scripts/`, nor `docker-compose.yml`, `Dockerfile`, `requirements.txt`, `pyproject.toml`, `alembic.ini`, `seed.sql`, `README.md` appear. The only changed tracked paths from this group are `frontend/src/App.tsx` and `frontend/src/App.test.tsx`.
9. Optionally confirm backend startup is unaffected: run `pytest -q` from the repo root; it must still pass as before. Do not modify any test to make it pass.

## Error handling
- If `npm install` fails (network, registry, peer-deps): STOP, surface the raw npm error verbatim, and do not modify backend files or the lockfile to force a resolution. Report it as a blocking dependency error per the issue's "Error Handling / Failure Expectations."
- If `npm run build` fails on a TypeScript error: report the exact `tsc` diagnostic (file + line). Fix only the offending `frontend/` file; never relax `strict` in `tsconfig.json` to hide a real error.
- If any test fails: report which assertion failed and the received DOM. Fix `frontend/src/App.tsx` (not the assertion) so the `<h1>` text is exactly `TaskFlow Frontend Initialized` and the `<p>` text is exactly `----Created this frontend for taskflow using Nightshift pipeline----`.
- If `npm run dev` fails to bind port 5173: report the port conflict; do not silently change the port in `vite.config.ts` without noting it. Port choice is not an acceptance criterion, but the message must be surfaced.
- Do NOT log or commit secrets, tokens, `.env` values, or `node_modules/` contents. There is no PII or credential handling in this issue.

## Constraints
- Do NOT modify any backend code or config: nothing under `app/`, `alembic/`, `scripts/`, nor `docker-compose.yml`, `Dockerfile`, `requirements.txt`, `pyproject.toml`, `alembic.ini`, `seed.sql`, `README.md`, `CONSTITUTION.md`. The frontend interacts with the backend only through future REST calls (out of scope here).
- Do NOT add anything out of scope for issue #4: no routing, no auth, no Tailwind, no API client, no state management, no additional UI components, no Docker changes, no `.env` files.
- Do NOT re-run `npm create vite` or otherwise regenerate the scaffold — it exists and is committed; regenerating would clobber `App.tsx`, tests, and configs.
- Do NOT alter the three existing tests in `frontend/src/App.test.tsx` — only append test 4. The `<h1>` text `TaskFlow Frontend Initialized` must remain exactly as-is to keep tests 1–2 green.
- No new npm dependencies beyond those already in `frontend/package.json`. Adding a package requires justification recorded here first; none is anticipated.
- Do NOT commit `frontend/dist/` or `frontend/node_modules/` (already gitignored).

## Risks
- Risk: A Coder re-scaffolds with `npm create vite`, overwriting committed `App.tsx`/tests. Mitigation: "Current state" and Constraints forbid re-scaffolding; the only edits are `App.tsx` line 7 and one appended test.
- Risk: Editing the paragraph inadvertently changes the `<h1>`, breaking tests 1–2. Mitigation: step 4 pins the full final component; only line 7 changes.
- Risk: Whitespace mismatch on the Nightshift string (extra spaces, smart dashes, or wrapping the string across JSX nodes) causes `getByText` to miss it. Mitigation: render the string as a single plain-text child of `<p>`; copy the literal `----Created this frontend for taskflow using Nightshift pipeline----` exactly (ASCII hyphens, no trailing space).
- Risk: `tsconfig.json` `include: ["src"]` type-checks `App.test.tsx` during `npm run build`; a missing test type would break the build. Mitigation: `types` already includes `vitest/globals` and `@testing-library/jest-dom`; verified in step 6.
- Risk: Windows dev environment — `npm run dev` is long-running and can block an automated runner. Mitigation: step 7 confirms the startup banner, then stops the process; do not await it.

## Rollback
- The frontend is fully isolated under `frontend/` with no backend coupling. To revert this group's work: `git checkout -- frontend/src/App.tsx frontend/src/App.test.tsx` (or revert the PR) restores the prior placeholder. The pre-existing `frontend/` scaffold commits remain independent. No migrations, no runtime/backend impact, no backend redeploy — rollback is risk-free for the API.

## Acceptance criteria
- [ ] `frontend/` directory exists and is a React + TypeScript + Vite app (`package.json`, `vite.config.ts`, `tsconfig.json` present).
- [ ] `npm install` completes successfully (step 1).
- [ ] `npm run test` passes 4/4 (Test plan items 1–4).
- [ ] The placeholder page renders `TaskFlow Frontend Initialized` as an `<h1>` (tests 1–2).
- [ ] The placeholder page renders `----Created this frontend for taskflow using Nightshift pipeline----` on screen (test 4 + browser check).
- [ ] `npm run build` (`tsc && vite build`) exits 0 and emits `dist/` (step 6).
- [ ] `npm run dev` starts the dev server on http://localhost:5173/ without errors (step 7).
- [ ] No backend files modified; `git status --short` shows only `frontend/src/App.tsx` and `frontend/src/App.test.tsx` changes (step 8) and existing backend tests still pass (step 9).
</content>
</invoke>
