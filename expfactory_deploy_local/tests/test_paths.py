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
