# expfactory_deploy_local

A minimal local deployer that serves jsPsych experiments one at a time in the browser and saves a raw JSON per experiment (always) plus a BIDS events CSV (only for fMRI experiments).

---

## Install

Requires Python ≥ 3.11.

```bash
uv venv --python 3.12
uv pip install -e /path/to/expfactory-deploy/expfactory_deploy_local
```

This installs the console script `expfactory_deploy_local`.

---

## CLI reference

| Short | Long | Description |
|-------|------|-------------|
| `-e` | `--exps` | Comma-delimited list of experiment paths. Mutually exclusive with `--config`. |
| `-c` | `--config` | Path to a single experiment, or to a config file listing one experiment path per line. Mutually exclusive with `--exps`. |
| `-gi` | `--group_index` | Inject a `group_index` variable into the experiment context. |
| `-sub` | `--subject_id` | Subject ID. |
| `-ses` | `--session_num` | Session number. |
| `-run` | `--run_num` | Run number. |
| `-raw` | `--raw_dir` | Output directory for raw JSON. |
| `-bids` | `--bids_dir` | Output directory for BIDS events CSV. |

---

## Examples

Single experiment with full metadata:

```bash
expfactory_deploy_local -e path/to/exp_rdoc__fmri \
  -raw ./.output/raw -bids ./.output/bids -sub s1 -ses 1 -run 1
```

Config file (one experiment path per line):

```bash
expfactory_deploy_local -c battery.txt -raw ./.output/raw -bids ./.output/bids -sub s1 -ses 1 -run 1
```

The server scans ports starting at 8080 and prints the URL to open in the browser.

---

## Output layout

### Filename prefix

The prefix is built in order from whichever of subject / session / run are provided:

```
sub-<id>_ses-<ses>_run-<run>_
```

Only the parts that are supplied appear (e.g., if `-run` is omitted the prefix ends at `ses-<ses>_`).

### Raw JSON (always written)

```
<raw_dir>/sub-<id>/ses-<ses>/<prefix>task-<expID>_dateTime-<unix>.json
```

Directory nesting under `raw_dir`:
- `sub-<id>/` when a subject is given.
- `ses-<ses>/` inside that when a session is given.
- The run number **never** creates a directory level.

With no `-raw`, the file is written to the current working directory using just the filename (no subdirectory nesting).

### BIDS events CSV (conditional)

Written **only** when `-bids` is set **and** the served experiment's folder name contains `__fmri`.

```
<bids_dir>/sub-<id>/ses-<ses>/func/<prefix>task-<expID>.csv
```

Nesting under `bids_dir`:
- `sub-<id>/ses-<ses>/func/` when both subject and session are given.
- `sub-<id>/func/` when a subject is given but no session.

### Concrete example

For `-sub s1 -ses 1 -run 1 -e .../stroop_rdoc__fmri`:

| Output type | Path |
|-------------|------|
| Raw JSON | `.output/raw/sub-s1/ses-1/sub-s1_ses-1_run-1_task-stroop_rdoc__fmri_dateTime-<unix>.json` |
| BIDS events CSV | `.output/bids/sub-s1/ses-1/func/sub-s1_ses-1_run-1_task-stroop_rdoc__fmri.csv` |

---

## Used by

The `rdoc-fmri-experiments` repo drives this tool for the RDoC fMRI battery. See that repo for the full launch and counterbalancing workflow.
