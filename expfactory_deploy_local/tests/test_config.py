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
