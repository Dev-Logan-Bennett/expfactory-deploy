# Fork resync, CONTRIBUTING.md, and first upstream PR — Design

**Date:** 2026-04-23
**Author:** Logan Bennett (lobennett) with Claude
**Status:** Approved by user — ready to implement

## Goal

Three related pieces of work, executed in order:

1. Move the user's 7 divergent commits off `main` onto a preservation branch, then sync both local `main` and the fork's `origin/main` with `upstream/main` (`expfactory/expfactory-deploy`).
2. Write a `CONTRIBUTING.md` at repo root modeled on [DataLad's CONTRIBUTING guide](https://github.com/datalad/datalad/blob/maint/CONTRIBUTING.md), using DataLad's exact branch/commit prefix conventions, adapted to this project.
3. Run the project locally (via podman), fix a small HTML typo on a topic branch following the new conventions, and stage a PR to upstream.

## Non-goals

- Pushing anything to `upstream` (`expfactory/expfactory-deploy`). The user does not have write access there, and the user has explicitly stated that the upstream main hosts the live site and must not receive force-pushes or direct pushes from this workflow. All contributions go fork → PR.
- Installing Docker, Podman, or podman-machine dependencies. Podman 5.8.1 is already present.
- Migrating away from `README.rst` to `README.md`. The user referred to "README.md" conversationally but the actual file is `README.rst`; keep as-is.
- Refactoring anything on `local.yml`, the template files, or the preserved commits beyond what this spec covers.

## Current state (pre-implementation)

- `origin` = `https://github.com/lobennett/expfactory-deploy.git` (user's fork)
- `upstream` = `https://github.com/expfactory/expfactory-deploy.git` (live site, no write access)
- Local `main` tip: `69d3417`, 7 commits ahead of merge base `e35147f`
- `upstream/main` tip: `d475ddd`, ~30 commits ahead of merge base; no conflicts with local main
- 7 commits on local main (to be preserved): polars→pandas migration, fmri utils, local data save helpers, port-collision fix, multi-static-dir serving by port
- `CONTRIBUTING.md` does not exist
- Stray untracked: `uv.lock` (from prior uv attempt) and `.venv/` (gitignored). Both to be deleted.
- `.envs/` does not exist; README-prescribed env files must be created.
- No podman machine exists (`podman machine list` empty).

## Section 1 — Git resync

### Operation sequence

1. `git switch -c nf-fmri-local-exports` — creates preserve branch at current `main` tip (`69d3417`), capturing all 7 divergent commits plus this spec commit (see Spec-commit placement below).
2. `git push -u origin nf-fmri-local-exports` — safety net: commits durable on `origin` before any destructive op.
3. `git fetch upstream`.
4. `git switch main && git reset --hard upstream/main` — local `main` now at `d475ddd`.
5. `git push --force-with-lease origin main` — fork's main mirrors upstream. `--force-with-lease` refuses the push if `origin/main` changed unexpectedly since the last fetch.
6. `git branch --set-upstream-to=upstream/main main` — local `main` tracks `upstream/main`, so future `git pull` on main brings upstream changes.

### Guarantees

- Preserved: all 7 commits on `origin/nf-fmri-local-exports` and local `nf-fmri-local-exports`.
- Unchanged: `upstream` remote; live site untouched.
- Changed: local `main` → `d475ddd`; `origin/main` → `d475ddd`.
- Destroyed: divergent history on `origin/main`. Commits themselves preserved on the preserve branch.

### Spec-commit placement

This spec file is committed on **current** `main` (pre-reset). Because Section 1 step 1 creates `nf-fmri-local-exports` at current HEAD *after* this commit, the spec rides onto the preserve branch naturally. After step 4's reset, `main` no longer contains the spec — which is correct, because this spec is not upstream-contribution material; it is a personal planning artifact that belongs on the fork's personal branch.

### Verification after step 6

```bash
git log --oneline -3
git log origin/nf-fmri-local-exports --oneline -8
git rev-parse main upstream/main origin/main
```

Expected: three identical SHAs at `d475ddd`; preserve branch shows 7 commits + spec commit + merge-base parent.

## Section 2 — CONTRIBUTING.md

### Location

Repo root (`./CONTRIBUTING.md`). GitHub auto-links this on the PR creation page.

### Attribution

Include near the top:

> Much of this document's structure and conventions (branch prefixes, commit prefixes, fork + PR workflow) are adapted from [DataLad's CONTRIBUTING guide](https://github.com/datalad/datalad/blob/maint/CONTRIBUTING.md). Thanks to the DataLad maintainers.

### Structure

1. **Welcome** — 2 lines: Django project for experiment battery deployment; how to get help (open an issue on `expfactory/expfactory-deploy`).
2. **Attribution** — see above.
3. **Development setup** — one-line summary; pointer to `README.rst` for full instructions.
4. **Fork-based workflow**
   - `origin` = your fork, `upstream` = `expfactory/expfactory-deploy`.
   - Topic branches off local `main` (which tracks `upstream/main`).
   - PRs target `expfactory/expfactory-deploy:main`.
5. **Branch naming** — DataLad prefixes, hyphen-separated lowercase topic:

   | Prefix | Meaning |
   |---|---|
   | `nf-` | New feature |
   | `bf-` | Bug fix |
   | `rf-` | Refactor |
   | `doc-` | Documentation |
   | `bm-` | Benchmarks |

   Example: `bf-preview-instructions-typo`.
6. **Commit message format** — DataLad prefixes:

   | Prefix | Meaning |
   |---|---|
   | `NF:` | New feature |
   | `BF:` | Bug fix |
   | `RF:` | Refactor |
   | `DOC:` | Documentation |
   | `BM:` | Benchmarks |
   | `TST:` | Tests only |
   | `CI:` | Continuous integration |
   | `UX:` | User-facing polish |
   | `BK:` | Known breakage |

   - Combinable with `+`: `RF+DOC: ...`
   - Scoping: `BF(TST): ...`
   - Close issues with footer: `Closes #123`.
7. **Before opening a PR** — checklist: main in sync with `upstream/main`; pre-commit passes (`.pre-commit-config.yaml` exists); migrations included if models changed; tests pass (`podman compose -f local.yml run --rm django ./manage.py test`).
8. **Opening the PR** — target branch `expfactory/expfactory-deploy:main`; describe what/why; link issues.
9. **After merge** — delete the topic branch on your fork; sync your fork's main from upstream.

### Deliberately omitted (not applicable)

- DataLad's semver labels.
- Release branch strategy (expfactory doesn't expose `maint` to contributors).
- Type-check / line-length rules (the repo has `.pre-commit-config.yaml` with ruff — reference it, don't restate).
- DataLad's test decorator list.

### Length target

120–150 lines. DataLad's is ~400 and heavily tooling-specific.

## Section 3 — Local setup (podman)

### Pre-flight

- `podman 5.8.1` installed ✅
- `podman compose` subcommand works (VM not yet started) ✅
- No existing podman machine — must `init` + `start`
- Ports 80 and 8000 free ✅
- `deployment_assets/repos/expfactory-experiments` does not exist; bind mount in `local.yml` will need this path to be present (some compose runtimes error on missing bind mount sources). Create as empty dir if needed.

### Sequence

1. **Init + start podman machine** (one-time):
   ```
   podman machine init
   podman machine start
   ```
2. **Make machine rootful** so nginx can bind host port 80 (matches README's `http://localhost` expectation; no `local.yml` edits needed):
   ```
   podman machine stop
   podman machine set --rootful
   podman machine start
   ```
3. **Create env files** (`.envs/` is already in `.gitignore`):
   ```
   # .envs/.local/.postgres
   POSTGRES_HOST=postgres
   POSTGRES_PORT=5432
   POSTGRES_DB=expfactory
   POSTGRES_USER=expfactory
   POSTGRES_PASSWORD=devpassword

   # .envs/.local/.django
   USE_DOCKER=yes
   IPYTHONDIR=/app/.ipython
   REDIS_URL=redis://redis:6379/0
   CELERY_FLOWER_USER=flower
   CELERY_FLOWER_PASSWORD=devpassword
   ```
   Note: `redis` and `celery*` services are commented out in `local.yml`. The `REDIS_URL` and `CELERY_FLOWER_*` env vars are inert but harmless — kept to match README's exact list.
4. **Clean stray files**:
   ```
   rm uv.lock
   rm -rf .venv
   ```
5. **Create empty experiments path if missing**:
   ```
   mkdir -p deployment_assets/repos/expfactory-experiments
   ```
6. **Build**:
   ```
   podman compose -f local.yml build
   ```
7. **Migrate**:
   ```
   podman compose -f local.yml run --rm django ./manage.py makemigrations
   podman compose -f local.yml run --rm django ./manage.py migrate
   ```
8. **Create superuser non-interactively**:
   ```
   podman compose -f local.yml run --rm \
     -e DJANGO_SUPERUSER_USERNAME=admin \
     -e DJANGO_SUPERUSER_EMAIL=admin@example.com \
     -e DJANGO_SUPERUSER_PASSWORD=devpassword \
     django ./manage.py createsuperuser --noinput
   ```
9. **Start stack detached**:
   ```
   podman compose -f local.yml up -d
   ```
10. **Smoke tests**:
    - `podman compose -f local.yml ps` → django, postgres, nginx, q2worker all `Up`
    - `curl -sI http://localhost/admin/` → 302 redirect to login
    - User opens `http://localhost/admin/` in browser, logs in as `admin / devpassword`

### Template hot-reload

`local.yml` mounts the entire repo (`.:/app:z`) into the django and nginx containers. Template edits are picked up on next request without a rebuild or restart.

### Known risks + fallbacks

- **Podman Compose parity gaps.** If `podman compose` rejects something in `local.yml`, surface the exact error and decide whether to adjust `local.yml` locally (not committed) or install a different compose variant.
- **Image pull rate limits.** If Docker Hub throttles, retry or `podman login docker.io`. Not to be done without user confirmation.
- **Rootful mode doesn't stick.** Fall back: edit `local.yml` to map nginx to host `8080`, add `local.yml` to `.git/info/exclude` so the edit doesn't pollute PRs.

### Actions requiring explicit user approval

- Switching podman machine to rootful mode (destroys/recreates connection context).
- Running any non-interactive `createsuperuser` with a different password than `devpassword`.
- `podman login` against any registry.

## Section 4 — Typo fix and PR

### The change

Fix `Insturcitons` → `Instructions` in two templates:

- `expfactory_deploy/templates/experiments/battery_form.html:13`
- `expfactory_deploy/templates/experiments/battery_detail.html:15`

Both currently read `Preview Insturcitons/Consent` → should read `Preview Instructions/Consent`.

### Branch and commit

- Branch: `bf-preview-instructions-typo`
- Commit: `BF: fix typo "Insturcitons" → "Instructions" on battery pages`

### Workflow

1. Starting point: local `main` = `upstream/main` (post Section 1).
2. `git switch -c bf-preview-instructions-typo`
3. Apply exact string swap in both files (no other edits).
4. `git add` the two files explicitly (not `-A`).
5. `git commit -m 'BF: fix typo "Insturcitons" → "Instructions" on battery pages'`
6. `git push -u origin bf-preview-instructions-typo`

### Verification

- With the Section 3 stack running, refresh any battery detail or form page; confirm the button now reads `Preview Instructions/Consent`.
- If no batteries exist in the dev DB, create one via `/admin/` to have a page to visit. Optional — the text diff is obviously correct.

### PR creation

- **Precondition:** local verification (above) has succeeded; both pages show `Preview Instructions/Consent`.
- Base: `expfactory:main`; head: `lobennett:bf-preview-instructions-typo`.
- Title: `BF: fix typo "Insturcitons" → "Instructions" on battery pages`
- Body:
  ```
  Two battery template buttons had a typo in their label:
  `Preview Insturcitons/Consent` → `Preview Instructions/Consent`.

  Files changed:
  - expfactory_deploy/templates/experiments/battery_form.html
  - expfactory_deploy/templates/experiments/battery_detail.html
  ```
- Command:
  ```
  gh pr create \
    --repo expfactory/expfactory-deploy \
    --base main \
    --head lobennett:bf-preview-instructions-typo \
    --title 'BF: fix typo "Insturcitons" → "Instructions" on battery pages' \
    --body-file <drafted-body.md>
  ```
- Only runs on explicit user approval. PR creation is externally visible and notifies upstream maintainers.

### Explicit non-goals

- No adjacent cleanup in the two template files.
- No tests added.
- No `collectstatic` (template files are not static assets in Django).
