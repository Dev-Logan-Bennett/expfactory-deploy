# Design: `expfactory_deploy_local` cleanup, README, and git hygiene

**Date:** 2026-06-01
**Status:** Approved (brainstorming)
**Scope:** Project A of a 4-project decomposition (A: module cleanup + git; B: Supabase/auto-push/validation; C: counterbalancing workflow; D: experiments README + Karabiner).

## Goal

Refactor the production `expfactory_deploy_local` web.py module for clarity and testability **without changing its runtime behavior or CLI**, document it with a README, get the production code onto `main`, and tidy the repository's branches.

This module runs live RDoC fMRI data collection. The CLI interface (`-e -c -gi -sub -ses -run -raw -bids`) is consumed by `rdoc-fmri-experiments/setup.py` and `run.sh` and **must stay byte-identical**. Behavior preservation is a hard requirement, proven by tests plus a manual launch check before merge.

## Background / current state

- Package: `expfactory_deploy_local` (web.py + Jinja2 + pandas), editable-installed into the experiments repo's venv. 8 tracked source files; no tests.
- The serving flow: `serve.run()` parses args, symlinks experiments into `static/experiments/`, starts a web.py app scanning ports 8080→9999, serves experiments one at a time from session state, and on POST saves a raw JSON (always) and a BIDS events CSV (only for `__fmri` experiments).
- Output layout produced today (the contract tests will lock in):
  - raw: `<raw_dir>/sub-<id>/ses-<ses>/sub-<id>_ses-<ses>_run-<run>_task-<expID>_dateTime-<unix>.json`
  - bids: `<bids_dir>/sub-<id>/ses-<ses>/func/sub-<id>_ses-<ses>_run-<run>_task-<expID>.csv` (only when `__fmri` in the experiment stem)
  - Any of sub/ses/run absent → that segment is omitted from filename and directory nesting.
- Git: `main` and the production branch `nf-fmri-local-exports` have **diverged** (main has an upstream "static files route" commit; production has all the fMRI module work). Production also carries unrelated *expdeploy* planning docs (that project now lives in its own directory).

## Known bugs (fix as part of cleanup)

1. **`-c/--config` crashes.** `serve.run()` reads `args.exp_config`, but the argparse dest is `config` → `AttributeError`. Only the `-e/--exps` path works today.
2. **`decline.GET(self, name)`** takes a `name` argument the `/decline` route never supplies → would error if hit.
3. **Debug noise:** `preprocess.raw_to_df` prints the entire raw payload (`print(raw_data)`).
4. **Dead code / stale comments:** the "Move exp_config into the mutually exclusive group…" comment, polars remnants.

## Target module structure

Keep `serve.py` as the web entry point (web.py resolves handler classes from module globals), but extract tangled logic into focused, testable units:

```
src/expfactory_deploy_local/
  cli.py         # entry point + tempsymlink (behavior unchanged)
  serve.py       # web app, urls, handlers (serve/decline/reset), run(), arg parser wiring
  config.py      # argparse parser + typed RunConfig (subject/session/run/raw_dir/bids_dir/group_index)
  paths.py       # build_raw_path(), build_bids_path() — PURE, fully tested
  storage.py     # save_raw(), save_bids_events() — write orchestration
  preprocess.py  # raw_to_df (cleaned; debug prints removed)
  utils.py       # generate_experiment_context (cleaned, typed)
  templates/  static/
tests/
  test_preprocess.py
  test_paths.py
  test_storage.py
```

After extraction, the POST handler reduces to: `data → raw_to_df → save_raw → (if __fmri) save_bids_events → respond`.

### Unit responsibilities

- **`paths.py`** — pure functions mapping `(RunConfig, exp_id, exp_stem, timestamp)` to the raw path and (when `__fmri`) the bids path, replicating today's omit-when-absent rules. No I/O. This is the highest-value extraction (it's where the s11/s4 mislabeling-class bugs originate).
- **`storage.py`** — takes the computed paths, creates directories, writes the raw bytes and the events CSV. Thin, side-effecting, tested against `tmp_path`.
- **`config.py`** — one place that defines the parser and returns a typed `RunConfig`; `serve.run()` consumes it. Fixes bug #1 by construction.

## Tests (pytest, new `tests/`)

- `test_preprocess.py` — `raw_to_df` across input shapes: bytes vs str, `exp_id` in the top-level dict vs inside trialdata vs missing (→ `"unknown"`), list-vs-Series exp_id handling.
- `test_paths.py` — `build_raw_path`/`build_bids_path` for every combination of sub/ses/run present-or-absent, and `__fmri` vs non-`__fmri` (bids only emitted for `__fmri`).
- `test_storage.py` — round-trip writes into `tmp_path`, asserting exact directory structure and filenames (the behavior contract).

## Module README (`expfactory_deploy_local/README.md`)

- Install via uv (editable), Python ≥ 3.11.
- CLI reference for every flag, with examples (single `-e` experiment; `-c` config file).
- The output layout it produces (raw JSON always; bids events CSV only for `__fmri`), with the exact naming rules.
- How `rdoc-fmri-experiments` invokes it (pointer; full launch workflow is Project D).

## Packaging / gitignore

- Add `sessions_*/` to gitignore (web.py session stores; currently untracked-but-noisy). `.venv` already ignored at root.
- Commit `expfactory_deploy_local/uv.lock` for reproducibility.
- Bump `requires-python` to `>=3.11` (matches the 3.12 venv reality); keep MIT license and existing author attribution.

## Git plan

1. Work happens on branch **`nf-module-cleanup`** (already created off `nf-fmri-local-exports`); this design doc is its first commit.
2. Implement refactor + tests + README + gitignore there. **Delete** the two superseded expdeploy docs (`docs/superpowers/plans/2026-05-14-expdeploy-bootstrap.md`, `docs/superpowers/specs/2026-05-14-expdeploy-design.md`) via a normal `git rm` commit; **keep** `2026-04-23-fork-sync-contributing-and-typo-fix-design.md`.
3. Verify: `pytest` green **and** a real local launch still saves raw+bids correctly.
4. **Merge `nf-module-cleanup` → `main`** — one merge reconciles the divergence (its ancestry already includes all production commits; main's "static files route" commit is preserved). `main` becomes the production branch going forward.
5. **Prune branches** (confirm before pushing deletions): delete `origin/patch-1..7`, `origin/add_args`, `origin/web_context`. **Keep** `doc-contributing` + `bf-codespell-typos` (pending upstream PRs). `upstream/*` is read-only.

## Non-goals / safety

- No change to the serving flow, output format/naming, port-scanning, session handling, or web.py itself.
- No subject/session **validation** here — that belongs to Project B (it directly addresses the data-quality issues found in the corpus audit).
- Branch deletion is outward-facing; confirm with the user before `git push --delete`.

## Validation criteria

- All CLI flags behave exactly as before; `setup.py`/`run.sh` run unmodified.
- `pytest` passes; path/preprocess/storage behavior matches pre-refactor output byte-for-byte.
- A manual launch of one `__fmri` and one non-`__fmri` experiment writes the same files as before.
- `main` contains the production module + cleanup; expdeploy docs gone; branches pruned.
