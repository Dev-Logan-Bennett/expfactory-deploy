# expdeploy — Design Spec

**Date:** 2026-05-14
**Author:** Logan Bennett (lobennett) with Claude
**Status:** Approved by user — ready to plan implementation

## 1. Goal

Build `expdeploy`, a modern Python deploy tool for jsPsych v8 experiments that pays homage to the original `expfactory` while expanding scope. It targets the broader open-source cognitive-psychology / jsPsych community, lives in a separate repository from this one, and prioritizes robustness, reproducibility, and transparency.

### 1.1 Headline goals

- Serve jsPsych v8 experiments locally with **no Node.js dependency for experimenters** — pure-Python install via `uv`.
- Canonical jsPsych v8 **ESM** authoring: `import { initJsPsych } from 'jspsych'` works via browser-native import maps injected by the server.
- **Local imports** in experiments (`import { sampleITI } from './lib/iti.js'`) work natively without a bundler.
- **Local-first storage**: every run writes JSON + CSV to disk; SQLite catalog indexes runs; **Supabase** is the first optional remote sync target.
- **BIDS-compatible** filename layout for fMRI and behavioral experiments.
- **Batteries**: define inline (`--exps a,b,c`) or via `battery.toml`. Four counterbalance schemes: Latin square, fixed, seeded-random, user-supplied.
- **Reproducibility via OCI**: slim multi-arch base image + `expdeploy build` to produce study-specific images that encode an entire experiment as a signed scientific artifact.
- **Robustness**: Pydantic-validated data POST, typed CLI, comprehensive test suite (pytest + Playwright e2e).
- **Transparency**: no bundler opacity — JS files served as authored; sourcemaps not needed.

### 1.2 Non-goals (v0.1)

- Live multi-subject dashboard (no websockets in v0.1).
- Subject authentication / password gating.
- Other remote storage adapters beyond Supabase (Firebase, MongoDB, S3) — adapter Protocol defined in v0.1, implementations deferred.
- Backward compatibility with `expfactory_deploy_local`'s `config.json` schema — clean break confirmed by user.
- jsPsych Builder webpack-style bundling — ESM-first only.
- Cosign signing of images — deferred to v0.2.
- Apptainer-specific CI test matrix (image is OCI so it should work; no first-class promise yet).
- HIPAA-level PII handling — subject IDs are treated as opaque strings; docs will warn against putting MRNs / names there.

### 1.3 Audience

Broader open-source cognitive-psychology / jsPsych community. Public-quality docs (mkdocs-material), semver, CONTRIBUTING.md, GitHub Actions CI, API stability after v1.0.

## 2. Context — what we're replacing

The current package `expfactory_deploy_local` (this repo) deploys jsPsych v7 experiments using `web.py`, a `config.json` schema with a `run` list of script tags, and per-port session directories. It supports BIDS-naming for fMRI outputs and a `--group_index` counterbalance variable. It bundles jsPsych v7 in `static/jspsych7/`.

The new package is a clean rewrite in a separate repo. Existing experiments in `rdoc-fmri-experiments/` will be rewritten by hand for the new schema — no migration tooling. Examples in this spec use canonical community tasks (`flanker`, `stroop`, `nback`) rather than lab-specific names.

## 3. System architecture

```
┌──────────────────────────────────────────────────────────────────┐
│  expdeploy CLI  (Typer)                                          │
│  ─ run     ─ init     ─ validate     ─ build     ─ status        │
│  ─ sync    ─ supabase ─ version                                  │
└────────┬─────────────────────────────────────────────────────────┘
         │
         ▼
┌──────────────────────────────────────────────────────────────────┐
│  expdeploy.app  (FastAPI / ASGI on uvicorn)                      │
│                                                                  │
│  GET  /              → ExperimentRenderer → HTML w/ import map   │
│  GET  /static/*      → jsPsych ESM assets, exp files (mounted)   │
│  POST /api/data      → DataIngest (Pydantic-validated)           │
│  GET  /api/state     → BatteryState (which exp is next)          │
│  POST /api/state     → advance / skip / reset                    │
│  GET  /healthz       → liveness                                  │
│  GET  /readyz        → readiness                                 │
└────────┬─────────────────────────────────────────────────────────┘
         │
         ▼
┌──────────────────────────────────────────────────────────────────┐
│  Core domain                                                     │
│                                                                  │
│  ExperimentLoader   ──reads──>  ManifestSchema (Pydantic)        │
│  ImportMapBuilder   ──emits──>  HTML <script type=importmap>     │
│  BatteryOrchestrator──uses──>  CounterbalanceStrategy (4 impls)  │
│  RunSession         ──tracks──> subject_id, session_num, run_num │
└────────┬─────────────────────────────────────────────────────────┘
         │
         ▼
┌──────────────────────────────────────────────────────────────────┐
│  Storage layer  (StorageAdapter Protocol)                        │
│                                                                  │
│   ┌──────────────┐   ┌──────────────┐   ┌──────────────────┐     │
│   │ FSAdapter    │   │ SQLiteCatalog│   │ SupabaseAdapter  │     │
│   │ (always-on)  │   │ (always-on)  │   │ (optional sync)  │     │
│   └──────────────┘   └──────────────┘   └──────────────────┘     │
│                                                                  │
│  Stack model: FS write is non-negotiable; SQLite indexes runs;   │
│  remote adapters are 0..N best-effort sync targets on top.       │
└──────────────────────────────────────────────────────────────────┘
```

### 3.1 Module layout — single package, optional extras

```
expdeploy/
├── pyproject.toml            # uv-managed; extras: [supabase], [container], [dev]
├── uv.lock
├── README.md
├── LICENSE                   # MIT
├── CONTRIBUTING.md
├── Dockerfile                # base image
├── docs/                     # mkdocs-material site
├── examples/
│   └── hello_world/          # minimal experiment validating the install
├── tests/
│   ├── unit/
│   ├── integration/
│   ├── e2e/                  # Playwright
│   └── fixtures/             # canonical flanker/stroop/nback test experiments + battery
└── src/expdeploy/
    ├── __init__.py
    ├── app.py                # FastAPI app factory
    ├── cli.py                # Typer entry point (`expdeploy …`)
    ├── manifest.py           # Pydantic models for manifest.toml, battery.toml
    ├── loader.py             # ExperimentLoader, ImportMapBuilder
    ├── battery.py            # BatteryOrchestrator + CounterbalanceStrategy
    ├── session.py            # RunSession (subject/session/run state, file-locked)
    ├── storage/
    │   ├── base.py           # StorageAdapter Protocol + RunRecord, RunStatus, etc.
    │   ├── fs.py             # FSAdapter (JSON + BIDS layout)
    │   ├── sqlite.py         # SQLiteCatalog
    │   └── supabase.py       # SupabaseAdapter (lazy import; in [supabase] extra)
    ├── jspsych_assets/       # vendored jsPsych v8.x ESM + core plugins
    └── templates/
        └── deploy.html.j2    # Jinja template w/ import map slot
```

### 3.2 Key architectural choices

- **Single package + optional extras** (`uv add expdeploy[supabase]`) rather than a multi-package monorepo. Cleaner v0.1; can split if it ever justifies the overhead.
- **`StorageAdapter` is a `typing.Protocol`** (structural typing), not a base class. Users bring adapters without inheritance.
- **jsPsych v8 ESM assets are vendored** in `src/expdeploy/jspsych_assets/`. Built once at release time from upstream `@jspsych/*` npm packages, pinned to specific versions. Multiple versions can coexist (`jspsych_assets/8.2.3/`, `jspsych_assets/8.3.0/`). No internet at runtime — supports air-gapped scanner rooms.
- **Sessions are file-based** (`state/sub-<id>.json`), file-locked via `filelock`. Survives server restart; no Redis dep; single-subject-per-server (matches current model).
- **Browser support**: import maps require Chrome 89+, Firefox 108+, Safari 16.4+ (all 2023+). jsPsych v8 itself already targets modern browsers, so this is strictly more lenient than what experiments will require. Pre-2023 browsers (iPad Safari 15, older Chromebooks) are not supported.

## 4. Experiment & battery model

### 4.1 Experiment on disk

```
experiments/flanker/
├── manifest.toml         # required
├── index.js              # required, ESM entry point
├── style.css             # optional
├── assets/               # optional: images, audio, video
│   └── stim_1.png
├── designs/              # optional: fMRI event timing CSVs
│   └── design_1.csv
└── lib/                  # optional: local JS modules
    ├── iti.js
    └── feedback.js
```

### 4.2 `manifest.toml`

```toml
[experiment]
exp_id = "flanker"
name = "Flanker task"
version = "1.0.0"
entry = "index.js"            # ESM entry point
style = "style.css"           # optional
estimated_minutes = 8

[experiment.metadata]
cognitive_atlas_task_id = "trm_4f24126c22011"
contributors = ["Lab Member A", "Lab Member B"]
notes = "Eriksen flanker; congruent vs. incongruent."

[jspsych]
# Defaults to the version vendored in the deploy package; override per experiment.
version = "8.2.3"
plugins = [
  "@jspsych/plugin-html-keyboard-response@2.1.0",
  "@jspsych/plugin-fullscreen@2.1.0",
  "@jspsych/plugin-instructions@2.1.0",
  "@jspsych/plugin-preload@2.1.0",
]
init = { fullscreen = true, display_element = "jspsych-target" }

[bids]
# Drives BIDS-layout output. Omit this section entirely for non-BIDS experiments.
type = "fmri"                 # one of: fmri, behavioral
task = "flanker"              # BIDS task label: alphanumeric only

[bids.columns.trial_type]     # optional per-column descriptions for _events.json sidecar
description = "Congruency of the flanker stimulus."
levels = { congruent = "Congruent", incongruent = "Incongruent" }

[import_map_extras]
# Optional aliases available to index.js
"@lab/iti" = "./lib/iti.js"
"@lab/feedback" = "./lib/feedback.js"
```

The Pydantic schema is the source of truth. Unknown keys → validation error citing the offending field path. A JSON Schema is published for editor autocomplete.

**BIDS task label validation**: `[a-zA-Z0-9]+` only. `nback` valid; `n_back` invalid. Enforced at manifest load time, not at write time.

### 4.3 `index.js`

```js
import { initJsPsych } from 'jspsych';
import htmlKeyboardResponse from '@jspsych/plugin-html-keyboard-response';
import fullscreen from '@jspsych/plugin-fullscreen';
import { sampleITI } from '@lab/iti';
import { showFeedback } from '@lab/feedback';

// Globals injected by the deploy server; contract is documented + typed (TS types shipped).
const { subjectId, sessionNum, runNum, groupIndex, vars } = window.expdeploy;

export default function build() {
  const jsPsych = initJsPsych({
    on_finish: () => window.expdeploy.submit(),
  });

  const timeline = [/* ... */];
  jsPsych.run(timeline);
}
```

The deploy server injects:
- `window.expdeploy.subjectId`, `.sessionNum`, `.runNum`, `.groupIndex`, `.vars` (from `--vars` flag), `.expId`, `.deployVersion`
- `window.expdeploy.submit()` — collects `jsPsych.data.get()` + browser metadata + interactionData, POSTs to `/api/data`, advances the battery on a 2xx response, surfaces errors on 4xx/5xx

### 4.4 `battery.toml`

```toml
[battery]
name = "RDoC fMRI battery v1"
counterbalance = "latin_square"   # latin_square | fixed | seeded_random | user_supplied

# Only used by counterbalance = "user_supplied":
# order_csv = "./orders.csv"      # columns: subject_id, exp_id_1, exp_id_2, ...

[[experiments]]
exp_id = "flanker"
path = "./flanker"

[[experiments]]
exp_id = "stroop"
path = "./stroop"

[[experiments]]
exp_id = "nback"
path = "./nback"

[breaks]
# Optional rest screens injected between experiments
between_each = { duration_seconds = 30, message = "Rest. Press SPACE when ready." }
```

### 4.5 What the server does on `GET /`

1. Read battery state for the subject from `state/sub-<id>.json`, or initialize it from the battery manifest + chosen counterbalance scheme.
2. Pick the next incomplete experiment.
3. Load that experiment's `manifest.toml` (Pydantic-validated).
4. Build an import map merging: vendored jsPsych ESM paths, requested plugin versions, the experiment's own root (for `./` imports), and any `import_map_extras`.
5. Render `deploy.html.j2` with the import map + a `<script type="module">` that imports the experiment's `index.js` and calls `build()`.

## 5. Storage layer

### 5.1 `StorageAdapter` Protocol

```python
# src/expdeploy/storage/base.py
from typing import Protocol, runtime_checkable

@runtime_checkable
class StorageAdapter(Protocol):
    name: str  # "fs" | "sqlite" | "supabase" | ...

    def save_run(self, run: RunRecord) -> SaveResult: ...
    def save_trials(self, run: RunRecord, trials: list[dict]) -> SaveResult: ...
    def save_events_tsv(self, run: RunRecord, events_df) -> SaveResult: ...
    def update_status(self, run_id: str, status: RunStatus) -> None: ...
    def health_check(self) -> AdapterHealth: ...
```

`RunRecord`, `RunStatus`, `SaveResult`, `AdapterHealth` are Pydantic models. Each adapter handles its own errors; the orchestrator collects results and logs partials.

### 5.2 Write flow (POST /api/data)

```
client POST  →  Pydantic validate  →  RunRecord
                                          ↓
                              FS.save_run (raw JSON)        ← required, must succeed
                                          ↓
                            FS.save_events_tsv (BIDS)       ← if [bids] block in manifest
                                          ↓
                              SQLite.save_run (index)       ← required, must succeed
                                          ↓
                          for each configured remote:
                              adapter.save_run (best-effort, async-fire-and-forget)
                                          ↓
                              return 200 + {run_id, fs_path, remote_status: [...]}
```

- FS or SQLite failure → 5xx response. Browser surfaces error UI + offers JSON download as fallback.
- Remote failure → logged + `remote_sync` row added with `status=failed`. Never blocks the response. Replayable via `expdeploy sync`.

### 5.3 Filesystem layout (BIDS-flavored)

For a flanker fMRI experiment, subject 01, session 1, run 1:

```
data/
├── raw/                                        # raw jsPsych JSON, always saved
│   └── sub-01/
│       └── ses-01/
│           └── sub-01_ses-01_task-flanker_run-01_beh.json
└── bids/                                       # only if [bids] in manifest
    ├── dataset_description.json                # auto-generated, idempotent
    ├── participants.tsv                        # append-on-first-encounter
    └── sub-01/
        └── ses-01/
            ├── func/                           # if bids.type = "fmri"
            │   ├── sub-01_ses-01_task-flanker_run-01_events.tsv
            │   └── sub-01_ses-01_task-flanker_run-01_events.json   # sidecar
            └── beh/                            # if bids.type = "behavioral"
                ├── sub-01_ses-01_task-flanker_run-01_beh.tsv
                └── sub-01_ses-01_task-flanker_run-01_beh.json
```

**BIDS details:**
- `dataset_description.json` written on first save, idempotent thereafter. Includes `Name`, `BIDSVersion`, `DatasetType: "raw"`, `Authors` (from manifest contributors).
- `participants.tsv` gets a row appended on first encounter of a new subject. File-locked atomic append.
- `_events.tsv` columns (fMRI): BIDS-mandated `onset` (seconds from run start), `duration`, `trial_type`, plus user-defined columns from trial data.
- `_events.json` sidecar auto-generated from `[bids.columns.*]` schema in the manifest.
- `participant_id` always uses zero-padded labels (`sub-01`, not `sub-1`) per BIDS convention. Enforced by manifest validator.
- Optional `expdeploy validate --bids ./data/bids` invokes the official `bids-validator` (Node-based) if available; otherwise a Python-side subset.

### 5.4 SQLite catalog schema

One file per data root: `data/catalog.sqlite`.

```sql
CREATE TABLE runs (
  run_id TEXT PRIMARY KEY,           -- ULID
  exp_id TEXT NOT NULL,
  exp_version TEXT,
  subject_id TEXT NOT NULL,
  session_num TEXT,
  run_num TEXT,
  battery_id TEXT,                   -- FK to batteries, nullable
  group_index INTEGER,               -- counterbalance row
  started_at TEXT NOT NULL,          -- ISO8601 UTC
  ended_at TEXT,
  status TEXT NOT NULL,              -- started | finished | aborted | declined
  raw_path TEXT NOT NULL,
  events_path TEXT,
  jspsych_version TEXT,
  deploy_version TEXT,
  client_user_agent TEXT,
  notes TEXT
);

CREATE TABLE batteries (
  battery_id TEXT PRIMARY KEY,
  name TEXT,
  manifest_hash TEXT,                -- sha256 of battery.toml
  counterbalance TEXT,
  created_at TEXT
);

CREATE TABLE remote_sync (
  run_id TEXT REFERENCES runs(run_id),
  adapter TEXT NOT NULL,             -- "supabase" | ...
  status TEXT NOT NULL,              -- pending | synced | failed
  attempted_at TEXT,
  remote_uri TEXT,
  error TEXT,
  PRIMARY KEY (run_id, adapter)
);

CREATE INDEX idx_runs_subject ON runs(subject_id, session_num, run_num);
CREATE INDEX idx_remote_sync_status ON remote_sync(status, adapter);
```

`expdeploy sync` queries `remote_sync where status != 'synced'` and replays writes. Idempotent.

### 5.5 Supabase adapter

- Lives in `src/expdeploy/storage/supabase.py`; lazy-imports the `supabase` Python SDK. Only installed via `expdeploy[supabase]` extra.
- Two destinations per run:
  - **Postgres table** `expdeploy.runs` (mirrors local SQLite, plus a `trials` JSONB column).
  - **Storage bucket** `expdeploy-raw/`, one file per run at `sub-01/ses-01/sub-01_ses-01_task-flanker_run-01_beh.json`.
- Config via env vars (`SUPABASE_URL`, `SUPABASE_SERVICE_ROLE_KEY`) or `--storage-config supabase.toml`.
- `expdeploy supabase migrate` runs idempotent DDL. Documented SQL for users who prefer to apply by hand.
- Network failures → logged + `remote_sync` row inserted with `status=failed`. Retried by `expdeploy sync`.
- **Security note (will appear loudly in docs)**: service role key is required because participants don't authenticate; anon key + RLS would force a Supabase Auth flow that doesn't fit lab workflow.

## 6. Counterbalancing

Four schemes, each a `CounterbalanceStrategy` (Pydantic-typed factory). Strategies return an ordered list of `exp_id`s for a given subject. Deterministic where possible.

```python
class CounterbalanceStrategy(Protocol):
    name: str
    def order_for(self, subject_id: str, experiments: list[ExpRef]) -> list[ExpRef]: ...
```

| Scheme | Behavior | When to use |
|---|---|---|
| `fixed` | Returns `experiments` verbatim, ignores `subject_id`. | Piloting, single-subject runs, fMRI runs where order is fixed by protocol. |
| `latin_square` | Generates a balanced K×K Latin square (K = number of experiments). `row = int(subject_id) mod K`. | Standard fMRI / behavioral batteries; balances first-experiment effects. Requires int-parseable subject IDs. |
| `seeded_random` | `random.Random(seed=subject_id).shuffle(experiments)`. Deterministic per subject; not balanced across subjects. | Online studies with many subjects where balance averages out. |
| `user_supplied` | Reads `order_csv` (columns: `subject_id, pos_1, pos_2, ...`). Looks up the row for this subject. | Custom designs (Williams, block-randomized), pre-registered orderings, replication. |

**Subject-id parsing.** For `latin_square`, non-integer IDs raise a typed error at battery-start time, not mid-run.

**Determinism guarantee.** Given identical `(battery.toml, subject_id, expdeploy version)`, all four schemes produce identical orders. Recorded in SQLite (`runs.group_index`) and in the raw JSON for post-hoc verification.

**Order materialization.** On first subject contact, the chosen order is written to `state/sub-<id>.json` and never recomputed for that subject — prevents accidental reordering mid-session if the manifest is edited.

## 7. Web server, sessions, and data flow

### 7.1 FastAPI route table

```
GET   /                          → serve current experiment HTML (with import map)
GET   /api/state                 → battery state for current subject (JSON)
POST  /api/state                 → advance | skip | reset
POST  /api/data                  → ingest run data (Pydantic-validated)
GET   /static/jspsych/{path}     → vendored jsPsych ESM assets
GET   /static/exp/{exp_id}/{p}   → experiment files (from mounted experiment dirs)
GET   /static/lib/{path}         → import_map_extras targets
GET   /healthz                   → liveness probe
GET   /readyz                    → readiness probe
```

HTML at `/` is generated per-request from `templates/deploy.html.j2`:
- `<script type="importmap">` with vendored jsPsych paths + plugin paths + `import_map_extras`
- `<script>window.expdeploy = { subjectId, sessionNum, runNum, groupIndex, expId, deployVersion, vars, submit }</script>`
- `<script type="module">import build from "/static/exp/<id>/index.js"; build();</script>`

### 7.2 POST /api/data — Pydantic schema

```python
class DataPayload(BaseModel):
    exp_id: str = Field(pattern=r"^[a-zA-Z0-9_-]+$", max_length=128)
    subject_id: str = Field(pattern=r"^[a-zA-Z0-9-]+$", max_length=64)
    session_num: str | None = None
    run_num: str | None = None
    started_at: datetime
    ended_at: datetime
    status: Literal["finished", "aborted", "declined"]
    jspsych_version: str
    deploy_version: str
    trials: list[dict[str, Any]]
    interaction_data: list[dict] = []
    browser: BrowserInfo
    client_clock_skew_ms: int | None = None
```

- 422 on validation failure, with offending field path.
- 2xx on success: `{run_id, status, remote_sync: [...]}`. Browser advances.
- 4xx/5xx → browser shows error modal with "Download data as JSON" fallback button so the subject's session is never lost.

### 7.3 Sessions — file-based, per-subject

```
state/
├── sub-01.json           # {battery_id, order: [...], completed: [...], current: "stroop"}
├── sub-02.json
└── _meta.json            # last-server-start timestamp, deploy_version, etc.
```

- One state file per subject. Atomic via tempfile + `os.replace`.
- File-locked on read/write (via `filelock`).
- Server restart: state durable; subject resumes.
- No port-coupled session storage (the current package's `sessions_<port>` directories go away).
- Reset endpoint (`POST /api/state {"op": "reset"}`) clears one subject's state.

### 7.4 Static assets

- **jsPsych ESM** served from package data dir (via `importlib.resources`) and FastAPI `StaticFiles`. Mounted at `/static/jspsych/`. `Cache-Control: public, max-age=31536000, immutable` (version is in path).
- **Experiment files** mounted at `/static/exp/<exp_id>/`, sourced from the experiment's directory on disk (no symlinks — departure from current package; symlinks complicate container + Windows support).
- **Local imports** (`import x from './lib/iti.js'`) resolve to `/static/exp/<exp_id>/lib/iti.js` because the import map declares the experiment's root.

### 7.5 Port handling

Single `--port` arg, default `8080`. If busy, the CLI errors with a clear message and a suggested next port. **No auto-retry** — explicit departure from the current package, which spawns `sessions_8080`…`sessions_8085` directories on retries.

### 7.6 Error UX

- Server error during POST → browser modal with the error + "Download data as JSON" button.
- Server crash mid-run → browser detects via failed `/healthz` poll (every 30s); reconnection UI.
- Adapter health failures at startup → CLI refuses to start with a clear message. `--allow-degraded` to start anyway.

## 8. CLI

`expdeploy` is a Typer-based CLI.

```
expdeploy --help

Usage: expdeploy [OPTIONS] COMMAND [ARGS]...

Commands:
  run         Run an experiment or battery against a local server.
  init        Scaffold a new experiment or battery folder.
  validate    Validate a manifest, battery, or BIDS output tree.
  build       Build a study-specific OCI image.
  status      Show recent runs from the SQLite catalog.
  sync        Replay failed remote-storage writes.
  supabase    Subcommand group: migrate, test-connection, drop.
  version     Print version + bundled jsPsych version.
```

### 8.1 `expdeploy run`

```bash
# Single experiment, quick test
expdeploy run ./flanker --subject 01 --session 1 --run 1 --data-dir ./data --port 8080

# Inline battery, with counterbalance
expdeploy run --exps ./flanker,./stroop,./nback \
              --counterbalance latin_square \
              --subject 01 --session 1 --data-dir ./data

# Battery manifest, with remote sync
expdeploy run ./battery.toml --subject 01 --session 1 --data-dir ./data --remote supabase

# Variables injected into window.expdeploy.vars
expdeploy run ./stroop --subject 01 --vars '{"language":"en","reward":2.0}'
```

Flags:

| Flag | Purpose |
|---|---|
| `--subject` | BIDS-compliant subject label. Required for data writes. |
| `--session`, `--run` | BIDS session / run labels. Optional. |
| `--counterbalance` | `fixed` (default) / `latin_square` / `seeded_random` / `user_supplied`. |
| `--data-dir` | Root for `raw/`, `bids/`, `catalog.sqlite`, `state/`. Default `./data`. |
| `--remote` | Repeatable. Names of configured remote adapters. |
| `--storage-config` | Path to TOML with adapter credentials. |
| `--port` | Default 8080. Errors with suggestion if busy. |
| `--vars` | JSON injected into `window.expdeploy.vars`. |
| `--allow-degraded` | Start even if a configured remote adapter fails health check. |
| `--log-level` | `debug` / `info` / `warning` / `error`. Default `info`. |
| `--no-browser` | Don't auto-open `http://localhost:<port>`. |

### 8.2 Other subcommands

```bash
expdeploy init experiment ./my_flanker --task flanker --type fmri
expdeploy init battery ./my_battery --experiments flanker,stroop,nback

expdeploy validate ./flanker
expdeploy validate --battery ./battery.toml
expdeploy validate --bids ./data/bids

expdeploy status
expdeploy status --subject 01
expdeploy status --since 2026-05-01 --status finished
expdeploy status --json

expdeploy sync --adapter supabase
expdeploy sync --dry-run

expdeploy supabase migrate
expdeploy supabase test-connection
expdeploy supabase drop --confirm

expdeploy version
```

## 9. Container model

Layered images. Base = runtime; study = reproducible scientific artifact.

### 9.1 Base image

`Dockerfile` at repo root:

```dockerfile
# syntax=docker/dockerfile:1
FROM python:3.12-slim AS runtime

COPY --from=ghcr.io/astral-sh/uv:0.5 /uv /usr/local/bin/uv

WORKDIR /opt/expdeploy
COPY pyproject.toml uv.lock ./
COPY src/ ./src/

RUN uv sync --frozen --no-dev --extra supabase \
    && rm -rf /root/.cache

RUN useradd -m -u 1000 expdeploy
USER expdeploy

ENV PYTHONUNBUFFERED=1 \
    EXPDEPLOY_DATA_DIR=/data

EXPOSE 8080
VOLUME ["/data", "/experiments"]

ENTRYPOINT ["uv", "run", "expdeploy"]
CMD ["--help"]
```

Multi-arch build via `docker buildx`:

```bash
docker buildx build --platform linux/amd64,linux/arm64 \
  -t ghcr.io/lobennett/expdeploy:0.1.0 \
  -t ghcr.io/lobennett/expdeploy:latest \
  --push .
```

Tagged on every release via GitHub Actions. `<org>` is TBD (see open questions).

### 9.2 Day-to-day dev — bind-mount

```bash
docker run --rm -p 8080:8080 \
  -v $PWD/experiments:/experiments:ro \
  -v $PWD/data:/data \
  ghcr.io/lobennett/expdeploy:0.1.0 \
  run /experiments/flanker --subject 01 --data-dir /data
```

### 9.3 Study image — `expdeploy build`

```bash
expdeploy build ./battery.toml \
  --tag ghcr.io/lab/study-2026:2026-05-14 \
  --output study.Dockerfile

# Generated study.Dockerfile (visible, committable to repo):
FROM ghcr.io/lobennett/expdeploy:0.1.0
COPY ./flanker /experiments/flanker
COPY ./stroop /experiments/stroop
COPY ./nback /experiments/nback
COPY ./battery.toml /experiments/battery.toml
ENV EXPDEPLOY_BATTERY=/experiments/battery.toml
ENTRYPOINT ["uv", "run", "expdeploy"]
CMD ["run", "/experiments/battery.toml"]
```

`expdeploy build` actions:
1. Validate manifest + battery + every experiment's `manifest.toml`.
2. Compute content hashes (battery + each experiment); embed as OCI labels.
3. Embed `expdeploy` version, jsPsych version, build timestamp, git SHA (if in a repo) as OCI labels.
4. Run `docker build` (auto-detects `docker` vs `podman`).
5. Optionally `--push` to a registry.

Generating a visible `study.Dockerfile` (rather than building from an in-memory string) keeps the artifact gitable and transparent.

### 9.4 Apptainer / HPC

```bash
apptainer pull docker://ghcr.io/lobennett/expdeploy:0.1.0
apptainer build expdeploy.sif docker://ghcr.io/lobennett/expdeploy:0.1.0

apptainer run --bind ./experiments:/experiments --bind ./data:/data \
  expdeploy.sif run /experiments/battery.toml --subject 01
```

Documented but not in v0.1 CI matrix.

### 9.5 Reproducibility contract

Given a study image + the same bind-mounted data dir + the same subject/session/run flags, raw JSON output is bit-identical (modulo timestamps and participant responses) across hosts with the same arch. Pinned: Python, deploy package, jsPsych ESM assets, every plugin version, every Python dep (via `uv.lock`).

## 10. Testing strategy

Three tiers, mapped to confidence levels.

### 10.1 Tier 1 — Unit (`tests/unit/`)

Pure Python, no I/O beyond `tmp_path`. pytest + hypothesis.

Coverage targets:
- `manifest.py` — every Pydantic model: valid + invalid + edge cases. Errors cite offending field path.
- `battery.py` — all 4 counterbalance schemes: determinism, balance properties (Latin square verified via hypothesis), error paths.
- `loader.py` — manifest parsing, import-map construction, asset resolution.
- `storage/fs.py` — BIDS filename construction, `dataset_description.json` idempotency, `participants.tsv` concurrent append.
- `storage/sqlite.py` — schema migrations, queries, FKs, concurrent writers.

Goal: **>90% line coverage** on `src/expdeploy/`, with branch coverage targets on storage.

### 10.2 Tier 2 — Integration (`tests/integration/`)

FastAPI TestClient + real SQLite + tmp filesystem. No browser.

- `GET /` returns valid HTML with a parseable import map.
- `POST /api/data` round-trip: payload → FS write → SQLite row → events.tsv → response.
- Counterbalance + state file: two subjects, verify orders match Latin-square rows.
- Battery advancement: simulate POSTs for a 3-experiment battery; verify state transitions and final complete state.
- **Adapter contract suite**: parametrized over `FSAdapter`, `SQLiteCatalog`, fake-Supabase mock. New adapters inherit this suite for free.
- Supabase live tests behind `pytest -m supabase` marker; skipped unless `SUPABASE_URL` is set.

### 10.3 Tier 3 — End-to-end (`tests/e2e/`)

Playwright (Python bindings) against a real `expdeploy run`. Most expensive; fewest tests.

- Hello-world experiment runs to completion; data on disk matches expectations.
- Canonical flanker timeline: keyboard responses, RT recording, data POST.
- 3-experiment battery: complete each, advance, verify SQLite final state.
- ESM + import map: no console errors, imports resolve, `window.expdeploy` populated.
- Error UX: simulate Supabase outage; FS write still succeeds; browser advances normally.
- BIDS output: `_events.tsv` schema after a 3-trial run.

Headless by default; `--headed` for local debugging.

### 10.4 Infrastructure

- pytest config in `pyproject.toml`; markers for `slow`, `e2e`, `supabase`, `bids_validator`.
- `tmp_path` for filesystem isolation. No shared mutable fixtures.
- Coverage via `pytest-cov`; uploaded to Codecov.
- Test fixtures in `tests/fixtures/`: minimal valid flanker, stroop, nback experiment folders + a 3-experiment battery. Reused across tiers.
- CI matrix: Ubuntu + macOS; Python 3.11 + 3.12. Apple Silicon native runner for arm64.

### 10.5 Lint / format / type

- `ruff` for lint + format (replaces black + isort + flake8).
- `mypy --strict` on `src/expdeploy/`. Storage adapters export typed Protocols.
- `pre-commit` hooks for ruff, mypy, manifest schema validation against `examples/`.

## 11. Phasing

### v0.1.0 — "Lab-ready" (this spec)

Everything in §3–10:
- FastAPI server, ESM + import maps, vendored jsPsych v8.
- Single + battery runs (inline + manifest).
- 4 counterbalance schemes.
- FS + SQLite + Supabase storage.
- BIDS layout (fMRI + behavioral).
- OCI base image, multi-arch, `expdeploy build` for study images.
- CLI: `run`, `init`, `validate`, `build`, `status`, `sync`, `supabase`.
- mkdocs-material docs site.
- Comprehensive test suite (unit, integration, Playwright e2e).
- MIT license, semver, CONTRIBUTING.md, GitHub Actions CI.

### v0.2.0 — "Community extensibility"

- Storage adapter plugin API via `entry_points` → community can publish `expdeploy-firebase`, `expdeploy-mongo`, etc.
- First-party Firebase + MongoDB adapters (or accept community contributions).
- Counterbalance plugin API.
- Cosign-signed study images + SLSA provenance.
- Sphinx-based API reference alongside mkdocs narrative.

### v0.3.0 — "Real-time + multi-subject"

- Websockets-driven live researcher dashboard (run progress, RTs, accuracy).
- Multi-subject parallel sessions on one server.
- Subject auth (simple login + magic-link flow).
- Apptainer-tested HPC matrix in CI.

### v1.0.0 — API stability

After at least one external lab has adopted the package for a published study without breaking changes for two minor releases.

## 12. Decisions & remaining risks

### 12.1 Resolved (locked at spec approval, 2026-05-14)

1. **GHCR org name** — `ghcr.io/lobennett/expdeploy`. Images published under the user's personal GitHub namespace.
2. **Repo location on disk** — `/Users/lobennett/grants/r01_rdoc/projects/expdeploy/` (sibling to `expfactory-deploy/`).
3. **License** — MIT.
4. **Python version range** — 3.11+.
5. **Manifest schema (§4.2)** — accepted as written, including `import_map_extras` naming and `[bids.columns.*]` shape.
6. **Port handling (§7.5)** — no auto-retry; CLI errors with a suggested next port. Explicit departure from current package.

### 12.2 Remaining risks / non-blocking items

1. **jsPsych version pinning** — vendor a specific patch version (e.g., `8.2.3`); allow per-experiment manifests to override `[jspsych] version` only if the override is also vendored. Multiple versions can coexist in subdirs of `jspsych_assets/`.
2. **Behavioral BIDS spec stability** — BEP for behavioral data is still evolving. Pin to BIDS 1.9; document the version in `dataset_description.json`; add `expdeploy migrate-bids` only if a future change requires it.
3. **`expdeploy build` requires Docker/Podman on the host** — one place "Node-free" isn't quite "dep-free." Acceptable: building a study image is a one-time deployment activity.
4. **PII handling** — v0.1 treats subject IDs as opaque. Docs will warn against putting MRNs / names there. No HIPAA-level controls.
5. **"Extending jsPsych" scope in v0.1** — supports local file imports + `import_map_extras` aliases. Custom jsPsych plugins are just ES modules; they Just Work. **Not** in v0.1: a blessed-plugin registry, npm-install of plugins into the deploy package.
6. **Single-subject-per-server assumption** — v0.1 matches the current model. Multi-subject is v0.3 work.

## 13. References

- jsPsych v8 docs (canonical setup tutorials): https://www.jspsych.org/
- BIDS spec 1.9: https://bids-specification.readthedocs.io/
- Vanessa Sochat's container-as-science writing (informs the layered image model).
- Existing `expfactory_deploy_local` (this repo's current package) — the homage target.
- Prior spec in this repo: `docs/superpowers/specs/2026-04-23-fork-sync-contributing-and-typo-fix-design.md`.
