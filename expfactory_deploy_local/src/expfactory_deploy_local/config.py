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
