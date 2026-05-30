# AGENTS.md — Mobile Web Demo Branch

This branch is for the mobile/H5 frontend demo.

This guidance is branch-specific. Do not copy it into backend or contract branches.

## Branch responsibility

- Branch: `feature/mobile-web-demo`
- Build a phone-sized mobile web experience for the P0-A demo.
- Reuse the same backend Mock/fixture API and card schema as the main web demo.
- Mobile UI may look different, but the business data and meanings must stay identical.
- Focus on a smooth demo path rather than broad feature coverage.

## Before any work

Run these checks and show the result to the user before editing:

```bash
git status
git branch --show-current
git pull origin feature/mobile-web-demo
```

If the current branch is not `feature/mobile-web-demo`, stop and ask before continuing.

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
git push origin feature/mobile-web-demo
```

- Open a GitHub PR only when the user asks.
- If Git reports a merge conflict, stop and show the conflict summary instead of guessing.

## Contract rules

- Do not change backend API contracts in this branch.
- Do not change Pydantic domain models in this branch.
- Do not change fixture schema in this branch.
- Do not invent mobile-only backend fields.
- If a field is missing, document the needed field and ask for a contract update.
- Use the same API client/types as the main web frontend when they exist.

## Frontend bootstrap warning

The v0 `main` branch may contain a backend guardrail test that intentionally forbids real frontend framework files such as `frontend/package.json`, `frontend/src/`, `vite.config.*`, `next.config.*`, `tsconfig.json`, or Tailwind config files. If this branch initializes a real frontend framework, coordinate with the backend owner before changing that guardrail. Do not silently delete backend tests.

## Product rules

- The mobile demo must consume backend data, not hardcoded business results.
- Do not bypass the `ReconstructionTask` model.
- Do not hardcode historical asset influence results in the UI.
- Do not store `session_context` as a `VideoContentAsset.fact`.
- Always distinguish:
  - video evidence;
  - historical asset evidence;
  - AI inference;
  - items needing user confirmation.

## Mobile implementation guidance

- Design for phone width first.
- TypeScript is allowed and preferred for frontend work.
- Do not create an independent TypeScript domain model that disagrees with the backend contract.
- Prefer generating or deriving TypeScript types from `/openapi.json` once the frontend toolchain is ready.
- If manual types are needed temporarily, keep them in one API/types module and mirror `docs/api-contract.md` exactly.
- Do not use `as any`, `@ts-ignore`, or `@ts-expect-error` to bypass contract mismatches; record the missing field as a contract need instead.
- Keep the P0-A flow obvious: source, user context, decision card, evidence, save.
- Avoid creating a separate mobile business logic layer.
- Prefer reusable components and shared types where possible.
- Add loading, error, and empty states so the demo does not look broken during presentation.
- Use clear Chinese labels and short mobile-friendly copy.

## Validation before handoff

Run the relevant available checks before pushing, for example:

```bash
npm run build
npm run lint
npm test
```

If a command does not exist, report that it does not exist. Do not delete failing tests to pass validation.
