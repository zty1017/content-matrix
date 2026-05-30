# AGENTS.md — P0-A Web Demo Branch

This branch is for the main P0-A Web Demo frontend.

This guidance is branch-specific. Do not copy it into backend or contract branches.

## Branch responsibility

- Branch: `feature/p0a-web-demo`
- Build the primary web demo that judges can open and understand.
- Consume the existing Mock/fixture API from the backend.
- Show the complete P0-A decision-card flow:
  - video/source selection;
  - demo user context selection;
  - fixed `session_context`;
  - `ReconstructionTask` creation/result display;
  - stable facts;
  - related historical assets;
  - `influence_type` as `supplement`, `preference_adaptation`, or `conflict_warning`;
  - evidence, uncertainty, and save-snapshot behavior.

## Before any work

Run these checks and show the result to the user before editing:

```bash
git status
git branch --show-current
git pull origin feature/p0a-web-demo
```

If the current branch is not `feature/p0a-web-demo`, stop and ask before continuing.

## Git and GitHub rules

- Do not develop directly on `main`.
- Do not force-push.
- Do not use `git reset --hard` unless the user explicitly asks.
- Do not rewrite history with rebase unless the user explicitly asks.
- Keep commits focused and explain what changed.
- Before committing, show:
  - `git status`
  - `git diff`
- After committing, push with:

```bash
git push origin feature/p0a-web-demo
```

- Open a GitHub PR into `main` or the contract branch only when the user asks.
- If Git reports a merge conflict, stop and show the conflict summary instead of guessing.

## Contract rules

- Do not change backend API contracts in this branch.
- Do not change Pydantic domain models in this branch.
- Do not change fixture schema in this branch.
- Do not invent frontend-only backend fields.
- If a field is missing, document the needed field and ask for a contract update.
- Frontend rendering may reshape data locally for display, but must not change business meaning.

## Frontend bootstrap warning

The v0 `main` branch may contain a backend guardrail test that intentionally forbids real frontend framework files such as `frontend/package.json`, `frontend/src/`, `vite.config.*`, `next.config.*`, `tsconfig.json`, or Tailwind config files. If this branch initializes a real frontend framework, coordinate with the backend owner before changing that guardrail. Do not silently delete backend tests.

## Product rules

- The web demo must use backend data, not hardcoded business results.
- Do not bypass the `ReconstructionTask` model.
- Do not hardcode historical asset influence results in the UI.
- Do not store `session_context` as a `VideoContentAsset.fact`.
- Always distinguish:
  - video evidence;
  - historical asset evidence;
  - AI inference;
  - items needing user confirmation.

## Frontend implementation guidance

- Prefer a small, stable demo over a broad unfinished UI.
- TypeScript is allowed and preferred for frontend work.
- Do not create an independent TypeScript domain model that disagrees with the backend contract.
- Prefer generating or deriving TypeScript types from `/openapi.json` once the frontend toolchain is ready.
- If manual types are needed temporarily, keep them in one API/types module and mirror `docs/api-contract.md` exactly.
- Do not use `as any`, `@ts-ignore`, or `@ts-expect-error` to bypass contract mismatches; record the missing field as a contract need instead.
- Keep API access in one client/module so mobile and other frontends can reuse the same contract.
- Add loading, error, and empty states for demo robustness.
- Use clear Chinese labels for the P0-A judging flow.
- If the backend is unavailable, use documented mock/fixture behavior only; do not create a separate fake business model.

## Validation before handoff

Run the relevant available checks before pushing, for example:

```bash
npm run build
npm run lint
npm test
```

If a command does not exist, report that it does not exist. Do not delete failing tests to pass validation.
