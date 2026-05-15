# expdeploy — Plan 1: Bootstrap + Serve Hello-World

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Bootstrap the new `expdeploy` repository and produce a working v0.1-alpha that can serve a canonical jsPsych v8 "hello world" experiment in the browser, accept its POSTed data, and save it to disk as raw JSON — with comprehensive tests at three tiers (unit, integration, Playwright e2e) and CI green.

**Architecture:** A pure-Python package built with `uv`. FastAPI app renders a Jinja template that injects a browser-native ES-module import map pointing at vendored jsPsych v8.2.3 assets. Experiments live in folders with a `manifest.toml` + ESM `index.js`. CLI is Typer-based. Storage in this plan is intentionally minimal — just an `FSAdapter` that writes the POSTed JSON to disk; full BIDS layout, SQLite catalog, batteries, counterbalance, and Supabase land in Plans 2 and 3.

**Tech Stack:** Python 3.11+ • uv • FastAPI • Pydantic v2 • Typer • Jinja2 • pytest • hypothesis • Playwright (Python) • ruff • mypy --strict • GitHub Actions • jsPsych v8.2.3 (vendored ESM).

**Source spec:** `/Users/lobennett/grants/r01_rdoc/projects/expfactory-deploy/docs/superpowers/specs/2026-05-14-expdeploy-design.md`.

**Target repo path:** `/Users/lobennett/grants/r01_rdoc/projects/expdeploy/` (does not exist yet — Task 1 creates it).

**Plan layout reminder:** the plan file currently lives in the *old* repo (`expfactory-deploy/docs/superpowers/plans/`). Task 1 copies the spec + this plan into the new repo so the new repo is self-contained from commit #1.

---

## Phase A — Repo bootstrap

### Task 1: Create the new repo directory and seed docs

**Files:**
- Create: `/Users/lobennett/grants/r01_rdoc/projects/expdeploy/` (directory)
- Create: `/Users/lobennett/grants/r01_rdoc/projects/expdeploy/docs/superpowers/specs/2026-05-14-expdeploy-design.md` (copy)
- Create: `/Users/lobennett/grants/r01_rdoc/projects/expdeploy/docs/superpowers/plans/2026-05-14-expdeploy-bootstrap.md` (copy)

- [ ] **Step 1: Create the directory tree**

```bash
mkdir -p /Users/lobennett/grants/r01_rdoc/projects/expdeploy/docs/superpowers/specs
mkdir -p /Users/lobennett/grants/r01_rdoc/projects/expdeploy/docs/superpowers/plans
mkdir -p /Users/lobennett/grants/r01_rdoc/projects/expdeploy/src/expdeploy/storage
mkdir -p /Users/lobennett/grants/r01_rdoc/projects/expdeploy/src/expdeploy/templates
mkdir -p /Users/lobennett/grants/r01_rdoc/projects/expdeploy/src/expdeploy/jspsych_assets
mkdir -p /Users/lobennett/grants/r01_rdoc/projects/expdeploy/tests/unit
mkdir -p /Users/lobennett/grants/r01_rdoc/projects/expdeploy/tests/integration
mkdir -p /Users/lobennett/grants/r01_rdoc/projects/expdeploy/tests/e2e
mkdir -p /Users/lobennett/grants/r01_rdoc/projects/expdeploy/tests/fixtures
mkdir -p /Users/lobennett/grants/r01_rdoc/projects/expdeploy/examples
mkdir -p /Users/lobennett/grants/r01_rdoc/projects/expdeploy/scripts
mkdir -p /Users/lobennett/grants/r01_rdoc/projects/expdeploy/.github/workflows
```

- [ ] **Step 2: Copy the spec and plan into the new repo**

```bash
cp /Users/lobennett/grants/r01_rdoc/projects/expfactory-deploy/docs/superpowers/specs/2026-05-14-expdeploy-design.md \
   /Users/lobennett/grants/r01_rdoc/projects/expdeploy/docs/superpowers/specs/2026-05-14-expdeploy-design.md

cp /Users/lobennett/grants/r01_rdoc/projects/expfactory-deploy/docs/superpowers/plans/2026-05-14-expdeploy-bootstrap.md \
   /Users/lobennett/grants/r01_rdoc/projects/expdeploy/docs/superpowers/plans/2026-05-14-expdeploy-bootstrap.md
```

- [ ] **Step 3: Verify the copies landed**

```bash
ls -la /Users/lobennett/grants/r01_rdoc/projects/expdeploy/docs/superpowers/specs/
ls -la /Users/lobennett/grants/r01_rdoc/projects/expdeploy/docs/superpowers/plans/
```

Expected: each directory contains exactly one `.md` file matching the names above.

---

### Task 2: Initial scaffold files (README, LICENSE, .gitignore)

**Files:**
- Create: `/Users/lobennett/grants/r01_rdoc/projects/expdeploy/README.md`
- Create: `/Users/lobennett/grants/r01_rdoc/projects/expdeploy/LICENSE`
- Create: `/Users/lobennett/grants/r01_rdoc/projects/expdeploy/.gitignore`

- [ ] **Step 1: Write `README.md`**

```markdown
# expdeploy

A modern Python deploy tool for [jsPsych v8](https://www.jspsych.org/) experiments.
Pays homage to [expfactory](https://github.com/expfactory) and expands its scope:
canonical jsPsych ESM authoring, BIDS-compliant data layout, batteries with
counterbalancing, and reproducibility via OCI containers.

**Status:** v0.1-alpha. Under active development; not yet stable.

## Quick start

```bash
uv tool install expdeploy
expdeploy run ./examples/hello_world --subject 01 --port 8080
# opens http://localhost:8080
```

## Documentation

See `docs/superpowers/specs/2026-05-14-expdeploy-design.md` for the v0.1 design spec.

## License

MIT — see [LICENSE](LICENSE).
```

- [ ] **Step 2: Write `LICENSE`**

```
MIT License

Copyright (c) 2026 Logan Bennett

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
```

- [ ] **Step 3: Write `.gitignore`**

```
# Python
__pycache__/
*.py[cod]
*$py.class
*.egg-info/
.eggs/
build/
dist/
.venv/
.python-version

# uv
.uv/

# pytest / coverage
.pytest_cache/
.coverage
htmlcov/
.tox/

# mypy / ruff
.mypy_cache/
.ruff_cache/

# Playwright
test-results/
playwright-report/
playwright/.cache/

# data dirs from local runs
data/
state/

# editor / OS
.DS_Store
.idea/
.vscode/

# expdeploy-specific
sessions_*/
```

---

### Task 3: Initialize git and make initial commit

**Files:** none new; this task only creates git state.

- [ ] **Step 1: Initialize git and configure default branch**

```bash
cd /Users/lobennett/grants/r01_rdoc/projects/expdeploy
git init -b main
```

Expected: `Initialized empty Git repository in /Users/lobennett/grants/r01_rdoc/projects/expdeploy/.git/`

- [ ] **Step 2: Stage scaffold files and commit**

```bash
cd /Users/lobennett/grants/r01_rdoc/projects/expdeploy
git add README.md LICENSE .gitignore docs/
git commit -m "Initial commit: README, LICENSE, .gitignore, design spec, bootstrap plan"
```

Expected: a single commit, four-ish files added (README, LICENSE, .gitignore, spec, plan).

---

## Phase B — Python tooling setup

### Task 4: pyproject.toml + uv environment

**Files:**
- Create: `/Users/lobennett/grants/r01_rdoc/projects/expdeploy/pyproject.toml`
- Create: `/Users/lobennett/grants/r01_rdoc/projects/expdeploy/src/expdeploy/__init__.py`

- [ ] **Step 1: Write `pyproject.toml`**

```toml
[project]
name = "expdeploy"
version = "0.1.0a0"
description = "Modern Python deploy tool for jsPsych v8 experiments"
readme = "README.md"
requires-python = ">=3.11"
license = { text = "MIT" }
authors = [{ name = "Logan Bennett", email = "logben@stanford.edu" }]
keywords = ["jspsych", "psychology", "cognitive-science", "experiment", "fmri", "bids"]
classifiers = [
  "Development Status :: 3 - Alpha",
  "Intended Audience :: Science/Research",
  "License :: OSI Approved :: MIT License",
  "Programming Language :: Python :: 3.11",
  "Programming Language :: Python :: 3.12",
  "Topic :: Scientific/Engineering",
]
dependencies = [
  "fastapi>=0.110",
  "uvicorn[standard]>=0.27",
  "pydantic>=2.6",
  "typer>=0.12",
  "jinja2>=3.1",
  "filelock>=3.13",
  "tomli>=2.0 ; python_version < '3.11'",
  "rich>=13.7",
]

[project.optional-dependencies]
dev = [
  "pytest>=8.0",
  "pytest-cov>=4.1",
  "pytest-asyncio>=0.23",
  "httpx>=0.27",
  "hypothesis>=6.98",
  "playwright>=1.42",
  "ruff>=0.3",
  "mypy>=1.9",
  "pre-commit>=3.6",
]

[project.scripts]
expdeploy = "expdeploy.cli:app"

[build-system]
requires = ["hatchling>=1.21"]
build-backend = "hatchling.build"

[tool.hatch.build.targets.wheel]
packages = ["src/expdeploy"]

[tool.hatch.build.targets.wheel.force-include]
"src/expdeploy/jspsych_assets" = "expdeploy/jspsych_assets"
"src/expdeploy/templates" = "expdeploy/templates"

[tool.ruff]
target-version = "py311"
line-length = 100
src = ["src", "tests"]

[tool.ruff.lint]
select = [
  "E", "F", "W",      # pycodestyle + pyflakes
  "I",                # isort
  "B",                # bugbear
  "UP",               # pyupgrade
  "SIM",              # simplify
  "RUF",              # ruff-specific
]
ignore = ["E501"]    # line length handled by formatter

[tool.ruff.format]
quote-style = "double"

[tool.mypy]
strict = true
python_version = "3.11"
files = ["src/expdeploy"]

[[tool.mypy.overrides]]
module = "tomli.*"
ignore_missing_imports = true

[tool.pytest.ini_options]
addopts = "-ra --strict-markers --strict-config"
testpaths = ["tests"]
markers = [
  "slow: marks tests as slow (deselect with '-m \"not slow\"')",
  "e2e: end-to-end Playwright tests",
  "supabase: requires SUPABASE_URL env var",
]
asyncio_mode = "auto"
```

- [ ] **Step 2: Create an empty package `__init__.py`**

```python
"""expdeploy — modern Python deploy tool for jsPsych v8 experiments."""

__version__ = "0.1.0a0"
```

Write this content to `src/expdeploy/__init__.py`.

- [ ] **Step 3: Create the venv and install dev dependencies**

```bash
cd /Users/lobennett/grants/r01_rdoc/projects/expdeploy
uv venv --python 3.12
uv sync --extra dev
```

Expected: a `.venv/` directory is created and a `uv.lock` file is written. `uv sync` exits 0.

- [ ] **Step 4: Verify the package is importable from the venv**

```bash
cd /Users/lobennett/grants/r01_rdoc/projects/expdeploy
uv run python -c "import expdeploy; print(expdeploy.__version__)"
```

Expected output: `0.1.0a0`

- [ ] **Step 5: Commit**

```bash
cd /Users/lobennett/grants/r01_rdoc/projects/expdeploy
git add pyproject.toml uv.lock src/expdeploy/__init__.py
git commit -m "Add pyproject.toml and package skeleton"
```

---

### Task 5: Ruff + mypy + pre-commit

**Files:**
- Create: `/Users/lobennett/grants/r01_rdoc/projects/expdeploy/.pre-commit-config.yaml`

- [ ] **Step 1: Write `.pre-commit-config.yaml`**

```yaml
repos:
  - repo: https://github.com/astral-sh/ruff-pre-commit
    rev: v0.3.4
    hooks:
      - id: ruff
        args: [--fix]
      - id: ruff-format

  - repo: https://github.com/pre-commit/mirrors-mypy
    rev: v1.9.0
    hooks:
      - id: mypy
        files: ^src/
        additional_dependencies:
          - fastapi>=0.110
          - pydantic>=2.6
          - typer>=0.12
          - jinja2>=3.1
          - filelock>=3.13
          - types-toml
```

- [ ] **Step 2: Install pre-commit hooks**

```bash
cd /Users/lobennett/grants/r01_rdoc/projects/expdeploy
uv run pre-commit install
```

Expected: `pre-commit installed at .git/hooks/pre-commit`.

- [ ] **Step 3: Run ruff + mypy against the skeleton**

```bash
cd /Users/lobennett/grants/r01_rdoc/projects/expdeploy
uv run ruff check .
uv run ruff format --check .
uv run mypy src/expdeploy
```

Expected: all three commands exit 0 (no issues on the empty skeleton).

- [ ] **Step 4: Commit**

```bash
cd /Users/lobennett/grants/r01_rdoc/projects/expdeploy
git add .pre-commit-config.yaml
git commit -m "Add ruff, mypy, and pre-commit config"
```

---

### Task 6: pytest baseline + sanity test

**Files:**
- Create: `/Users/lobennett/grants/r01_rdoc/projects/expdeploy/tests/__init__.py` (empty)
- Create: `/Users/lobennett/grants/r01_rdoc/projects/expdeploy/tests/unit/__init__.py` (empty)
- Create: `/Users/lobennett/grants/r01_rdoc/projects/expdeploy/tests/unit/test_sanity.py`
- Create: `/Users/lobennett/grants/r01_rdoc/projects/expdeploy/tests/conftest.py`

- [ ] **Step 1: Write `tests/conftest.py`**

```python
"""Shared pytest fixtures and configuration."""
```

(Intentionally minimal; fixtures are added per-task.)

- [ ] **Step 2: Write a failing sanity test in `tests/unit/test_sanity.py`**

```python
from expdeploy import __version__


def test_version_is_alpha():
    assert __version__ == "0.1.0a0"


def test_version_is_str():
    assert isinstance(__version__, str)
```

- [ ] **Step 3: Run the test to verify it passes**

```bash
cd /Users/lobennett/grants/r01_rdoc/projects/expdeploy
uv run pytest tests/unit/test_sanity.py -v
```

Expected: `2 passed`.

- [ ] **Step 4: Commit**

```bash
cd /Users/lobennett/grants/r01_rdoc/projects/expdeploy
git add tests/
git commit -m "Add pytest baseline with version sanity test"
```

---

## Phase C — jsPsych asset vendoring

### Task 7: Write the asset-fetching script

**Files:**
- Create: `/Users/lobennett/grants/r01_rdoc/projects/expdeploy/scripts/fetch_jspsych_assets.py`

This script downloads jsPsych v8.2.3 and a fixed list of plugins from the unpkg CDN, extracts the ESM bundle from each, and writes them to `src/expdeploy/jspsych_assets/8.2.3/` in a layout the import-map builder can consume. We vendor a curated set of plugins (not all of them) — the hello-world needs only `html-keyboard-response`, but the v0.1 plan vendors a broader set so common timelines work out of the box.

- [ ] **Step 1: Write `scripts/fetch_jspsych_assets.py`**

```python
"""Fetch jsPsych v8 + plugin ESM bundles from unpkg into src/expdeploy/jspsych_assets/.

Run: uv run python scripts/fetch_jspsych_assets.py
"""

from __future__ import annotations

import hashlib
import json
import shutil
import sys
import urllib.request
from pathlib import Path

JSPSYCH_VERSION = "8.2.3"
PLUGIN_VERSION = "2.1.0"  # matches jsPsych 8.x

PLUGINS = [
    "html-keyboard-response",
    "html-button-response",
    "image-keyboard-response",
    "image-button-response",
    "fullscreen",
    "instructions",
    "preload",
    "call-function",
    "survey-text",
]

ROOT = Path(__file__).resolve().parent.parent
ASSETS_ROOT = ROOT / "src" / "expdeploy" / "jspsych_assets" / JSPSYCH_VERSION


def fetch(url: str, dest: Path) -> None:
    dest.parent.mkdir(parents=True, exist_ok=True)
    print(f"  GET  {url}")
    with urllib.request.urlopen(url, timeout=30) as resp:
        dest.write_bytes(resp.read())


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> int:
    if ASSETS_ROOT.exists():
        print(f"Cleaning existing {ASSETS_ROOT}")
        shutil.rmtree(ASSETS_ROOT)
    ASSETS_ROOT.mkdir(parents=True)

    manifest: dict[str, dict[str, str]] = {}

    # Core jsPsych: ESM build + CSS
    fetch(
        f"https://unpkg.com/jspsych@{JSPSYCH_VERSION}/dist/index.js",
        ASSETS_ROOT / "jspsych.js",
    )
    fetch(
        f"https://unpkg.com/jspsych@{JSPSYCH_VERSION}/css/jspsych.css",
        ASSETS_ROOT / "jspsych.css",
    )
    manifest["jspsych"] = {
        "version": JSPSYCH_VERSION,
        "esm": "jspsych.js",
        "css": "jspsych.css",
        "sha256_esm": sha256(ASSETS_ROOT / "jspsych.js"),
    }

    # Plugins
    plugins_dir = ASSETS_ROOT / "plugins"
    plugins_dir.mkdir()
    for plugin in PLUGINS:
        url = f"https://unpkg.com/@jspsych/plugin-{plugin}@{PLUGIN_VERSION}/dist/index.js"
        dest = plugins_dir / f"{plugin}.js"
        fetch(url, dest)
        manifest[f"@jspsych/plugin-{plugin}"] = {
            "version": PLUGIN_VERSION,
            "esm": f"plugins/{plugin}.js",
            "sha256_esm": sha256(dest),
        }

    # Write a manifest so loader.py can introspect what's vendored
    (ASSETS_ROOT / "manifest.json").write_text(
        json.dumps(manifest, indent=2, sort_keys=True) + "\n"
    )

    # Make `from expdeploy import jspsych_assets` work
    package_init = ASSETS_ROOT.parent / "__init__.py"
    if not package_init.exists():
        package_init.write_text(
            '"""Vendored jsPsych ESM assets. Populated by scripts/fetch_jspsych_assets.py."""\n'
        )

    print(f"\nWrote {len(manifest)} entries to {ASSETS_ROOT / 'manifest.json'}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
```

- [ ] **Step 2: Commit the script (before running it)**

```bash
cd /Users/lobennett/grants/r01_rdoc/projects/expdeploy
git add scripts/fetch_jspsych_assets.py
git commit -m "Add scripts/fetch_jspsych_assets.py"
```

---

### Task 8: Run the script and vendor the assets

**Files:**
- Create: `/Users/lobennett/grants/r01_rdoc/projects/expdeploy/src/expdeploy/jspsych_assets/8.2.3/jspsych.js` (downloaded)
- Create: `/Users/lobennett/grants/r01_rdoc/projects/expdeploy/src/expdeploy/jspsych_assets/8.2.3/jspsych.css` (downloaded)
- Create: `/Users/lobennett/grants/r01_rdoc/projects/expdeploy/src/expdeploy/jspsych_assets/8.2.3/plugins/*.js` (downloaded)
- Create: `/Users/lobennett/grants/r01_rdoc/projects/expdeploy/src/expdeploy/jspsych_assets/8.2.3/manifest.json` (generated)

- [ ] **Step 1: Run the script**

```bash
cd /Users/lobennett/grants/r01_rdoc/projects/expdeploy
uv run python scripts/fetch_jspsych_assets.py
```

Expected output: lines like `GET  https://unpkg.com/jspsych@8.2.3/dist/index.js` for each asset, then `Wrote N entries to .../manifest.json`. No tracebacks.

- [ ] **Step 2: Verify the layout**

```bash
ls /Users/lobennett/grants/r01_rdoc/projects/expdeploy/src/expdeploy/jspsych_assets/8.2.3/
ls /Users/lobennett/grants/r01_rdoc/projects/expdeploy/src/expdeploy/jspsych_assets/8.2.3/plugins/
```

Expected: `jspsych.js`, `jspsych.css`, `manifest.json`, `plugins/` (latter with 9 `.js` files corresponding to the `PLUGINS` list in the script).

- [ ] **Step 3: Spot-check the ESM**

```bash
head -3 /Users/lobennett/grants/r01_rdoc/projects/expdeploy/src/expdeploy/jspsych_assets/8.2.3/jspsych.js
```

Expected: looks like a minified JS module — opening lines may be `var n={...` or similar. The file is non-empty (>10 KB).

- [ ] **Step 4: Commit the vendored assets**

```bash
cd /Users/lobennett/grants/r01_rdoc/projects/expdeploy
git add src/expdeploy/jspsych_assets/
git commit -m "Vendor jsPsych v8.2.3 + 9 plugins (ESM, fetched via scripts/fetch_jspsych_assets.py)"
```

---

## Phase D — Pydantic manifest models

### Task 9: ExperimentManifest model — happy path

**Files:**
- Create: `/Users/lobennett/grants/r01_rdoc/projects/expdeploy/src/expdeploy/manifest.py`
- Create: `/Users/lobennett/grants/r01_rdoc/projects/expdeploy/tests/unit/test_manifest.py`

- [ ] **Step 1: Write the failing happy-path test**

Write to `tests/unit/test_manifest.py`:

```python
"""Tests for expdeploy.manifest — Pydantic models for manifest.toml."""

from __future__ import annotations

import tomllib

import pytest

from expdeploy.manifest import ExperimentManifest


HELLO_TOML = """
[experiment]
exp_id = "hello"
name = "Hello world"
version = "1.0.0"
entry = "index.js"
estimated_minutes = 1

[jspsych]
version = "8.2.3"
plugins = ["@jspsych/plugin-html-keyboard-response@2.1.0"]
init = { fullscreen = false }
"""


def test_minimal_manifest_parses():
    data = tomllib.loads(HELLO_TOML)
    manifest = ExperimentManifest.model_validate(data)
    assert manifest.experiment.exp_id == "hello"
    assert manifest.experiment.name == "Hello world"
    assert manifest.experiment.entry == "index.js"
    assert manifest.jspsych.version == "8.2.3"
    assert manifest.jspsych.plugins == ["@jspsych/plugin-html-keyboard-response@2.1.0"]
    assert manifest.bids is None
    assert manifest.import_map_extras == {}
```

- [ ] **Step 2: Run the test and watch it fail**

```bash
cd /Users/lobennett/grants/r01_rdoc/projects/expdeploy
uv run pytest tests/unit/test_manifest.py::test_minimal_manifest_parses -v
```

Expected: `ModuleNotFoundError: No module named 'expdeploy.manifest'`.

- [ ] **Step 3: Implement `src/expdeploy/manifest.py`**

Note on TOML nesting: the spec writes `[experiment.metadata]`, which in TOML means `metadata` is nested *inside* `experiment`. So in the Pydantic model, `metadata` is a field on `ExperimentInfo`, not on `ExperimentManifest`.

```python
"""Pydantic models for manifest.toml and battery.toml."""

from __future__ import annotations

import tomllib
from pathlib import Path
from typing import Annotated

from pydantic import BaseModel, ConfigDict, Field, field_validator


class ExperimentMetadata(BaseModel):
    model_config = ConfigDict(extra="allow")  # researchers add arbitrary keys

    cognitive_atlas_task_id: str | None = None
    contributors: list[str] = Field(default_factory=list)
    notes: str | None = None


class ExperimentInfo(BaseModel):
    model_config = ConfigDict(extra="forbid")

    exp_id: str = Field(pattern=r"^[a-zA-Z0-9_-]+$", max_length=128)
    name: str
    version: str = "0.1.0"
    entry: str = "index.js"
    style: str | None = None
    estimated_minutes: int | None = Field(default=None, ge=0)
    metadata: ExperimentMetadata = Field(default_factory=ExperimentMetadata)


class JsPsychConfig(BaseModel):
    model_config = ConfigDict(extra="forbid")

    version: str
    plugins: list[str] = Field(default_factory=list)
    init: dict[str, object] = Field(default_factory=dict)


class BidsColumn(BaseModel):
    model_config = ConfigDict(extra="forbid")

    description: str
    levels: dict[str, str] = Field(default_factory=dict)


BidsType = Annotated[str, Field(pattern=r"^(fmri|behavioral)$")]
BidsTaskLabel = Annotated[str, Field(pattern=r"^[a-zA-Z0-9]+$", max_length=64)]


class BidsConfig(BaseModel):
    model_config = ConfigDict(extra="forbid")

    type: BidsType
    task: BidsTaskLabel
    columns: dict[str, BidsColumn] = Field(default_factory=dict)


class ExperimentManifest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    experiment: ExperimentInfo
    jspsych: JsPsychConfig
    bids: BidsConfig | None = None
    import_map_extras: dict[str, str] = Field(default_factory=dict)

    @field_validator("import_map_extras")
    @classmethod
    def _no_bare_keys(cls, value: dict[str, str]) -> dict[str, str]:
        for key in value:
            if not key.strip():
                msg = "import_map_extras keys must not be empty"
                raise ValueError(msg)
        return value


def load_manifest(path: Path) -> ExperimentManifest:
    """Read a manifest.toml from disk and return a validated ExperimentManifest."""
    with path.open("rb") as fp:
        data = tomllib.load(fp)
    return ExperimentManifest.model_validate(data)
```

- [ ] **Step 4: Run the test and verify it passes**

```bash
cd /Users/lobennett/grants/r01_rdoc/projects/expdeploy
uv run pytest tests/unit/test_manifest.py -v
```

Expected: `1 passed`.

- [ ] **Step 5: Commit**

```bash
cd /Users/lobennett/grants/r01_rdoc/projects/expdeploy
git add src/expdeploy/manifest.py tests/unit/test_manifest.py
git commit -m "Add ExperimentManifest Pydantic model with happy-path test"
```

---

### Task 10: Manifest BIDS validation (task label must be alphanumeric)

**Files:**
- Modify: `/Users/lobennett/grants/r01_rdoc/projects/expdeploy/tests/unit/test_manifest.py`

- [ ] **Step 1: Add the failing test**

Append to `tests/unit/test_manifest.py`:

```python
INVALID_BIDS_TASK_TOML = """
[experiment]
exp_id = "n_back_test"
name = "Bad BIDS label"
version = "1.0.0"
entry = "index.js"

[jspsych]
version = "8.2.3"
plugins = []

[bids]
type = "fmri"
task = "n_back"
"""


def test_bids_task_label_rejects_underscore():
    data = tomllib.loads(INVALID_BIDS_TASK_TOML)
    with pytest.raises(Exception) as excinfo:
        ExperimentManifest.model_validate(data)
    assert "task" in str(excinfo.value)
```

- [ ] **Step 2: Run the test and verify it passes**

The existing `BidsTaskLabel` pattern already enforces `^[a-zA-Z0-9]+$`, so this test should pass without code changes:

```bash
cd /Users/lobennett/grants/r01_rdoc/projects/expdeploy
uv run pytest tests/unit/test_manifest.py -v
```

Expected: both tests pass.

- [ ] **Step 3: Add a positive test for valid BIDS**

Append:

```python
VALID_BIDS_TOML = """
[experiment]
exp_id = "nback_v1"
name = "N-back"
version = "1.0.0"
entry = "index.js"

[jspsych]
version = "8.2.3"
plugins = []

[bids]
type = "behavioral"
task = "nback"

[bids.columns.trial_type]
description = "Whether the trial was a target or non-target."
levels = { target = "Target", nontarget = "Non-target" }
"""


def test_valid_bids_with_columns_parses():
    data = tomllib.loads(VALID_BIDS_TOML)
    manifest = ExperimentManifest.model_validate(data)
    assert manifest.bids is not None
    assert manifest.bids.type == "behavioral"
    assert manifest.bids.task == "nback"
    assert "trial_type" in manifest.bids.columns
    assert manifest.bids.columns["trial_type"].levels["target"] == "Target"
```

- [ ] **Step 4: Run and verify**

```bash
cd /Users/lobennett/grants/r01_rdoc/projects/expdeploy
uv run pytest tests/unit/test_manifest.py -v
```

Expected: `3 passed`.

- [ ] **Step 5: Commit**

```bash
cd /Users/lobennett/grants/r01_rdoc/projects/expdeploy
git add tests/unit/test_manifest.py
git commit -m "Validate BIDS task labels are alphanumeric; test column sidecar schema"
```

---

### Task 11: `load_manifest` from-disk path test

**Files:**
- Modify: `/Users/lobennett/grants/r01_rdoc/projects/expdeploy/tests/unit/test_manifest.py`

- [ ] **Step 1: Add the failing test**

Append to `tests/unit/test_manifest.py`:

```python
from expdeploy.manifest import load_manifest


def test_load_manifest_from_disk(tmp_path):
    manifest_path = tmp_path / "manifest.toml"
    manifest_path.write_text(HELLO_TOML)
    manifest = load_manifest(manifest_path)
    assert manifest.experiment.exp_id == "hello"


def test_load_manifest_missing_file_raises(tmp_path):
    with pytest.raises(FileNotFoundError):
        load_manifest(tmp_path / "nope.toml")
```

- [ ] **Step 2: Run and verify**

```bash
cd /Users/lobennett/grants/r01_rdoc/projects/expdeploy
uv run pytest tests/unit/test_manifest.py -v
```

Expected: `5 passed`. The `load_manifest` function was already implemented in Task 9.

- [ ] **Step 3: Commit**

```bash
cd /Users/lobennett/grants/r01_rdoc/projects/expdeploy
git add tests/unit/test_manifest.py
git commit -m "Test load_manifest reads from disk and raises on missing file"
```

---

## Phase E — Experiment loader

### Task 12: ExperimentLoader — locate and load a manifest from a folder

**Files:**
- Create: `/Users/lobennett/grants/r01_rdoc/projects/expdeploy/src/expdeploy/loader.py`
- Create: `/Users/lobennett/grants/r01_rdoc/projects/expdeploy/tests/unit/test_loader.py`

The loader is responsible for: pointing it at an experiment directory, finding `manifest.toml` inside it, loading + validating it, and returning a typed view that bundles the manifest with the experiment's filesystem path.

- [ ] **Step 1: Write the failing test**

Write to `tests/unit/test_loader.py`:

```python
"""Tests for expdeploy.loader.ExperimentLoader."""

from __future__ import annotations

import pytest

from expdeploy.loader import ExperimentLoader, LoadedExperiment


HELLO_TOML = """
[experiment]
exp_id = "hello"
name = "Hello world"
version = "1.0.0"
entry = "index.js"

[jspsych]
version = "8.2.3"
plugins = ["@jspsych/plugin-html-keyboard-response@2.1.0"]
"""


def _make_hello(tmp_path):
    exp_dir = tmp_path / "hello"
    exp_dir.mkdir()
    (exp_dir / "manifest.toml").write_text(HELLO_TOML)
    (exp_dir / "index.js").write_text("export default () => {};")
    return exp_dir


def test_loader_returns_loaded_experiment(tmp_path):
    exp_dir = _make_hello(tmp_path)
    loaded = ExperimentLoader().load(exp_dir)
    assert isinstance(loaded, LoadedExperiment)
    assert loaded.manifest.experiment.exp_id == "hello"
    assert loaded.path == exp_dir.resolve()
    assert loaded.entry_path == (exp_dir / "index.js").resolve()


def test_loader_rejects_missing_manifest(tmp_path):
    exp_dir = tmp_path / "no_manifest"
    exp_dir.mkdir()
    with pytest.raises(FileNotFoundError):
        ExperimentLoader().load(exp_dir)


def test_loader_rejects_missing_entry(tmp_path):
    exp_dir = tmp_path / "no_entry"
    exp_dir.mkdir()
    (exp_dir / "manifest.toml").write_text(HELLO_TOML)
    # no index.js
    with pytest.raises(FileNotFoundError):
        ExperimentLoader().load(exp_dir)
```

- [ ] **Step 2: Run the test to verify it fails**

```bash
cd /Users/lobennett/grants/r01_rdoc/projects/expdeploy
uv run pytest tests/unit/test_loader.py -v
```

Expected: `ModuleNotFoundError: No module named 'expdeploy.loader'`.

- [ ] **Step 3: Implement `src/expdeploy/loader.py`**

```python
"""Loading experiment directories from disk."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from expdeploy.manifest import ExperimentManifest, load_manifest


@dataclass(frozen=True, slots=True)
class LoadedExperiment:
    """An experiment directory after manifest validation."""

    path: Path
    manifest: ExperimentManifest

    @property
    def entry_path(self) -> Path:
        return (self.path / self.manifest.experiment.entry).resolve()

    @property
    def style_path(self) -> Path | None:
        style = self.manifest.experiment.style
        if style is None:
            return None
        return (self.path / style).resolve()


class ExperimentLoader:
    """Loads + validates an experiment directory."""

    def load(self, exp_dir: Path) -> LoadedExperiment:
        exp_dir = Path(exp_dir).resolve()
        manifest_path = exp_dir / "manifest.toml"
        if not manifest_path.is_file():
            msg = f"manifest.toml not found in {exp_dir}"
            raise FileNotFoundError(msg)
        manifest = load_manifest(manifest_path)
        entry_path = exp_dir / manifest.experiment.entry
        if not entry_path.is_file():
            msg = f"entry file not found: {entry_path}"
            raise FileNotFoundError(msg)
        return LoadedExperiment(path=exp_dir, manifest=manifest)
```

- [ ] **Step 4: Run the test and verify it passes**

```bash
cd /Users/lobennett/grants/r01_rdoc/projects/expdeploy
uv run pytest tests/unit/test_loader.py -v
```

Expected: `3 passed`.

- [ ] **Step 5: Commit**

```bash
cd /Users/lobennett/grants/r01_rdoc/projects/expdeploy
git add src/expdeploy/loader.py tests/unit/test_loader.py
git commit -m "Add ExperimentLoader with manifest + entry validation"
```

---

## Phase F — Import map builder

### Task 13: ImportMapBuilder — construct import map from a LoadedExperiment

**Files:**
- Create: `/Users/lobennett/grants/r01_rdoc/projects/expdeploy/src/expdeploy/importmap.py`
- Create: `/Users/lobennett/grants/r01_rdoc/projects/expdeploy/tests/unit/test_importmap.py`

The import map tells the browser how to resolve `import { initJsPsych } from 'jspsych'` and similar bare specifiers. The builder takes a `LoadedExperiment` plus the vendored jsPsych assets directory and produces a dict suitable for `<script type="importmap">{...}</script>`.

- [ ] **Step 1: Write the failing test**

Write to `tests/unit/test_importmap.py`:

```python
"""Tests for expdeploy.importmap.ImportMapBuilder."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from expdeploy.importmap import ImportMapBuilder
from expdeploy.loader import ExperimentLoader


HELLO_TOML = """
[experiment]
exp_id = "hello"
name = "Hello world"
version = "1.0.0"
entry = "index.js"

[jspsych]
version = "8.2.3"
plugins = ["@jspsych/plugin-html-keyboard-response@2.1.0"]

[import_map_extras]
"@lab/iti" = "./lib/iti.js"
"""


def _make_hello(tmp_path):
    exp_dir = tmp_path / "hello"
    exp_dir.mkdir()
    (exp_dir / "manifest.toml").write_text(HELLO_TOML)
    (exp_dir / "index.js").write_text("export default () => {};")
    (exp_dir / "lib").mkdir()
    (exp_dir / "lib" / "iti.js").write_text("export const sampleITI = () => 500;")
    return exp_dir


def _vendored_assets_root() -> Path:
    """Find the real vendored jsPsych assets root (committed in Task 8)."""
    from expdeploy import jspsych_assets

    return Path(jspsych_assets.__file__).resolve().parent


def test_import_map_contains_jspsych_and_plugin(tmp_path):
    loaded = ExperimentLoader().load(_make_hello(tmp_path))
    builder = ImportMapBuilder(vendored_root=_vendored_assets_root())
    import_map = builder.build(
        loaded,
        jspsych_url_prefix="/static/jspsych/8.2.3",
        experiment_url_prefix="/static/exp/hello",
    )
    imports = import_map["imports"]
    assert imports["jspsych"] == "/static/jspsych/8.2.3/jspsych.js"
    assert imports["@jspsych/plugin-html-keyboard-response"] == (
        "/static/jspsych/8.2.3/plugins/html-keyboard-response.js"
    )


def test_import_map_includes_extras(tmp_path):
    loaded = ExperimentLoader().load(_make_hello(tmp_path))
    builder = ImportMapBuilder(vendored_root=_vendored_assets_root())
    import_map = builder.build(
        loaded,
        jspsych_url_prefix="/static/jspsych/8.2.3",
        experiment_url_prefix="/static/exp/hello",
    )
    assert (
        import_map["imports"]["@lab/iti"]
        == "/static/exp/hello/lib/iti.js"
    )


def test_import_map_is_json_serializable(tmp_path):
    loaded = ExperimentLoader().load(_make_hello(tmp_path))
    builder = ImportMapBuilder(vendored_root=_vendored_assets_root())
    import_map = builder.build(
        loaded,
        jspsych_url_prefix="/static/jspsych/8.2.3",
        experiment_url_prefix="/static/exp/hello",
    )
    # Must round-trip through json.dumps without raising
    json.dumps(import_map)


def test_import_map_rejects_unvendored_jspsych_version(tmp_path):
    bad_toml = HELLO_TOML.replace('version = "8.2.3"', 'version = "9.99.99"')
    exp_dir = tmp_path / "hello"
    exp_dir.mkdir()
    (exp_dir / "manifest.toml").write_text(bad_toml)
    (exp_dir / "index.js").write_text("export default () => {};")
    loaded = ExperimentLoader().load(exp_dir)
    builder = ImportMapBuilder(vendored_root=_vendored_assets_root())
    with pytest.raises(LookupError) as excinfo:
        builder.build(
            loaded,
            jspsych_url_prefix="/static/jspsych/9.99.99",
            experiment_url_prefix="/static/exp/hello",
        )
    assert "9.99.99" in str(excinfo.value)
```

- [ ] **Step 2: Run the test to verify it fails**

```bash
cd /Users/lobennett/grants/r01_rdoc/projects/expdeploy
uv run pytest tests/unit/test_importmap.py -v
```

Expected: `ModuleNotFoundError: No module named 'expdeploy.importmap'`.

- [ ] **Step 3: Implement `src/expdeploy/importmap.py`**

```python
"""Build browser-native import maps for served experiments."""

from __future__ import annotations

import json
import re
from pathlib import Path

from expdeploy.loader import LoadedExperiment


PLUGIN_NAME_RE = re.compile(r"^(@jspsych/plugin-[a-zA-Z0-9-]+)(?:@([\d.]+))?$")


class ImportMapBuilder:
    """Constructs a browser import map for a LoadedExperiment.

    The vendored_root is `src/expdeploy/jspsych_assets/`. Inside it, each
    available jsPsych version has its own subdir (e.g., `8.2.3/`) with a
    `manifest.json` describing what's available.
    """

    def __init__(self, vendored_root: Path) -> None:
        self.vendored_root = Path(vendored_root).resolve()

    def build(
        self,
        loaded: LoadedExperiment,
        *,
        jspsych_url_prefix: str,
        experiment_url_prefix: str,
    ) -> dict[str, dict[str, str]]:
        manifest = loaded.manifest
        version = manifest.jspsych.version
        version_dir = self.vendored_root / version
        if not version_dir.is_dir():
            available = sorted(p.name for p in self.vendored_root.iterdir() if p.is_dir())
            msg = (
                f"jsPsych version {version} is not vendored. "
                f"Available versions: {available}"
            )
            raise LookupError(msg)

        vendored_manifest_path = version_dir / "manifest.json"
        if not vendored_manifest_path.is_file():
            msg = f"Vendored manifest missing at {vendored_manifest_path}"
            raise LookupError(msg)
        vendored = json.loads(vendored_manifest_path.read_text())

        imports: dict[str, str] = {}

        # Core jsPsych
        imports["jspsych"] = f"{jspsych_url_prefix}/{vendored['jspsych']['esm']}"

        # Plugins declared in the experiment manifest
        for plugin_spec in manifest.jspsych.plugins:
            match = PLUGIN_NAME_RE.match(plugin_spec)
            if match is None:
                msg = f"Unrecognized plugin spec: {plugin_spec!r}"
                raise ValueError(msg)
            name = match.group(1)
            if name not in vendored:
                available_plugins = sorted(k for k in vendored if k.startswith("@jspsych/"))
                msg = f"Plugin not vendored: {name}. Available: {available_plugins}"
                raise LookupError(msg)
            imports[name] = f"{jspsych_url_prefix}/{vendored[name]['esm']}"

        # Experiment-local imports for bare ./ paths via the import map
        # (relative imports in index.js resolve automatically; this exposes
        # any aliases declared in import_map_extras)
        for alias, relative in manifest.import_map_extras.items():
            if relative.startswith("./"):
                url = f"{experiment_url_prefix}/{relative[2:]}"
            elif relative.startswith("/"):
                url = relative
            elif relative.startswith("http"):
                url = relative
            else:
                url = f"{experiment_url_prefix}/{relative}"
            imports[alias] = url

        return {"imports": imports}
```

- [ ] **Step 4: Run the tests and verify they pass**

```bash
cd /Users/lobennett/grants/r01_rdoc/projects/expdeploy
uv run pytest tests/unit/test_importmap.py -v
```

Expected: `4 passed`.

- [ ] **Step 5: Commit**

```bash
cd /Users/lobennett/grants/r01_rdoc/projects/expdeploy
git add src/expdeploy/importmap.py tests/unit/test_importmap.py
git commit -m "Add ImportMapBuilder; vendored jsPsych + plugins + extras"
```

---

## Phase G — HTML template

### Task 14: deploy.html.j2 + render function

**Files:**
- Create: `/Users/lobennett/grants/r01_rdoc/projects/expdeploy/src/expdeploy/templates/deploy.html.j2`
- Create: `/Users/lobennett/grants/r01_rdoc/projects/expdeploy/src/expdeploy/renderer.py`
- Create: `/Users/lobennett/grants/r01_rdoc/projects/expdeploy/tests/unit/test_renderer.py`

- [ ] **Step 1: Write the failing test**

Write to `tests/unit/test_renderer.py`:

```python
"""Tests for expdeploy.renderer.render_experiment_html."""

from __future__ import annotations

import json
import re
from pathlib import Path

from expdeploy.renderer import render_experiment_html


def test_html_contains_import_map():
    html = render_experiment_html(
        exp_id="hello",
        experiment_entry_url="/static/exp/hello/index.js",
        style_url=None,
        jspsych_css_url="/static/jspsych/8.2.3/jspsych.css",
        import_map={"imports": {"jspsych": "/static/jspsych/8.2.3/jspsych.js"}},
        runtime_globals={"subjectId": "01", "sessionNum": "1", "runNum": "1"},
        post_url="/api/data",
    )
    # Find the import map script
    match = re.search(
        r'<script\s+type="importmap"[^>]*>(.*?)</script>',
        html,
        re.DOTALL,
    )
    assert match is not None
    payload = json.loads(match.group(1))
    assert payload["imports"]["jspsych"] == "/static/jspsych/8.2.3/jspsych.js"


def test_html_injects_window_expdeploy():
    html = render_experiment_html(
        exp_id="hello",
        experiment_entry_url="/static/exp/hello/index.js",
        style_url=None,
        jspsych_css_url="/static/jspsych/8.2.3/jspsych.css",
        import_map={"imports": {}},
        runtime_globals={"subjectId": "01"},
        post_url="/api/data",
    )
    assert 'window.expdeploy' in html
    assert '"subjectId":"01"' in html or '"subjectId": "01"' in html


def test_html_loads_experiment_entry_as_module():
    html = render_experiment_html(
        exp_id="hello",
        experiment_entry_url="/static/exp/hello/index.js",
        style_url=None,
        jspsych_css_url="/static/jspsych/8.2.3/jspsych.css",
        import_map={"imports": {}},
        runtime_globals={},
        post_url="/api/data",
    )
    # The experiment entry is imported as an ES module
    assert "/static/exp/hello/index.js" in html
    assert 'type="module"' in html


def test_html_optionally_includes_style():
    html_with = render_experiment_html(
        exp_id="hello",
        experiment_entry_url="/static/exp/hello/index.js",
        style_url="/static/exp/hello/style.css",
        jspsych_css_url="/static/jspsych/8.2.3/jspsych.css",
        import_map={"imports": {}},
        runtime_globals={},
        post_url="/api/data",
    )
    assert "/static/exp/hello/style.css" in html_with

    html_without = render_experiment_html(
        exp_id="hello",
        experiment_entry_url="/static/exp/hello/index.js",
        style_url=None,
        jspsych_css_url="/static/jspsych/8.2.3/jspsych.css",
        import_map={"imports": {}},
        runtime_globals={},
        post_url="/api/data",
    )
    assert "style.css" not in html_without
```

- [ ] **Step 2: Run the test to verify it fails**

```bash
cd /Users/lobennett/grants/r01_rdoc/projects/expdeploy
uv run pytest tests/unit/test_renderer.py -v
```

Expected: `ModuleNotFoundError: No module named 'expdeploy.renderer'`.

- [ ] **Step 3: Write the Jinja template `src/expdeploy/templates/deploy.html.j2`**

We use Jinja's `tojson` filter (not raw `| safe`) for everything emitted inside `<script>` tags. `tojson` escapes `<`, `>`, `&`, `'` to `\u00xx` so an attacker can't terminate the script tag via a malicious string in (e.g.) a session label.

```html
<!DOCTYPE html>
<html lang="en">
  <head>
    <meta charset="utf-8" />
    <title>expdeploy — {{ exp_id }}</title>
    <link rel="stylesheet" href="{{ jspsych_css_url }}" />
    {% if style_url %}
    <link rel="stylesheet" href="{{ style_url }}" />
    {% endif %}

    <script type="importmap">
{{ import_map | tojson }}
    </script>

    <script>
      window.expdeploy = Object.assign(
        {{ runtime_globals | tojson }},
        {
          submit(payload) {
            return fetch({{ post_url | tojson }}, {
              method: "POST",
              headers: { "Content-Type": "application/json" },
              body: JSON.stringify(payload),
            }).then((r) => {
              if (!r.ok) throw new Error("POST /api/data failed: " + r.status);
              return r.json();
            });
          },
        }
      );
    </script>
  </head>
  <body>
    <div id="jspsych-target"></div>
    <script type="module">
      import build from {{ experiment_entry_url | tojson }};
      if (typeof build === "function") {
        build();
      } else if (build && typeof build.default === "function") {
        build.default();
      } else {
        console.error("Experiment entry did not export a default function:", build);
      }
    </script>
  </body>
</html>
```

- [ ] **Step 4: Write `src/expdeploy/renderer.py`**

```python
"""Render the HTML page that serves an experiment to the browser."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from jinja2 import Environment, FileSystemLoader, select_autoescape


TEMPLATES_DIR = Path(__file__).resolve().parent / "templates"

_env = Environment(
    loader=FileSystemLoader(TEMPLATES_DIR),
    autoescape=select_autoescape(["html"]),
)


def render_experiment_html(
    *,
    exp_id: str,
    experiment_entry_url: str,
    style_url: str | None,
    jspsych_css_url: str,
    import_map: dict[str, Any],
    runtime_globals: dict[str, Any],
    post_url: str,
) -> str:
    template = _env.get_template("deploy.html.j2")
    return template.render(
        exp_id=exp_id,
        experiment_entry_url=experiment_entry_url,
        style_url=style_url,
        jspsych_css_url=jspsych_css_url,
        import_map=import_map,
        runtime_globals=runtime_globals,
        post_url=post_url,
    )
```

- [ ] **Step 5: Run the tests and verify they pass**

```bash
cd /Users/lobennett/grants/r01_rdoc/projects/expdeploy
uv run pytest tests/unit/test_renderer.py -v
```

Expected: `4 passed`.

- [ ] **Step 6: Commit**

```bash
cd /Users/lobennett/grants/r01_rdoc/projects/expdeploy
git add src/expdeploy/templates/deploy.html.j2 src/expdeploy/renderer.py tests/unit/test_renderer.py
git commit -m "Add Jinja deploy template + render_experiment_html()"
```

---

## Phase H — Minimal FS storage

### Task 15: FSAdapter — raw JSON to disk

**Files:**
- Create: `/Users/lobennett/grants/r01_rdoc/projects/expdeploy/src/expdeploy/storage/__init__.py` (empty)
- Create: `/Users/lobennett/grants/r01_rdoc/projects/expdeploy/src/expdeploy/storage/base.py`
- Create: `/Users/lobennett/grants/r01_rdoc/projects/expdeploy/src/expdeploy/storage/fs.py`
- Create: `/Users/lobennett/grants/r01_rdoc/projects/expdeploy/tests/unit/test_fs.py`

This is **intentionally minimal** for Plan 1. We only need to save the raw POSTed JSON to disk so the e2e test can verify a round-trip. The `RunRecord`, BIDS layout, dataset_description.json, participants.tsv, and SQLiteCatalog all land in Plan 2.

- [ ] **Step 1: Write the failing test**

Write to `tests/unit/test_fs.py`:

```python
"""Tests for expdeploy.storage.fs.FSAdapter (minimal Plan-1 surface)."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from expdeploy.storage.base import RunRecord
from expdeploy.storage.fs import FSAdapter


def _record(exp_id: str = "hello", subject_id: str = "01") -> RunRecord:
    return RunRecord(
        exp_id=exp_id,
        subject_id=subject_id,
        session_num=None,
        run_num=None,
        raw_payload={"trials": [{"trial_type": "html-keyboard-response", "rt": 250}]},
    )


def test_save_writes_raw_json(tmp_path):
    adapter = FSAdapter(data_dir=tmp_path)
    result = adapter.save(_record())
    assert result.ok is True
    saved = Path(result.path)
    assert saved.exists()
    assert saved.is_file()
    payload = json.loads(saved.read_text())
    assert payload["trials"][0]["rt"] == 250


def test_save_uses_bids_style_filename(tmp_path):
    adapter = FSAdapter(data_dir=tmp_path)
    result = adapter.save(_record(exp_id="hello", subject_id="01"))
    saved = Path(result.path)
    assert saved.name.startswith("sub-01_")
    assert "_task-hello_" in saved.name
    assert saved.name.endswith("_beh.json")


def test_save_with_session_and_run(tmp_path):
    adapter = FSAdapter(data_dir=tmp_path)
    record = RunRecord(
        exp_id="hello",
        subject_id="01",
        session_num="1",
        run_num="2",
        raw_payload={"trials": []},
    )
    result = adapter.save(record)
    saved = Path(result.path)
    assert "sub-01" in saved.name
    assert "ses-1" in saved.name
    assert "run-2" in saved.name


def test_save_writes_under_subject_directory(tmp_path):
    adapter = FSAdapter(data_dir=tmp_path)
    result = adapter.save(_record(subject_id="01"))
    assert Path(result.path).parent.name == "sub-01"


def test_save_rejects_invalid_subject_id(tmp_path):
    adapter = FSAdapter(data_dir=tmp_path)
    with pytest.raises(ValueError):
        # subject_id with disallowed characters
        FSAdapter._make_filename(  # type: ignore[attr-defined]
            exp_id="hello",
            subject_id="sub/../escape",
            session_num=None,
            run_num=None,
        )
```

- [ ] **Step 2: Run the test to verify it fails**

```bash
cd /Users/lobennett/grants/r01_rdoc/projects/expdeploy
uv run pytest tests/unit/test_fs.py -v
```

Expected: `ModuleNotFoundError: No module named 'expdeploy.storage.base'`.

- [ ] **Step 3: Implement `src/expdeploy/storage/base.py`**

```python
"""Storage adapter protocol and common types."""

from __future__ import annotations

import re
from dataclasses import dataclass
from typing import Any, Protocol, runtime_checkable

from pydantic import BaseModel, ConfigDict, Field


_LABEL_RE = re.compile(r"^[a-zA-Z0-9-]+$")


def _validate_label(value: str, *, field: str) -> str:
    if not _LABEL_RE.match(value):
        msg = f"{field} {value!r} must match {_LABEL_RE.pattern}"
        raise ValueError(msg)
    return value


class RunRecord(BaseModel):
    """One completed experiment run; what an adapter saves."""

    model_config = ConfigDict(extra="forbid")

    exp_id: str = Field(pattern=r"^[a-zA-Z0-9_-]+$", max_length=128)
    subject_id: str = Field(pattern=r"^[a-zA-Z0-9-]+$", max_length=64)
    session_num: str | None = Field(default=None, pattern=r"^[a-zA-Z0-9-]+$", max_length=32)
    run_num: str | None = Field(default=None, pattern=r"^[a-zA-Z0-9-]+$", max_length=32)
    raw_payload: dict[str, Any] = Field(default_factory=dict)


@dataclass(frozen=True, slots=True)
class SaveResult:
    ok: bool
    path: str
    error: str | None = None


@runtime_checkable
class StorageAdapter(Protocol):
    name: str

    def save(self, record: RunRecord) -> SaveResult: ...
```

- [ ] **Step 4: Implement `src/expdeploy/storage/fs.py`**

```python
"""Filesystem storage adapter (raw JSON only in Plan 1)."""

from __future__ import annotations

import json
import re
from datetime import datetime, timezone
from pathlib import Path

from expdeploy.storage.base import RunRecord, SaveResult


_LABEL_RE = re.compile(r"^[a-zA-Z0-9-]+$")


class FSAdapter:
    """Saves raw run JSON to a BIDS-shaped filename under data_dir/raw/."""

    name = "fs"

    def __init__(self, data_dir: Path) -> None:
        self.data_dir = Path(data_dir).resolve()

    @staticmethod
    def _validate(field: str, value: str | None) -> None:
        if value is not None and not _LABEL_RE.match(value):
            msg = f"{field} {value!r} must match {_LABEL_RE.pattern}"
            raise ValueError(msg)

    @classmethod
    def _make_filename(
        cls,
        *,
        exp_id: str,
        subject_id: str,
        session_num: str | None,
        run_num: str | None,
    ) -> str:
        cls._validate("exp_id", exp_id)
        cls._validate("subject_id", subject_id)
        cls._validate("session_num", session_num)
        cls._validate("run_num", run_num)
        parts = [f"sub-{subject_id}"]
        if session_num is not None:
            parts.append(f"ses-{session_num}")
        parts.append(f"task-{exp_id}")
        if run_num is not None:
            parts.append(f"run-{run_num}")
        return "_".join(parts) + "_beh.json"

    def save(self, record: RunRecord) -> SaveResult:
        try:
            filename = self._make_filename(
                exp_id=record.exp_id,
                subject_id=record.subject_id,
                session_num=record.session_num,
                run_num=record.run_num,
            )
            subject_dir = self.data_dir / "raw" / f"sub-{record.subject_id}"
            if record.session_num is not None:
                subject_dir = subject_dir / f"ses-{record.session_num}"
            subject_dir.mkdir(parents=True, exist_ok=True)
            path = subject_dir / filename
            payload = {
                "saved_at_utc": datetime.now(timezone.utc).isoformat(),
                **record.raw_payload,
            }
            # Atomic write
            tmp = path.with_suffix(path.suffix + ".tmp")
            tmp.write_text(json.dumps(payload, indent=2, sort_keys=True))
            tmp.replace(path)
        except Exception as exc:  # noqa: BLE001
            return SaveResult(ok=False, path="", error=str(exc))
        return SaveResult(ok=True, path=str(path))
```

- [ ] **Step 5: Note about `_validate` — fix the static-method test**

The test `test_save_rejects_invalid_subject_id` calls `FSAdapter._make_filename` directly. Re-run tests now:

```bash
cd /Users/lobennett/grants/r01_rdoc/projects/expdeploy
uv run pytest tests/unit/test_fs.py -v
```

Expected: `5 passed`. If the static-method test still fails because slashes aren't matched by `^[a-zA-Z0-9-]+$`, the regex (which excludes `/`) does raise — pass.

- [ ] **Step 6: Commit**

```bash
cd /Users/lobennett/grants/r01_rdoc/projects/expdeploy
git add src/expdeploy/storage/ tests/unit/test_fs.py
git commit -m "Add StorageAdapter Protocol + FSAdapter (raw JSON only)"
```

---

## Phase I — FastAPI app

### Task 16: `create_app` + GET / serves an experiment

**Files:**
- Create: `/Users/lobennett/grants/r01_rdoc/projects/expdeploy/src/expdeploy/app.py`
- Create: `/Users/lobennett/grants/r01_rdoc/projects/expdeploy/tests/integration/__init__.py` (empty)
- Create: `/Users/lobennett/grants/r01_rdoc/projects/expdeploy/tests/integration/test_app.py`

The app factory takes config (loaded experiment, vendored assets root, storage adapter) and returns a FastAPI instance. Configuration is explicit (no global state).

- [ ] **Step 1: Write the failing integration test**

Write to `tests/integration/test_app.py`:

```python
"""Integration tests for the FastAPI app — TestClient against tmp_path fixtures."""

from __future__ import annotations

import json
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

from expdeploy import jspsych_assets
from expdeploy.app import AppConfig, create_app
from expdeploy.loader import ExperimentLoader
from expdeploy.storage.fs import FSAdapter


HELLO_TOML = """
[experiment]
exp_id = "hello"
name = "Hello world"
version = "1.0.0"
entry = "index.js"

[jspsych]
version = "8.2.3"
plugins = ["@jspsych/plugin-html-keyboard-response@2.1.0"]
"""


HELLO_JS = """
import { initJsPsych } from 'jspsych';
import htmlKeyboardResponse from '@jspsych/plugin-html-keyboard-response';

export default function build() {
  const jsPsych = initJsPsych({
    on_finish: () => window.expdeploy.submit({
      exp_id: window.expdeploy.expId,
      subject_id: window.expdeploy.subjectId,
      trials: jsPsych.data.get().values(),
      status: 'finished',
    }),
  });
  jsPsych.run([{
    type: htmlKeyboardResponse,
    stimulus: '<p>Press any key.</p>',
  }]);
}
"""


def _vendored_root() -> Path:
    return Path(jspsych_assets.__file__).resolve().parent


@pytest.fixture
def hello_experiment(tmp_path):
    exp_dir = tmp_path / "hello"
    exp_dir.mkdir()
    (exp_dir / "manifest.toml").write_text(HELLO_TOML)
    (exp_dir / "index.js").write_text(HELLO_JS)
    return exp_dir


@pytest.fixture
def app_client(hello_experiment, tmp_path):
    data_dir = tmp_path / "data"
    config = AppConfig(
        experiment=ExperimentLoader().load(hello_experiment),
        vendored_root=_vendored_root(),
        storage=FSAdapter(data_dir=data_dir),
        subject_id="01",
        session_num=None,
        run_num=None,
    )
    app = create_app(config)
    return TestClient(app), data_dir


def test_root_returns_html(app_client):
    client, _ = app_client
    response = client.get("/")
    assert response.status_code == 200
    assert response.headers["content-type"].startswith("text/html")
    body = response.text
    assert "<!DOCTYPE html>" in body
    assert 'type="importmap"' in body
    assert 'window.expdeploy' in body
    assert '"subjectId":"01"' in body or '"subjectId": "01"' in body


def test_healthz_returns_ok(app_client):
    client, _ = app_client
    response = client.get("/healthz")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_static_jspsych_asset_served(app_client):
    client, _ = app_client
    response = client.get("/static/jspsych/8.2.3/jspsych.js")
    assert response.status_code == 200
    assert "javascript" in response.headers["content-type"]


def test_static_experiment_index_js_served(app_client):
    client, _ = app_client
    response = client.get("/static/exp/hello/index.js")
    assert response.status_code == 200
    body = response.text
    assert "initJsPsych" in body


def test_post_data_writes_file(app_client):
    client, data_dir = app_client
    payload = {
        "exp_id": "hello",
        "subject_id": "01",
        "trials": [{"trial_type": "html-keyboard-response", "rt": 432}],
        "status": "finished",
    }
    response = client.post("/api/data", json=payload)
    assert response.status_code == 200
    body = response.json()
    assert body["ok"] is True
    saved_path = Path(body["path"])
    assert saved_path.exists()
    saved = json.loads(saved_path.read_text())
    assert saved["trials"][0]["rt"] == 432


def test_post_data_rejects_invalid_subject(app_client):
    client, _ = app_client
    payload = {
        "exp_id": "hello",
        "subject_id": "../oops",
        "trials": [],
        "status": "finished",
    }
    response = client.post("/api/data", json=payload)
    assert response.status_code == 422
```

- [ ] **Step 2: Run the test to verify it fails**

```bash
cd /Users/lobennett/grants/r01_rdoc/projects/expdeploy
uv run pytest tests/integration/test_app.py -v
```

Expected: `ModuleNotFoundError: No module named 'expdeploy.app'`.

- [ ] **Step 3: Implement `src/expdeploy/app.py`**

```python
"""FastAPI app factory and route handlers."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any

from fastapi import FastAPI, HTTPException
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles

from expdeploy import __version__
from expdeploy.importmap import ImportMapBuilder
from expdeploy.loader import LoadedExperiment
from expdeploy.renderer import render_experiment_html
from expdeploy.storage.base import RunRecord, StorageAdapter


@dataclass(frozen=True, slots=True)
class AppConfig:
    experiment: LoadedExperiment
    vendored_root: Path
    storage: StorageAdapter
    subject_id: str
    session_num: str | None
    run_num: str | None


def create_app(config: AppConfig) -> FastAPI:
    app = FastAPI(title="expdeploy", version=__version__)

    exp = config.experiment
    exp_id = exp.manifest.experiment.exp_id
    jspsych_version = exp.manifest.jspsych.version
    jspsych_dir = config.vendored_root / jspsych_version
    if not jspsych_dir.is_dir():
        msg = f"jsPsych version {jspsych_version} not vendored"
        raise LookupError(msg)

    app.mount(
        f"/static/jspsych/{jspsych_version}",
        StaticFiles(directory=str(jspsych_dir)),
        name="static-jspsych",
    )
    app.mount(
        f"/static/exp/{exp_id}",
        StaticFiles(directory=str(exp.path)),
        name="static-experiment",
    )

    builder = ImportMapBuilder(vendored_root=config.vendored_root)

    @app.get("/", response_class=HTMLResponse)
    def serve_root() -> HTMLResponse:
        import_map = builder.build(
            exp,
            jspsych_url_prefix=f"/static/jspsych/{jspsych_version}",
            experiment_url_prefix=f"/static/exp/{exp_id}",
        )
        style_url = (
            f"/static/exp/{exp_id}/{exp.manifest.experiment.style}"
            if exp.manifest.experiment.style
            else None
        )
        html = render_experiment_html(
            exp_id=exp_id,
            experiment_entry_url=f"/static/exp/{exp_id}/{exp.manifest.experiment.entry}",
            style_url=style_url,
            jspsych_css_url=f"/static/jspsych/{jspsych_version}/jspsych.css",
            import_map=import_map,
            runtime_globals={
                "expId": exp_id,
                "subjectId": config.subject_id,
                "sessionNum": config.session_num,
                "runNum": config.run_num,
                "deployVersion": __version__,
            },
            post_url="/api/data",
        )
        return HTMLResponse(content=html)

    @app.get("/healthz")
    def healthz() -> dict[str, str]:
        return {"status": "ok"}

    @app.get("/readyz")
    def readyz() -> dict[str, str]:
        return {"status": "ready"}

    @app.post("/api/data")
    def post_data(payload: dict[str, Any]) -> JSONResponse:
        try:
            record = RunRecord(
                exp_id=payload.get("exp_id", exp_id),
                subject_id=payload.get("subject_id") or config.subject_id,
                session_num=payload.get("session_num") or config.session_num,
                run_num=payload.get("run_num") or config.run_num,
                raw_payload=payload,
            )
        except Exception as exc:  # Pydantic ValidationError surfaces here
            raise HTTPException(status_code=422, detail=str(exc)) from exc
        result = config.storage.save(record)
        if not result.ok:
            raise HTTPException(status_code=500, detail=result.error or "save failed")
        return JSONResponse({"ok": True, "path": result.path})

    return app
```

- [ ] **Step 4: Run the integration tests**

```bash
cd /Users/lobennett/grants/r01_rdoc/projects/expdeploy
uv run pytest tests/integration/test_app.py -v
```

Expected: `6 passed`.

- [ ] **Step 5: Run *all* tests**

```bash
cd /Users/lobennett/grants/r01_rdoc/projects/expdeploy
uv run pytest -v
```

Expected: all tests pass (sanity + manifest + loader + importmap + renderer + fs + app).

- [ ] **Step 6: Commit**

```bash
cd /Users/lobennett/grants/r01_rdoc/projects/expdeploy
git add src/expdeploy/app.py tests/integration/
git commit -m "Add FastAPI app: GET / serves HTML, POST /api/data saves run, static mounts, healthz"
```

---

## Phase J — Typer CLI

### Task 17: `expdeploy version` + `expdeploy validate`

**Files:**
- Create: `/Users/lobennett/grants/r01_rdoc/projects/expdeploy/src/expdeploy/cli.py`
- Create: `/Users/lobennett/grants/r01_rdoc/projects/expdeploy/src/expdeploy/__main__.py`
- Create: `/Users/lobennett/grants/r01_rdoc/projects/expdeploy/tests/unit/test_cli.py`

- [ ] **Step 1: Write the failing test**

Write to `tests/unit/test_cli.py`:

```python
"""Tests for the Typer CLI (without spinning up uvicorn)."""

from __future__ import annotations

from pathlib import Path

import pytest
from typer.testing import CliRunner

from expdeploy import __version__
from expdeploy.cli import app

runner = CliRunner()

HELLO_TOML = """
[experiment]
exp_id = "hello"
name = "Hello world"
version = "1.0.0"
entry = "index.js"

[jspsych]
version = "8.2.3"
plugins = ["@jspsych/plugin-html-keyboard-response@2.1.0"]
"""


def test_version_command():
    result = runner.invoke(app, ["version"])
    assert result.exit_code == 0
    assert __version__ in result.stdout


def test_validate_valid_experiment(tmp_path):
    exp_dir = tmp_path / "hello"
    exp_dir.mkdir()
    (exp_dir / "manifest.toml").write_text(HELLO_TOML)
    (exp_dir / "index.js").write_text("export default () => {};")
    result = runner.invoke(app, ["validate", str(exp_dir)])
    assert result.exit_code == 0
    assert "ok" in result.stdout.lower()


def test_validate_missing_manifest(tmp_path):
    exp_dir = tmp_path / "empty"
    exp_dir.mkdir()
    result = runner.invoke(app, ["validate", str(exp_dir)])
    assert result.exit_code != 0
    assert "manifest.toml" in result.stdout or "manifest.toml" in str(result.exception)


def test_validate_bad_bids_task_label(tmp_path):
    bad_toml = HELLO_TOML + '\n[bids]\ntype = "fmri"\ntask = "n_back"\n'
    exp_dir = tmp_path / "bad"
    exp_dir.mkdir()
    (exp_dir / "manifest.toml").write_text(bad_toml)
    (exp_dir / "index.js").write_text("")
    result = runner.invoke(app, ["validate", str(exp_dir)])
    assert result.exit_code != 0
```

- [ ] **Step 2: Run the test to verify it fails**

```bash
cd /Users/lobennett/grants/r01_rdoc/projects/expdeploy
uv run pytest tests/unit/test_cli.py -v
```

Expected: `ModuleNotFoundError: No module named 'expdeploy.cli'`.

- [ ] **Step 3: Implement `src/expdeploy/cli.py`**

```python
"""expdeploy CLI — Typer-based."""

from __future__ import annotations

from pathlib import Path

import typer

from expdeploy import __version__
from expdeploy.loader import ExperimentLoader


app = typer.Typer(no_args_is_help=True, help="expdeploy — deploy jsPsych v8 experiments.")


@app.command()
def version() -> None:
    """Print the expdeploy version."""
    typer.echo(f"expdeploy {__version__}")


@app.command()
def validate(
    path: Path = typer.Argument(..., exists=True, file_okay=False, dir_okay=True),
) -> None:
    """Validate an experiment manifest at PATH."""
    try:
        ExperimentLoader().load(path)
    except Exception as exc:  # noqa: BLE001
        typer.echo(f"INVALID: {exc}", err=True)
        raise typer.Exit(code=1) from exc
    typer.echo("ok")
```

- [ ] **Step 4: Run the tests and verify they pass**

```bash
cd /Users/lobennett/grants/r01_rdoc/projects/expdeploy
uv run pytest tests/unit/test_cli.py -v
```

Expected: `4 passed`.

- [ ] **Step 5: Write `src/expdeploy/__main__.py`**

This lets the e2e test (and anyone else) run `python -m expdeploy` and have it dispatch to the Typer app.

```python
"""Entry point for `python -m expdeploy`."""

from expdeploy.cli import app

if __name__ == "__main__":
    app()
```

- [ ] **Step 6: Smoke-test both entry points**

```bash
cd /Users/lobennett/grants/r01_rdoc/projects/expdeploy
uv run expdeploy version
uv run python -m expdeploy version
uv run expdeploy --help
```

Expected: first two each print `expdeploy 0.1.0a0`; third prints help listing `version` + `validate`.

- [ ] **Step 7: Commit**

```bash
cd /Users/lobennett/grants/r01_rdoc/projects/expdeploy
git add src/expdeploy/cli.py src/expdeploy/__main__.py tests/unit/test_cli.py
git commit -m "Add Typer CLI with version and validate subcommands"
```

---

### Task 18: `expdeploy run` — boot uvicorn with a real experiment

**Files:**
- Modify: `/Users/lobennett/grants/r01_rdoc/projects/expdeploy/src/expdeploy/cli.py`
- Modify: `/Users/lobennett/grants/r01_rdoc/projects/expdeploy/tests/unit/test_cli.py`

The `run` command boots a uvicorn server. Testing the *actual* uvicorn launch is e2e territory; in unit tests, we mock uvicorn.run to verify the wiring.

- [ ] **Step 1: Add the failing test**

Append to `tests/unit/test_cli.py`:

```python
from unittest.mock import patch


def test_run_command_wires_uvicorn(tmp_path):
    exp_dir = tmp_path / "hello"
    exp_dir.mkdir()
    (exp_dir / "manifest.toml").write_text(HELLO_TOML)
    (exp_dir / "index.js").write_text("export default () => {};")

    with patch("expdeploy.cli.uvicorn") as mock_uvicorn:
        result = runner.invoke(
            app,
            ["run", str(exp_dir), "--subject", "01", "--port", "9091", "--no-browser"],
        )
    assert result.exit_code == 0, result.stdout
    assert mock_uvicorn.run.called
    kwargs = mock_uvicorn.run.call_args.kwargs
    assert kwargs["port"] == 9091
    assert kwargs["host"] == "127.0.0.1"


def test_run_command_rejects_busy_port(tmp_path):
    import socket

    exp_dir = tmp_path / "hello"
    exp_dir.mkdir()
    (exp_dir / "manifest.toml").write_text(HELLO_TOML)
    (exp_dir / "index.js").write_text("export default () => {};")

    # Open a socket on a port to make it busy
    sock = socket.socket()
    sock.bind(("127.0.0.1", 0))
    busy_port = sock.getsockname()[1]
    try:
        result = runner.invoke(
            app,
            ["run", str(exp_dir), "--subject", "01", "--port", str(busy_port), "--no-browser"],
        )
        assert result.exit_code != 0
        # Look for the suggested-next-port hint
        assert "busy" in result.stdout.lower() or "in use" in result.stdout.lower()
    finally:
        sock.close()
```

- [ ] **Step 2: Run the test to verify it fails**

```bash
cd /Users/lobennett/grants/r01_rdoc/projects/expdeploy
uv run pytest tests/unit/test_cli.py::test_run_command_wires_uvicorn -v
```

Expected: AttributeError or missing-command error (the `run` command doesn't exist yet).

- [ ] **Step 3: Extend `src/expdeploy/cli.py`**

Add at the top, in the existing imports:

```python
import socket
import webbrowser
from pathlib import Path

import typer
import uvicorn

from expdeploy import __version__
from expdeploy.app import AppConfig, create_app
from expdeploy.loader import ExperimentLoader
from expdeploy.storage.fs import FSAdapter
```

(Keep the existing module docstring + `app` + `version` + `validate` commands; just add the new imports and the new command below them.)

Append the new command:

```python
def _port_is_free(port: int, host: str = "127.0.0.1") -> bool:
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        try:
            sock.bind((host, port))
        except OSError:
            return False
    return True


def _next_free_port(start: int, host: str = "127.0.0.1", attempts: int = 100) -> int | None:
    for candidate in range(start + 1, start + 1 + attempts):
        if _port_is_free(candidate, host):
            return candidate
    return None


@app.command()
def run(
    path: Path = typer.Argument(..., exists=True, file_okay=False, dir_okay=True),
    subject: str = typer.Option(..., "--subject", help="Subject label (e.g., 01)."),
    session: str | None = typer.Option(None, "--session", help="Session label."),
    run_num: str | None = typer.Option(None, "--run", help="Run label."),
    data_dir: Path = typer.Option(Path("./data"), "--data-dir"),
    port: int = typer.Option(8080, "--port"),
    no_browser: bool = typer.Option(False, "--no-browser"),
) -> None:
    """Serve an experiment on a local port."""
    if not _port_is_free(port):
        suggestion = _next_free_port(port)
        msg = f"Port {port} is in use."
        if suggestion is not None:
            msg += f" Try --port {suggestion}."
        typer.echo(msg, err=True)
        raise typer.Exit(code=2)

    experiment = ExperimentLoader().load(path)
    from expdeploy import jspsych_assets

    config = AppConfig(
        experiment=experiment,
        vendored_root=Path(jspsych_assets.__file__).resolve().parent,
        storage=FSAdapter(data_dir=data_dir),
        subject_id=subject,
        session_num=session,
        run_num=run_num,
    )
    fastapi_app = create_app(config)

    url = f"http://127.0.0.1:{port}/"
    typer.echo(f"Serving {experiment.manifest.experiment.exp_id} at {url}")
    if not no_browser:
        webbrowser.open(url)
    uvicorn.run(fastapi_app, host="127.0.0.1", port=port, log_level="info")
```

- [ ] **Step 4: Run the tests and verify they pass**

```bash
cd /Users/lobennett/grants/r01_rdoc/projects/expdeploy
uv run pytest tests/unit/test_cli.py -v
```

Expected: `6 passed`.

- [ ] **Step 5: Commit**

```bash
cd /Users/lobennett/grants/r01_rdoc/projects/expdeploy
git add src/expdeploy/cli.py tests/unit/test_cli.py
git commit -m "Add 'expdeploy run' command (uvicorn boot, port-busy check, browser open)"
```

---

## Phase K — Hello-world example experiment

### Task 19: `examples/hello_world/`

**Files:**
- Create: `/Users/lobennett/grants/r01_rdoc/projects/expdeploy/examples/hello_world/manifest.toml`
- Create: `/Users/lobennett/grants/r01_rdoc/projects/expdeploy/examples/hello_world/index.js`
- Create: `/Users/lobennett/grants/r01_rdoc/projects/expdeploy/examples/hello_world/style.css`

- [ ] **Step 1: Write `examples/hello_world/manifest.toml`**

```toml
[experiment]
exp_id = "hello"
name = "Hello world"
version = "1.0.0"
entry = "index.js"
style = "style.css"
estimated_minutes = 1

[experiment.metadata]
contributors = ["expdeploy"]
notes = "Single-trial example used by expdeploy smoke tests."

[jspsych]
version = "8.2.3"
plugins = ["@jspsych/plugin-html-keyboard-response@2.1.0"]
init = { display_element = "jspsych-target" }
```

- [ ] **Step 2: Write `examples/hello_world/index.js`**

```javascript
import { initJsPsych } from "jspsych";
import htmlKeyboardResponse from "@jspsych/plugin-html-keyboard-response";

export default function build() {
  const jsPsych = initJsPsych({
    display_element: "jspsych-target",
    on_finish: () => {
      const payload = {
        exp_id: window.expdeploy.expId,
        subject_id: window.expdeploy.subjectId,
        session_num: window.expdeploy.sessionNum,
        run_num: window.expdeploy.runNum,
        deploy_version: window.expdeploy.deployVersion,
        trials: jsPsych.data.get().values(),
        status: "finished",
      };
      window.expdeploy
        .submit(payload)
        .then((result) => {
          document.body.innerHTML +=
            '<div style="text-align:center;margin-top:2em;">' +
            "<h1>Saved.</h1>" +
            "<p>Path: " +
            (result.path || "(none)") +
            "</p></div>";
        })
        .catch((err) => {
          document.body.innerHTML +=
            '<div style="color:red;text-align:center;margin-top:2em;">' +
            "<h1>Save failed</h1><pre>" +
            String(err) +
            "</pre></div>";
        });
    },
  });

  jsPsych.run([
    {
      type: htmlKeyboardResponse,
      stimulus:
        "<h1>Hello, world!</h1><p>Press any key to finish.</p>",
    },
  ]);
}
```

- [ ] **Step 3: Write `examples/hello_world/style.css`**

```css
body {
  font-family: system-ui, -apple-system, sans-serif;
  margin: 0;
  background: #fafafa;
}

#jspsych-target {
  max-width: 720px;
  margin: 4em auto;
  text-align: center;
}

h1 {
  font-weight: 600;
}
```

- [ ] **Step 4: Validate the hello-world**

```bash
cd /Users/lobennett/grants/r01_rdoc/projects/expdeploy
uv run expdeploy validate ./examples/hello_world
```

Expected: prints `ok`, exits 0.

- [ ] **Step 5: Commit**

```bash
cd /Users/lobennett/grants/r01_rdoc/projects/expdeploy
git add examples/hello_world/
git commit -m "Add examples/hello_world (single-trial jsPsych v8 demo)"
```

---

## Phase L — Playwright e2e test

### Task 20: Browser-driven hello-world round-trip

**Files:**
- Create: `/Users/lobennett/grants/r01_rdoc/projects/expdeploy/tests/e2e/__init__.py` (empty)
- Create: `/Users/lobennett/grants/r01_rdoc/projects/expdeploy/tests/e2e/test_hello_world.py`

- [ ] **Step 1: Install Playwright browsers**

```bash
cd /Users/lobennett/grants/r01_rdoc/projects/expdeploy
uv run playwright install chromium
```

Expected: downloads chromium into `~/Library/Caches/ms-playwright/` (macOS) or equivalent.

- [ ] **Step 2: Write `tests/e2e/test_hello_world.py`**

```python
"""End-to-end test: Playwright drives a real browser through hello-world."""

from __future__ import annotations

import json
import socket
import subprocess
import sys
import time
from pathlib import Path

import httpx
import pytest
from playwright.sync_api import sync_playwright


REPO = Path(__file__).resolve().parents[2]
HELLO_DIR = REPO / "examples" / "hello_world"


def _free_port() -> int:
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        sock.bind(("127.0.0.1", 0))
        return sock.getsockname()[1]


def _wait_for_healthz(url: str, timeout_seconds: float = 15.0) -> None:
    deadline = time.monotonic() + timeout_seconds
    last_exc: Exception | None = None
    while time.monotonic() < deadline:
        try:
            r = httpx.get(url, timeout=2.0)
            if r.status_code == 200:
                return
        except Exception as exc:  # noqa: BLE001
            last_exc = exc
        time.sleep(0.25)
    msg = f"server at {url} never became healthy"
    if last_exc is not None:
        msg += f" (last error: {last_exc})"
    raise TimeoutError(msg)


@pytest.mark.e2e
def test_hello_world_browser_round_trip(tmp_path):
    port = _free_port()
    data_dir = tmp_path / "data"
    proc = subprocess.Popen(
        [
            sys.executable,
            "-m",
            "expdeploy",
            "run",
            str(HELLO_DIR),
            "--subject",
            "01",
            "--data-dir",
            str(data_dir),
            "--port",
            str(port),
            "--no-browser",
        ],
        cwd=str(REPO),
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
    )
    try:
        _wait_for_healthz(f"http://127.0.0.1:{port}/healthz")

        with sync_playwright() as pw:
            browser = pw.chromium.launch()
            page = browser.new_page()
            page.goto(f"http://127.0.0.1:{port}/")
            # Wait for the jsPsych target to render the stimulus
            page.wait_for_selector("text=Hello, world!", timeout=10_000)
            # Press a key — Space is fine; html-keyboard-response accepts any.
            page.keyboard.press("Space")
            # Wait for the "Saved." confirmation rendered by index.js
            page.wait_for_selector("text=Saved.", timeout=10_000)
            browser.close()
    finally:
        proc.terminate()
        proc.wait(timeout=10)

    # Verify the run was saved to disk
    saved_files = list((data_dir / "raw" / "sub-01").glob("*.json"))
    assert len(saved_files) == 1, f"expected one saved run, got {saved_files}"
    saved = json.loads(saved_files[0].read_text())
    # The single trial should be present in the payload
    trials = saved["trials"]
    assert len(trials) == 1
    assert trials[0]["trial_type"] == "html-keyboard-response"
```

- [ ] **Step 3: Run the e2e test**

```bash
cd /Users/lobennett/grants/r01_rdoc/projects/expdeploy
uv run pytest tests/e2e/test_hello_world.py -v -m e2e
```

Expected: `1 passed`. (Allow a generous timeout — the first run downloads jsPsych assets at import time and Playwright launches chromium.)

- [ ] **Step 4: Commit**

```bash
cd /Users/lobennett/grants/r01_rdoc/projects/expdeploy
git add tests/e2e/
git commit -m "Add Playwright e2e: browser-driven hello-world round-trip to disk"
```

---

## Phase M — GitHub Actions CI

### Task 21: CI workflow

**Files:**
- Create: `/Users/lobennett/grants/r01_rdoc/projects/expdeploy/.github/workflows/ci.yml`

- [ ] **Step 1: Write `.github/workflows/ci.yml`**

```yaml
name: CI

on:
  push:
    branches: [main]
  pull_request:
    branches: [main]

jobs:
  test:
    runs-on: ${{ matrix.os }}
    strategy:
      fail-fast: false
      matrix:
        os: [ubuntu-latest, macos-latest]
        python: ["3.11", "3.12"]

    steps:
      - uses: actions/checkout@v4

      - name: Install uv
        uses: astral-sh/setup-uv@v3
        with:
          version: "0.5.x"

      - name: Set up Python ${{ matrix.python }}
        run: uv python install ${{ matrix.python }}

      - name: Install dependencies
        run: uv sync --extra dev

      - name: Install Playwright browsers
        run: uv run playwright install --with-deps chromium

      - name: Lint (ruff)
        run: |
          uv run ruff check .
          uv run ruff format --check .

      - name: Type check (mypy)
        run: uv run mypy src/expdeploy

      - name: Unit + integration tests
        run: uv run pytest tests/unit tests/integration -v

      - name: End-to-end (Playwright)
        run: uv run pytest tests/e2e -v -m e2e
```

- [ ] **Step 2: Commit**

```bash
cd /Users/lobennett/grants/r01_rdoc/projects/expdeploy
git add .github/
git commit -m "Add GitHub Actions CI: ruff, mypy, pytest unit/integration/e2e on Ubuntu+macOS, py3.11+3.12"
```

- [ ] **Step 3 (post-push, optional): create the GitHub repo and push**

The user can run this once they have `gh` authenticated:

```bash
cd /Users/lobennett/grants/r01_rdoc/projects/expdeploy
gh repo create lobennett/expdeploy --public --source=. --description "Modern Python deploy tool for jsPsych v8 experiments"
git push -u origin main
```

This is optional and outside the scope of this plan's CI verification (CI runs on push). Leave to the user.

---

## Final sanity sweep

### Task 22: Full local verification

**Files:** none.

- [ ] **Step 1: Lint clean**

```bash
cd /Users/lobennett/grants/r01_rdoc/projects/expdeploy
uv run ruff check .
uv run ruff format --check .
```

Expected: both exit 0.

- [ ] **Step 2: Type clean**

```bash
cd /Users/lobennett/grants/r01_rdoc/projects/expdeploy
uv run mypy src/expdeploy
```

Expected: `Success: no issues found`.

- [ ] **Step 3: All tests pass**

```bash
cd /Users/lobennett/grants/r01_rdoc/projects/expdeploy
uv run pytest -v
```

Expected: all tests pass (unit + integration + e2e).

- [ ] **Step 4: Smoke-test the CLI end-to-end manually**

```bash
cd /Users/lobennett/grants/r01_rdoc/projects/expdeploy
uv run expdeploy run ./examples/hello_world --subject 01 --port 8080 --no-browser
# In another terminal, open http://localhost:8080 in a real browser,
# press any key on the stimulus, see "Saved." confirmation.
# Then Ctrl-C the server and check:
ls ./data/raw/sub-01/
```

Expected: one JSON file named `sub-01_task-hello_beh.json` containing a `trials` array with one entry.

- [ ] **Step 5: No commit needed; this is verification only.**

---

## Summary of what Plan 1 produced

After Task 22 you have:

- A new repo at `/Users/lobennett/grants/r01_rdoc/projects/expdeploy/`.
- Pure-Python install via `uv`; no Node.js required.
- jsPsych v8.2.3 + 9 plugins vendored as browser-loadable ESM.
- Pydantic v2 manifest schema with BIDS task-label validation.
- Browser-native import maps that resolve `jspsych`, `@jspsych/plugin-*`, and `import_map_extras` aliases.
- FastAPI app: `GET /`, `POST /api/data`, `/healthz`, `/readyz`, static asset mounts.
- Typer CLI: `expdeploy version`, `validate`, `run`.
- `examples/hello_world/` runnable in seconds.
- Comprehensive tests at three tiers (unit, integration, Playwright e2e).
- ruff + mypy --strict + pre-commit + GitHub Actions CI matrix.

**Plan 2 (next):** full BIDS layout, SQLite catalog, RunSession, BatteryOrchestrator + 4 counterbalance schemes, `expdeploy init`/`status`/`sync`.

**Plan 3 (after):** Supabase adapter, Dockerfile + multi-arch base image, `expdeploy build` for study images, mkdocs site, release CI.
