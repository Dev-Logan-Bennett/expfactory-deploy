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
