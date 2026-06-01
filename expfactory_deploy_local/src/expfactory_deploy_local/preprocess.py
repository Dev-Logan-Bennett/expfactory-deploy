import json

import pandas as pd


def raw_to_df(raw_data) -> tuple[pd.DataFrame, str]:
    """Convert raw data to a pandas DataFrame.

    Args:
        raw_data: Either a file path (str) or raw data (bytes).

    Returns:
        tuple[pd.DataFrame, str]: A tuple containing the pandas
        DataFrame containing the trial data and the experiment ID.
    """
    if isinstance(raw_data, str):
        # It's a file path
        with open(raw_data, "r") as f:
            data = json.load(f)
    elif isinstance(raw_data, bytes):
        # It's bytes data
        data = json.loads(raw_data.decode("utf-8"))
    else:
        # Invalid input type
        raise TypeError(f"Expected str or bytes, got {type(raw_data)}")

    # Get the trial data
    trialdata = json.loads(data["trialdata"])
    parsed_trialdata = pd.DataFrame(trialdata)

    # Try to get experiment ID from different potential locations
    exp_id = None

    # First check if it's directly in the data dict (from our template update)
    if "exp_id" in data:
        exp_id = data["exp_id"]
    # Then check if it's in the trial data
    elif parsed_trialdata.get("exp_id") is not None:
        exp_id = parsed_trialdata["exp_id"]

    # Handle different data formats
    if isinstance(exp_id, pd.Series):
        exp_id = exp_id.dropna().iloc[0]
    elif isinstance(exp_id, str):
        pass  # Already a string
    elif isinstance(exp_id, list) and len(exp_id) > 0:
        exp_id = exp_id[0]
    else:
        # Fallback if exp_id can't be determined
        exp_id = "unknown"
        print("Warning: Could not determine exp_id, using 'unknown'")

    return pd.DataFrame(trialdata), exp_id
