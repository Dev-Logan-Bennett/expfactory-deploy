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
