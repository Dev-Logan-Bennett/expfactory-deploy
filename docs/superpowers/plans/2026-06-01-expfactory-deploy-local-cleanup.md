# expfactory_deploy_local Cleanup Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Refactor the production `expfactory_deploy_local` web.py module into focused, tested units without changing its CLI or output behavior, document it, land it on `main`, and prune stale branches.

**Architecture:** Extract the tangled POST/path/save logic from `serve.py` into pure `paths.py`, side-effecting `storage.py`, and a typed `config.py`; cover them with pytest contract tests that lock in today's exact filenames/directories; then thin `serve.py` down to wiring. Behavior preservation is proven by tests + a manual launch before merge.

**Tech Stack:** Python ≥3.11, web.py, Jinja2, pandas, pytest, uv, git.

**Working branch:** `nf-module-cleanup` (already created off `nf-fmri-local-exports`). All work commits here; merged to `main` at the end.

---

## File structure

```
expfactory_deploy_local/
  pyproject.toml            # MODIFY: requires-python>=3.11, add pytest dev group
  .gitignore                # CREATE: ignore sessions_*/
  uv.lock                   # COMMIT (currently untracked)
  README.md                 # REWRITE: install + CLI + output layout
  src/expfactory_deploy_local/
    config.py               # CREATE: RunConfig + build_parser() (fixes -c bug)
    paths.py                # CREATE: pure path builders (the behavior contract)
    storage.py              # CREATE: save_raw(), save_bids_events()
    preprocess.py           # MODIFY: remove debug prints, add types
    serve.py                # MODIFY: thin handlers, wire config/paths/storage, fix decline
    utils.py                # MODIFY: light tidy (types/docstrings)
  tests/
    __init__.py             # CREATE
    test_config.py          # CREATE
    test_paths.py           # CREATE
    test_storage.py         # CREATE
    test_preprocess.py      # CREATE
docs/superpowers/
  plans/2026-05-14-expdeploy-bootstrap.md   # DELETE
  specs/2026-05-14-expdeploy-design.md      # DELETE
```

**Behavior contract (must be preserved exactly):**
- Filename prefix is built in order from whichever of subject/session/run are present: `sub-<id>_`, `ses-<ses>_`, `run-<run>_`.
- Raw file: `<prefix>task-<expID>_dateTime-<unix>.json`. Directory nesting under `raw_dir`: `sub-<id>/` then (if session) `ses-<ses>/`. **`run` never creates a directory level.** No `raw_dir` → write to CWD with just the filename.
- Bids events file: `<prefix>task-<expID>.csv`, written **only** when `bids_dir` is set AND the served experiment's stem contains `__fmri`. Directory nesting under `bids_dir`: `sub-<id>/` then (if session) `ses-<ses>/func/`, else `sub-<id>/func/`; no subject → `bids_dir/` directly.
- The raw/bids **filename** uses `exp_id` (from the POST payload via `raw_to_df`); the `__fmri` **gate** uses the served experiment's path stem (`exp_stem`). Keep these two inputs distinct.

---

## Task 1: Scaffolding — gitignore, uv.lock, pytest dev dependency

**Files:**
- Create: `expfactory_deploy_local/.gitignore`
- Modify: `expfactory_deploy_local/pyproject.toml`
- Commit (untracked): `expfactory_deploy_local/uv.lock`

- [ ] **Step 1: Create module .gitignore**

Create `expfactory_deploy_local/.gitignore`:

```gitignore
# web.py per-port session stores created at runtime
src/expfactory_deploy_local/sessions_*/
# virtualenv
.venv/
```

- [ ] **Step 2: Add pytest dev group and bump Python floor in pyproject.toml**

In `expfactory_deploy_local/pyproject.toml`, change `requires-python = ">=3.8"` to `requires-python = ">=3.11"`, and add this block after the `[project]` table:

```toml
[dependency-groups]
dev = ["pytest>=8"]
```

- [ ] **Step 3: Sync and confirm pytest is available**

Run: `cd expfactory_deploy_local && uv sync --group dev`
Expected: resolves and installs pytest into `.venv`.

- [ ] **Step 4: Commit**

```bash
git add expfactory_deploy_local/.gitignore expfactory_deploy_local/pyproject.toml expfactory_deploy_local/uv.lock
git commit -m "chore: gitignore sessions_*, add pytest dev group, py>=3.11, commit uv.lock"
```

---

## Task 2: `config.py` — typed RunConfig + parser (fixes the -c/--config bug)

**Files:**
- Create: `expfactory_deploy_local/src/expfactory_deploy_local/config.py`
- Create: `expfactory_deploy_local/tests/__init__.py` (empty)
- Test: `expfactory_deploy_local/tests/test_config.py`

- [ ] **Step 1: Create empty `tests/__init__.py`**

Create `expfactory_deploy_local/tests/__init__.py` with no content.

- [ ] **Step 2: Write the failing test**

Create `expfactory_deploy_local/tests/test_config.py`:

```python
from pathlib import Path
from expfactory_deploy_local.config import build_parser, RunConfig


def test_config_flag_parses_without_crashing():
    # Regression: run() used to read args.exp_config (dest is 'config') -> AttributeError
    args = build_parser().parse_args(["-c", "battery.txt"])
    assert args.config == Path("battery.txt")


def test_exps_flag_parses_comma_list():
    args = build_parser().parse_args(["-e", "a/exp1,b/exp2"])
    assert args.exps == [Path("a/exp1"), Path("b/exp2")]


def test_runconfig_from_args_collects_metadata():
    args = build_parser().parse_args(
        ["-e", "exp1", "-sub", "s1", "-ses", "1", "-run", "1",
         "-raw", "/r", "-bids", "/b", "-gi", "3"]
    )
    cfg = RunConfig.from_args(args)
    assert cfg.subject_id == "s1"
    assert cfg.session_num == "1"
    assert cfg.run_num == "1"
    assert cfg.raw_dir == "/r"
    assert cfg.bids_dir == "/b"
    assert cfg.group_index == "3"


def test_runconfig_defaults_are_none():
    args = build_parser().parse_args(["-e", "exp1"])
    cfg = RunConfig.from_args(args)
    assert cfg.subject_id is None and cfg.bids_dir is None and cfg.group_index is None
```

- [ ] **Step 3: Run test to verify it fails**

Run: `cd expfactory_deploy_local && uv run pytest tests/test_config.py -v`
Expected: FAIL with `ModuleNotFoundError: expfactory_deploy_local.config`.

- [ ] **Step 4: Write minimal implementation**

Create `expfactory_deploy_local/src/expfactory_deploy_local/config.py`:

```python
"""Argument parsing and typed run configuration for the local deployer."""

from __future__ import annotations

import argparse
from dataclasses import dataclass
from pathlib import Path
from typing import Optional


def build_parser() -> argparse.ArgumentParser:
    """Build the CLI parser. Flags are part of the public interface and must
    stay stable (consumed by rdoc-fmri-experiments setup.py and run.sh)."""
    parser = argparse.ArgumentParser(
        description="Start a local deployment of a battery"
    )
    group = parser.add_mutually_exclusive_group()
    group.add_argument(
        "-e",
        "--exps",
        help="Comma delimited list of paths to experiments. Mutually exclusive with --config.",
        type=lambda x: [Path(y) for y in x.split(",")],
    )
    group.add_argument(
        "-c",
        "--config",
        metavar="EXP_CONFIG",
        type=Path,
        help=(
            "Path to a single experiment, or to a config file listing one "
            "experiment path per line."
        ),
    )
    parser.add_argument(
        "-gi",
        "--group_index",
        help="Inject a group_index variable into the experiment context.",
    )
    parser.add_argument("-sub", "--subject_id", help="Subject ID")
    parser.add_argument("-ses", "--session_num", help="Session number")
    parser.add_argument("-run", "--run_num", help="Run number")
    parser.add_argument("-raw", "--raw_dir", help="Path to raw data output")
    parser.add_argument("-bids", "--bids_dir", help="Path to bids data output")
    return parser


@dataclass(frozen=True)
class RunConfig:
    """Run metadata parsed from the CLI; all optional."""

    subject_id: Optional[str] = None
    session_num: Optional[str] = None
    run_num: Optional[str] = None
    raw_dir: Optional[str] = None
    bids_dir: Optional[str] = None
    group_index: Optional[str] = None

    @classmethod
    def from_args(cls, args: argparse.Namespace) -> "RunConfig":
        return cls(
            subject_id=args.subject_id,
            session_num=args.session_num,
            run_num=args.run_num,
            raw_dir=args.raw_dir,
            bids_dir=args.bids_dir,
            group_index=args.group_index,
        )
```

- [ ] **Step 5: Run test to verify it passes**

Run: `cd expfactory_deploy_local && uv run pytest tests/test_config.py -v`
Expected: PASS (4 tests).

- [ ] **Step 6: Commit**

```bash
git add expfactory_deploy_local/src/expfactory_deploy_local/config.py expfactory_deploy_local/tests/__init__.py expfactory_deploy_local/tests/test_config.py
git commit -m "feat: add config.py (typed RunConfig + parser), fixing -c/--config crash"
```

---

## Task 3: `paths.py` — pure path builders (the behavior contract)

**Files:**
- Create: `expfactory_deploy_local/src/expfactory_deploy_local/paths.py`
- Test: `expfactory_deploy_local/tests/test_paths.py`

- [ ] **Step 1: Write the failing test**

Create `expfactory_deploy_local/tests/test_paths.py`:

```python
from pathlib import Path
from expfactory_deploy_local.config import RunConfig
from expfactory_deploy_local import paths


def test_filename_prefix_full():
    cfg = RunConfig(subject_id="s1", session_num="2", run_num="1")
    assert paths.filename_prefix(cfg) == "sub-s1_ses-2_run-1_"


def test_filename_prefix_partial_omits_absent():
    cfg = RunConfig(subject_id="s1")  # no session/run
    assert paths.filename_prefix(cfg) == "sub-s1_"
    assert paths.filename_prefix(RunConfig()) == ""


def test_raw_path_full_nesting():
    cfg = RunConfig(subject_id="s1", session_num="2", run_num="1", raw_dir="/r")
    p = paths.raw_path(cfg, exp_id="stroop_rdoc__fmri", timestamp="1700000000")
    assert p == Path("/r/sub-s1/ses-2/sub-s1_ses-2_run-1_task-stroop_rdoc__fmri_dateTime-1700000000.json")


def test_raw_path_subject_only_no_session_dir():
    cfg = RunConfig(subject_id="s1", run_num="1", raw_dir="/r")
    p = paths.raw_path(cfg, exp_id="stroop", timestamp="100")
    # run never creates a directory level; no session dir
    assert p == Path("/r/sub-s1/sub-s1_run-1_task-stroop_dateTime-100.json")


def test_raw_path_no_subject_dir():
    cfg = RunConfig(raw_dir="/r")
    p = paths.raw_path(cfg, exp_id="stroop", timestamp="100")
    assert p == Path("/r/task-stroop_dateTime-100.json")


def test_raw_path_no_raw_dir_is_cwd_filename():
    cfg = RunConfig(subject_id="s1")
    p = paths.raw_path(cfg, exp_id="stroop", timestamp="100")
    assert p == Path("sub-s1_task-stroop_dateTime-100.json")


def test_bids_path_full_nesting():
    cfg = RunConfig(subject_id="s1", session_num="2", run_num="1", bids_dir="/b")
    p = paths.bids_events_path(cfg, exp_id="stroop_rdoc__fmri")
    assert p == Path("/b/sub-s1/ses-2/func/sub-s1_ses-2_run-1_task-stroop_rdoc__fmri.csv")


def test_bids_path_subject_no_session_uses_func():
    cfg = RunConfig(subject_id="s1", bids_dir="/b")
    p = paths.bids_events_path(cfg, exp_id="stroop")
    assert p == Path("/b/sub-s1/func/sub-s1_task-stroop.csv")


def test_bids_path_no_subject():
    cfg = RunConfig(bids_dir="/b")
    p = paths.bids_events_path(cfg, exp_id="stroop")
    assert p == Path("/b/task-stroop.csv")


def test_should_write_bids_requires_dir_and_fmri_stem():
    cfg = RunConfig(bids_dir="/b")
    assert paths.should_write_bids(cfg, "stroop_rdoc__fmri") is True
    assert paths.should_write_bids(cfg, "stroop_rdoc") is False
    assert paths.should_write_bids(RunConfig(), "stroop_rdoc__fmri") is False
    assert paths.should_write_bids(cfg, "") is False
```

- [ ] **Step 2: Run test to verify it fails**

Run: `cd expfactory_deploy_local && uv run pytest tests/test_paths.py -v`
Expected: FAIL with `ModuleNotFoundError: expfactory_deploy_local.paths`.

- [ ] **Step 3: Write minimal implementation**

Create `expfactory_deploy_local/src/expfactory_deploy_local/paths.py`:

```python
"""Pure functions that map run metadata to output paths.

These encode the exact naming/nesting contract of the legacy POST handler:
- prefix order sub_, ses_, run_ (only those present)
- run never creates a directory level
- bids events written only for __fmri experiments
"""

from __future__ import annotations

from pathlib import Path

from .config import RunConfig


def filename_prefix(cfg: RunConfig) -> str:
    prefix = ""
    if cfg.subject_id:
        prefix += f"sub-{cfg.subject_id}_"
    if cfg.session_num:
        prefix += f"ses-{cfg.session_num}_"
    if cfg.run_num:
        prefix += f"run-{cfg.run_num}_"
    return prefix


def raw_path(cfg: RunConfig, exp_id: str, timestamp: str) -> Path:
    filename = f"{filename_prefix(cfg)}task-{exp_id}_dateTime-{timestamp}.json"
    if not cfg.raw_dir:
        return Path(filename)
    base = Path(cfg.raw_dir)
    if cfg.subject_id:
        base = base / f"sub-{cfg.subject_id}"
        if cfg.session_num:
            base = base / f"ses-{cfg.session_num}"
    return base / filename


def bids_events_path(cfg: RunConfig, exp_id: str) -> Path:
    filename = f"{filename_prefix(cfg)}task-{exp_id}.csv"
    base = Path(cfg.bids_dir) if cfg.bids_dir else Path()
    if cfg.subject_id:
        if cfg.session_num:
            base = base / f"sub-{cfg.subject_id}" / f"ses-{cfg.session_num}" / "func"
        else:
            base = base / f"sub-{cfg.subject_id}" / "func"
    return base / filename


def should_write_bids(cfg: RunConfig, exp_stem: str) -> bool:
    return bool(cfg.bids_dir) and bool(exp_stem) and "__fmri" in exp_stem
```

- [ ] **Step 4: Run test to verify it passes**

Run: `cd expfactory_deploy_local && uv run pytest tests/test_paths.py -v`
Expected: PASS (10 tests).

- [ ] **Step 5: Commit**

```bash
git add expfactory_deploy_local/src/expfactory_deploy_local/paths.py expfactory_deploy_local/tests/test_paths.py
git commit -m "feat: add paths.py pure path builders with contract tests"
```

---

## Task 4: `storage.py` — write orchestration

**Files:**
- Create: `expfactory_deploy_local/src/expfactory_deploy_local/storage.py`
- Test: `expfactory_deploy_local/tests/test_storage.py`

- [ ] **Step 1: Write the failing test**

Create `expfactory_deploy_local/tests/test_storage.py`:

```python
import pandas as pd
from expfactory_deploy_local.config import RunConfig
from expfactory_deploy_local import storage


def test_save_raw_writes_bytes_and_creates_dirs(tmp_path):
    cfg = RunConfig(subject_id="s1", session_num="2", run_num="1", raw_dir=str(tmp_path))
    out = storage.save_raw(cfg, exp_id="stroop__fmri", timestamp="100", data=b'{"a":1}')
    assert out.exists()
    assert out.read_bytes() == b'{"a":1}'
    assert out == tmp_path / "sub-s1/ses-2/sub-s1_ses-2_run-1_task-stroop__fmri_dateTime-100.json"


def test_save_bids_events_writes_csv(tmp_path):
    cfg = RunConfig(subject_id="s1", session_num="2", run_num="1", bids_dir=str(tmp_path))
    df = pd.DataFrame([{"trial": 1, "rt": 250}])
    out = storage.save_bids_events(cfg, exp_id="stroop__fmri", df=df)
    assert out.exists()
    assert out == tmp_path / "sub-s1/ses-2/func/sub-s1_ses-2_run-1_task-stroop__fmri.csv"
    reread = pd.read_csv(out)
    assert list(reread.columns) == ["trial", "rt"]
    assert len(reread) == 1
```

- [ ] **Step 2: Run test to verify it fails**

Run: `cd expfactory_deploy_local && uv run pytest tests/test_storage.py -v`
Expected: FAIL with `ModuleNotFoundError: expfactory_deploy_local.storage`.

- [ ] **Step 3: Write minimal implementation**

Create `expfactory_deploy_local/src/expfactory_deploy_local/storage.py`:

```python
"""Side-effecting writers that persist raw payloads and bids events files."""

from __future__ import annotations

import os
from pathlib import Path

import pandas as pd

from .config import RunConfig
from . import paths


def save_raw(cfg: RunConfig, exp_id: str, timestamp: str, data: bytes) -> Path:
    out = paths.raw_path(cfg, exp_id, timestamp)
    os.makedirs(out.parent, exist_ok=True)
    with open(out, "wb") as fp:
        fp.write(data)
    print(f"Saved raw data to: {out}")
    return out


def save_bids_events(cfg: RunConfig, exp_id: str, df: pd.DataFrame) -> Path:
    out = paths.bids_events_path(cfg, exp_id)
    os.makedirs(out.parent, exist_ok=True)
    df.to_csv(out, index=False)
    print(f"Saved BIDS events to: {out}")
    return out
```

- [ ] **Step 4: Run test to verify it passes**

Run: `cd expfactory_deploy_local && uv run pytest tests/test_storage.py -v`
Expected: PASS (2 tests).

- [ ] **Step 5: Commit**

```bash
git add expfactory_deploy_local/src/expfactory_deploy_local/storage.py expfactory_deploy_local/tests/test_storage.py
git commit -m "feat: add storage.py write orchestration with tmp_path tests"
```

---

## Task 5: `preprocess.py` — remove debug prints, add tests

**Files:**
- Modify: `expfactory_deploy_local/src/expfactory_deploy_local/preprocess.py`
- Test: `expfactory_deploy_local/tests/test_preprocess.py`

- [ ] **Step 1: Write the failing test**

Create `expfactory_deploy_local/tests/test_preprocess.py`:

```python
import json
import pandas as pd
from expfactory_deploy_local.preprocess import raw_to_df


def _payload(trials, exp_id=None):
    d = {"trialdata": json.dumps(trials)}
    if exp_id is not None:
        d["exp_id"] = exp_id
    return json.dumps(d).encode("utf-8")


def test_exp_id_from_top_level():
    df, exp_id = raw_to_df(_payload([{"a": 1}], exp_id="stroop__fmri"))
    assert exp_id == "stroop__fmri"
    assert isinstance(df, pd.DataFrame) and len(df) == 1


def test_exp_id_from_trialdata_when_absent_top_level():
    df, exp_id = raw_to_df(_payload([{"exp_id": "flanker__fmri"}, {"exp_id": "flanker__fmri"}]))
    assert exp_id == "flanker__fmri"


def test_exp_id_unknown_when_missing_everywhere():
    df, exp_id = raw_to_df(_payload([{"a": 1}]))
    assert exp_id == "unknown"


def test_accepts_str_path(tmp_path):
    p = tmp_path / "raw.json"
    p.write_text(json.dumps({"trialdata": json.dumps([{"a": 1}]), "exp_id": "x"}))
    df, exp_id = raw_to_df(str(p))
    assert exp_id == "x" and len(df) == 1
```

- [ ] **Step 2: Run test to verify it fails (or passes noisily)**

Run: `cd expfactory_deploy_local && uv run pytest tests/test_preprocess.py -v`
Expected: tests PASS but stdout shows the payload from the leftover `print(raw_data)`. (If `raw_to_df` already behaves correctly the prints are the only issue.)

- [ ] **Step 3: Remove the debug print(s)**

In `expfactory_deploy_local/src/expfactory_deploy_local/preprocess.py`, delete the line `print(raw_data)` near the top of `raw_to_df`. Keep the `"Warning: Could not determine exp_id..."` print (it is a genuine warning). The function body otherwise unchanged.

- [ ] **Step 4: Run tests and confirm clean output**

Run: `cd expfactory_deploy_local && uv run pytest tests/test_preprocess.py -v -s`
Expected: PASS (4 tests) with no payload dump in stdout.

- [ ] **Step 5: Commit**

```bash
git add expfactory_deploy_local/src/expfactory_deploy_local/preprocess.py expfactory_deploy_local/tests/test_preprocess.py
git commit -m "refactor: drop debug print in raw_to_df, add preprocess tests"
```

---

## Task 6: `serve.py` — thin handlers, wire config/paths/storage, fix decline

**Files:**
- Modify: `expfactory_deploy_local/src/expfactory_deploy_local/serve.py`

This task has no new unit test (web.py app wiring); correctness is guarded by Tasks 2–5 plus the manual launch in Task 10. Run the full suite after editing.

- [ ] **Step 1: Replace the parser block with config.build_parser**

In `serve.py`, remove the local `create_parser()` function and the module-level `parser = create_parser()`. Add to imports:

```python
from .config import build_parser, RunConfig
from . import storage
from .paths import should_write_bids
```

Then define near the top (after `app = web.application(...)`):

```python
parser = build_parser()
```

- [ ] **Step 2: Fix the args handling in run()**

In `run()`, replace the `args.exp_config` references. The experiments-selection block becomes:

```python
def run(args=None):
    args = parser.parse_args(args)
    if args.exps is not None:
        experiments = args.exps
    elif args.config is not None:
        if args.config.is_file():
            with open(args.config) as fp:
                experiments = [Path(x.strip()) for x in fp.readlines()]
        else:
            experiments = [args.config]
    else:
        parser.print_help()
        sys.exit()

    experiments = [e.absolute() for e in experiments if e.exists()]
    if len(experiments) == 0:
        print("No Experiments Found")
        sys.exit()
```

- [ ] **Step 3: Store a RunConfig on web.config instead of scattered keys**

Still in `run()`, after the symlink loop, replace the `config_updates`/`optional_params` block with:

```python
    web.config.update({"experiments": experiments})
    web.config.run_config = RunConfig.from_args(args)
    if args.group_index is not None:
        web.config.update({"group_index": args.group_index})
```

Leave the port-scanning `while` loop below unchanged.

- [ ] **Step 4: Rewrite serve.POST to use storage**

Replace the body of `serve.POST` with:

```python
    def POST(self):
        data = web.data()
        timestamp = str(int(datetime.datetime.now(datetime.timezone.utc).timestamp()))

        try:
            if not session.get("incomplete"):
                if getattr(web.config, "experiments", None):
                    session.incomplete = [*web.config.experiments]
            exp_name = session.incomplete.pop() if session.get("incomplete") else Path("unknown_experiment")
        except Exception as e:
            print(f"Error accessing session data: {e}")
            exp_name = Path("unknown_experiment")

        df, exp_id = raw_to_df(data)
        cfg = web.config.run_config
        storage.save_raw(cfg, exp_id, timestamp, data)

        exp_stem = getattr(exp_name, "stem", str(exp_name))
        if should_write_bids(cfg, exp_stem):
            storage.save_bids_events(cfg, exp_id, df)

        web.header("Content-Type", "application/json")
        return "{'success': true}"
```

- [ ] **Step 5: Fix the decline handler signature**

Replace the `decline` class with:

```python
class decline:
    def GET(self):
        app.stop()
```

- [ ] **Step 6: Remove dead code/comments**

Delete the stale comment `# Move exp_config into the mutually exclusive group AFTER creating it` (now gone with the parser move) and any now-unused locals. Ensure imports at top no longer reference removed names.

- [ ] **Step 7: Run the full test suite**

Run: `cd expfactory_deploy_local && uv run pytest -v`
Expected: PASS (all tests from Tasks 2–5).

- [ ] **Step 8: Import smoke check**

Run: `cd expfactory_deploy_local && uv run python -c "from expfactory_deploy_local import serve, cli; print('ok')"`
Expected: prints `ok` with no ImportError.

- [ ] **Step 9: Commit**

```bash
git add expfactory_deploy_local/src/expfactory_deploy_local/serve.py
git commit -m "refactor: thin serve.py via config/paths/storage; fix decline handler"
```

---

## Task 7: `utils.py` — light tidy

**Files:**
- Modify: `expfactory_deploy_local/src/expfactory_deploy_local/utils.py`

- [ ] **Step 1: Add type hints and a module note; no behavior change**

In `utils.py`, add return type `-> str` to `format_external_scripts` and `-> list` to `load_survey_tsv`, and `-> dict` to `generate_experiment_context`. Do not change logic.

- [ ] **Step 2: Run suite to confirm nothing broke**

Run: `cd expfactory_deploy_local && uv run pytest -v && uv run python -c "import expfactory_deploy_local.utils; print('ok')"`
Expected: PASS + `ok`.

- [ ] **Step 3: Commit**

```bash
git add expfactory_deploy_local/src/expfactory_deploy_local/utils.py
git commit -m "refactor: add type hints to utils.py (no behavior change)"
```

---

## Task 8: Module README

**Files:**
- Modify: `expfactory_deploy_local/README.md`

- [ ] **Step 1: Rewrite README.md**

Replace `expfactory_deploy_local/README.md` with content covering, in order:
1. One-line description (local jsPsych battery deployer that saves raw JSON + optional BIDS events CSV).
2. **Install:** `uv venv --python 3.12 && uv pip install -e /path/to/expfactory_deploy_local` (Python ≥3.11).
3. **CLI reference** — a table of every flag from `config.build_parser()`: `-e/--exps`, `-c/--config`, `-gi/--group_index`, `-sub/--subject_id`, `-ses/--session_num`, `-run/--run_num`, `-raw/--raw_dir`, `-bids/--bids_dir`. Note `-e` and `-c` are mutually exclusive.
4. **Examples:** single experiment (`expfactory_deploy_local -e path/to/exp -raw ./.output/raw -bids ./.output/bids -sub s1 -ses 1 -run 1`) and config file.
5. **Output layout** — the exact raw and bids paths/filenames (copy the contract from the plan's "Behavior contract"), and the rule that bids events are written only for `__fmri` experiments.
6. **Pointer** to `rdoc-fmri-experiments` for the full launch workflow (Project D).

- [ ] **Step 2: Commit**

```bash
git add expfactory_deploy_local/README.md
git commit -m "docs: rewrite module README (install, CLI, output layout)"
```

---

## Task 9: Delete superseded expdeploy docs

**Files:**
- Delete: `docs/superpowers/plans/2026-05-14-expdeploy-bootstrap.md`
- Delete: `docs/superpowers/specs/2026-05-14-expdeploy-design.md`

- [ ] **Step 1: Remove the two files**

```bash
git rm docs/superpowers/plans/2026-05-14-expdeploy-bootstrap.md docs/superpowers/specs/2026-05-14-expdeploy-design.md
```

(Keep `docs/superpowers/specs/2026-04-23-fork-sync-contributing-and-typo-fix-design.md` — that is this repo's upstream-contribution plan.)

- [ ] **Step 2: Commit**

```bash
git commit -m "docs: remove superseded expdeploy planning docs (project lives elsewhere)"
```

---

## Task 10: Integration verify, merge to main, prune branches

**Files:** none (git + manual verification)

- [ ] **Step 1: Full test suite**

Run: `cd expfactory_deploy_local && uv run pytest -v`
Expected: all PASS.

- [ ] **Step 2: Manual launch check — fMRI experiment writes raw + bids**

From the experiments repo venv, launch one `__fmri` experiment with `-raw`/`-bids`/`-sub`/`-ses`/`-run`, complete it in the browser, and confirm a raw JSON and a bids `func/…csv` appear with the expected names. Then launch one non-`__fmri` experiment and confirm only a raw JSON is written (no bids file).
Expected: filenames match the pre-refactor convention exactly.

- [ ] **Step 3: Merge cleanup branch into main**

```bash
git checkout main
git merge --no-ff nf-module-cleanup -m "Merge: expfactory_deploy_local cleanup + production module onto main"
```
Expected: merge succeeds (resolve any conflict in favor of the cleanup branch's module files; main's only unique change is the static-files-route commit, which does not touch the module).

- [ ] **Step 4: Push main**

```bash
git push origin main
```

- [ ] **Step 5: Prune branches (CONFIRM with user before running)**

```bash
git push origin --delete patch-1 patch-2 patch-3 patch-4 patch-5 patch-6 patch-7 add_args web_context
git remote prune origin
```
Keep `doc-contributing` and `bf-codespell-typos`. Do not touch `upstream/*`.

- [ ] **Step 6: Final state check**

Run: `git branch -a | cat`
Expected: `main` contains the cleaned module; deleted origin branches gone; `doc-contributing`, `bf-codespell-typos`, `nf-fmri-local-exports` retained.

---

## Self-review notes

- **Spec coverage:** module restructure (Tasks 2–7), `-c` bug (Task 2), decline bug + dead code + debug prints (Tasks 5–6), tests (Tasks 2–5), README (Task 8), gitignore/uv.lock/py-version (Task 1), expdeploy doc deletion (Task 9), merge-to-main + prune (Task 10). All spec sections mapped.
- **Behavior contract** is asserted byte-for-byte in `test_paths.py`/`test_storage.py` and re-checked manually in Task 10 Step 2.
- **Type/name consistency:** `RunConfig`, `build_parser`, `filename_prefix`, `raw_path`, `bids_events_path`, `should_write_bids`, `save_raw`, `save_bids_events` are used identically across tasks.
- **CLI stability:** every flag preserved in `config.build_parser()`; `setup.py`/`run.sh` need no changes.
