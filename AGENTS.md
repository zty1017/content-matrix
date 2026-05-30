# AGENTS.md — Douyin URL Resolver Experiment Worktree

This local worktree is for autonomous exploration of extracting usable video information from Douyin share URLs.

## Branch and workspace

- Worktree path: `/home/zty/projects/douyinHackathon/content-matrix-douyin`
- Branch: `experiment/douyin-url-resolver`
- Remote: `origin/experiment/douyin-url-resolver`
- This is an experiment branch, not the P0-A delivery path.

## Mission

Explore whether a Douyin share URL can be resolved into a normalized source result that may include:

- canonical URL;
- title or caption;
- author/display name if safely available;
- cover image URL if safely available;
- video metadata or playable URL if safely available;
- failure reason when resolution is blocked or unsupported.

The success criterion is not universal Douyin parsing. Success means: for a small local test set, attempt resolution and always return either a normalized result or a controlled error without breaking fixture fallback.

## Hard boundaries

- Do not promise stable parsing of arbitrary Douyin URLs.
- Do not break preset/fixture source resolution.
- Do not change frontend branches from this worktree.
- Do not change core domain models unless the user explicitly moves the change through `contract/v0.1-p0a-contract`.
- Do not let third-party library response shapes leak into Pydantic domain models.
- Do not add production database, auth, vector search, async queue, Docker, or deployment work here.
- Do not commit secrets, cookies, tokens, browser profiles, raw private links, or downloaded media.

## Git safety

Before editing, run and inspect:

```bash
git status
git branch --show-current
git pull origin experiment/douyin-url-resolver
```

If the branch is not `experiment/douyin-url-resolver`, stop.

Do not use:

```bash
git push --force
git reset --hard
git rebase
```

unless the user explicitly asks.

Before committing, show:

```bash
git status
git diff
```

Use focused conventional commits such as:

```text
exp: add douyin url resolver probe
test: cover douyin resolver fallback errors
docs: document douyin resolver experiment limits
```

## Integration target

Prefer integrating through the existing source-resolution boundary:

- `backend/app/api/v1/source.py` — `POST /api/v1/source/resolve`;
- `backend/app/services/source_resolver.py` — `SourceResolver.resolve()` and `_extract_douyin_identifier()`;
- `backend/app/repositories/json_repository.py` — source mapping fixture/runtime lookup;
- `backend/app/services/asset_builder.py` — source-to-asset construction;
- `backend/app/services/task_state.py` — task creation source-type validation;
- `backend/app/core/errors.py` and `backend/app/schemas/errors.py` — unified error envelope;
- `backend/tests/test_source_asset_api.py`, `backend/tests/test_error_contract.py`, and `backend/tests/test_task_card_snapshot_api.py` — regression tests.

Keep all experimental parsing behind an adapter boundary so it can be removed without affecting P0-A.

Existing source enums already include public `douyin_url` input and asset `douyin_link` source type. Do not add new enum values unless the user first moves that decision through the contract branch.

## File boundaries

Allowed experiment surfaces:

- `backend/app/services/source_resolver.py` for resolver dispatch and fixture-safe Douyin identifier extraction.
- New isolated service modules under `backend/app/services/` for optional resolver adapters.
- `backend/app/services/asset_builder.py` only when source-to-asset hydration must preserve the existing contract.
- `backend/app/services/task_state.py` only when source-type validation needs experiment-safe compatibility.
- Fixture additions in `backend/app/data/fixtures/source_mappings.json` or `backend/app/data/fixtures/video_content_assets.json` only if the existing schema shape stays unchanged.
- New or extended tests under `backend/tests/`, especially resolver and fallback tests.
- Experiment notes under `docs/experiments/`.

Contract-critical files require explicit user approval and should normally move through `contract/v0.1-p0a-contract` first:

- `backend/app/schemas/*.py`;
- `backend/app/core/errors.py`;
- `backend/app/core/config.py`;
- `backend/app/api/v1/*.py`;
- `backend/app/api/error_handlers.py`;
- `backend/app/main.py`;
- `backend/pyproject.toml`;
- `backend/app/repositories/json_repository.py`;
- existing guardrail tests such as `backend/tests/test_error_contract.py`, `backend/tests/test_domain_schemas.py`, `backend/tests/test_docs_contract.py`, `backend/tests/test_fixture_repository.py`, and `backend/tests/test_task_card_snapshot_api.py`.

If a contract-critical change seems necessary, stop implementation and document the exact required contract change, rationale, and compatibility risk for review.

## Error and fallback rules

- Resolution failure must be expected behavior, not an unhandled exception.
- Return controlled errors compatible with the existing API error contract.
- Preserve mock/fixture behavior for known preset sources.
- Add tests proving fixture fallback still works after experiment changes.
- If real Douyin access fails due to anti-bot, region, login, network, or format changes, document it and degrade gracefully.
- The experiment should be metadata-only by default. Do not download or store video files.
- Prefer a feature flag such as `DOUYIN_RESOLVER_ENABLED=false` by default.
- Use aggressive timeouts and low request volume. A safe starting limit is no more than 5 requests per minute during manual experiments.

## Research rules

- Prefer official/public behavior and reputable open-source examples.
- Treat third-party scrapers as unstable references, not guaranteed dependencies.
- Prefer stable extraction boundaries such as short-link normalization, `aweme_id` extraction, SSR/HTML metadata parsing, or battle-tested libraries.
- Useful references to evaluate include `yt-dlp`, `parse-video-py`, and `Evil0ctal/Douyin_TikTok_Download_API`, but do not adopt any dependency without documenting license, maintenance status, and failure behavior.
- Document package names, URLs, observed behavior, and failure modes.
- Do not bypass paywalls, authentication, platform protections, or private content restrictions.
- Do not attempt CAPTCHA bypass, mass scraping, proxy rotation, or reverse-engineering signature algorithms unless the user explicitly narrows the task to a legal/ethical research spike.

## Verification expectations

After code changes, run relevant checks such as:

```bash
uv run pytest
uv run pytest backend/tests
```

If commands fail because the environment is missing dependencies, report the exact failure. Do not delete failing tests to pass validation.

Also inspect changed files before pushing:

```bash
git diff --name-only
```

If forbidden or contract-critical files appear unexpectedly, stop and explain why they were touched.

## Documentation expectation

Keep experiment notes in a dedicated doc, for example:

```text
docs/experiments/douyin-url-resolver.md
```

Record:

- tested URL categories;
- approach attempted;
- libraries or HTTP patterns tested;
- success/failure examples without secrets;
- recommended next step;
- why the P0-A fixture fallback remains safe.
