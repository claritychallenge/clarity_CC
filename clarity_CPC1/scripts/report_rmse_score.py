"""
Score a set of intelligibility predictions

Usage:
  python3 compute_rmse_score.py <CPC1_METADATA_JSON_FILE> <PREDICTION_CSV_FILE>

e.g.
  python3 compute_rmse_score.py "$CLARITY_DATA"/metadata/CPC1.train.json predictions.csv

Requires the predictions.csv file containing the predicted intelligibility
for each signal. This should have the following format.

  scene,listener,system,predicted
  S09637,L0240,E013,81.72
  S08636,L0218,E013,90.99
  S08575,L0236,E013,81.43
etc
"""

import argparse

import numpy as np
import pandas as pd


def rmse_score(x, y):
    return np.sqrt(np.mean((x - y) ** 2))


def main(intel_file_json, prediction_file_csv):
    """Compute and report the RMS error comparing true intelligibilities
    with the predicted intelligibilities

    The true intelligibilities are stored in the CPC1 JSON metadata file
    that is supplied with the challenge. The predicted scores should be
    stored in a csv file with a format as follows

    scene,listener,system,predicted
    S09637,L0240,E013,81.72
    S08636,L0218,E013,90.99
    S08575,L0236,E013,81.43

    For example, as produced by the baseline system script predict_intel.py
    ...

    Args:
        intel_file_json (str): Name of the CPC JSON metadata storing true scores
        prediction_file_csv (str): Name of the csv file scoring predicted scores
    """

    # Load the predictions and the actual intelligibility data
    df_predictions = pd.read_csv(prediction_file_csv)
    df_intel = pd.read_json(intel_file_json)

    # Merge into a common dataframe
    data = pd.merge(
        df_predictions,
        df_intel[["scene", "listener", "system", "correctness"]],
        how="left",
        on=["scene", "listener", "system"],
    )

    # Compute the score comparing predictions with the actual
    # word correctnesses recorded by the listners
    error = rmse_score(data["predicted"], data["correctness"])

    print(f"RMS prediction error: {error:5.2f}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "cpc1_train_json_file", help="JSON file containing the CPC1 training metadata"
    )
    parser.add_argument(
        "predictions_csv_file", help="csv file containing the predicted intelligibilities"
    )
    args = parser.parse_args()

    main(args.cpc1_train_json_file, args.predictions_csv_file)
