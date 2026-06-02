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
