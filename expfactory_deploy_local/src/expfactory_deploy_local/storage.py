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
