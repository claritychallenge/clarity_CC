"""Predict final intelligibility scores from a set of MBSTOI scores.

Usage:
  python3 predict_intel.py <MBSTOI_CSV_FILE> <CPC1_TRAIN_JSON_FILE>
  <OUTPUT_CSV_FILE>

- <MBSTOI_CSV_FILE> - name of file containing the raw MBSTOI scores
- <CPC1_TRAIN_JSON_FILE> - the JSON file containing the CPC1 metadata
- <OUTPUT_CSV_FILE> - name of a csv file to which prediction will be written

Final stage of the baseline pipeline which maps MBSTOI scores 
(between 0 and 1) onto sentence intelligibility scores between (0 and 100).
The mapping is performed by first estimating the parameters of a sigmoid function
that minimise the RMS estimation error.

The script is provided as an example of the way in which the training
data should be treated when using it for development. The training data
is partitioned into training data and development evaluation data. i.e.
the sigmoid mapping is learnt from the training partition and applied to
the evaluation partition. A K-fold cross-validation set up is employed so
that, via repetition, a score can be computed for all responses in the 
training data set. 

Care needs to be taken when constructing the folds. In particular, the
training data has multiple responses originating from the same 'scene' -
either processed with a different hearing aid or processed for a different
listener. However, the final CPC1  evaluation dataset (released later) will contain a new set of previously unseen scenes. It is therefore important 
to evaluate during development in a scene-independent fashion. In this 
example script, scene-independence is maintained by splitting data 
on the 'scene' label field so that no signal originating from the same 
scene appears in more than one fold. 
"""


import argparse

import numpy as np
import pandas as pd
from scipy.optimize import curve_fit
from tqdm import tqdm


N_FOLDS = 5  # Number of folds to use in the n-fold cross validation


class Model:
    """Class to represent the mapping from mbstoi parameters to intelligibility scores.

    The mapping uses a simple sigmoid function scaled between 0 and 100.
    The mapping parameters need to fit first using mbstoi, intelligibility score pairs, using fit().
    Once the fit has been made predictions can be made by calling predict()
    """

    params = None  # The model params

    def _sigmoid_mapping(self, x, x0, k):
        """
        Logistic function
            x0 - x value of the sigmoid's midpoint
            k - the logistic growth rate or steepness of the curve
        """
        L = 100  # correctness can't be over 100
        return L / (1 + np.exp(-k * (x - x0)))

    def fit(self, mbstoi, intel):
        """Fit a mapping betweeen mbstoi scores and intelligibility scores."""
        initial_guess = [0.5, 1.0]  # Initial guess for parameter values
        self.params, pcov = curve_fit(self._sigmoid_mapping, mbstoi, intel, initial_guess)

    def predict(self, x):
        """Predict intelligilbity scores from mbstoi scores."""
        # Note, fit() must be called before predictions can be made
        assert self.params is not None
        return self._sigmoid_mapping(x, self.params[0], self.params[1])


def main(mbstoi_file_csv, intel_file_json, prediction_file_csv):

    # Load the mbstoi data and the intelligibility data
    df_mbstoi = pd.read_csv(mbstoi_file_csv)
    df_intel = pd.read_json(intel_file_json)

    # Merge into a common dataframe
    data = pd.merge(
        df_mbstoi,
        df_intel[["scene", "listener", "system", "correctness"]],
        how="left",
        on=["scene", "listener", "system"],
    )
    data["predicted"] = np.nan  # Add column to store intel predictions

    # The model that will represent the MBSTOI to intel mapping
    # This model is going to be fit using the data
    model = Model()

    # Make a unique list of all the scenes appearing in the data
    scenes = data.scene.unique()

    for fold in tqdm(range(N_FOLDS)):
        # Split the train scenes and the test scenes
        test_scenes = set(scenes[fold : len(scenes) : N_FOLDS])
        train_scenes = set(scenes) - set(test_scenes)

        # Fit the logistic function to map from mbstoi to intelligibility
        # Using only the data corresponding to the train set scenes
        train_data = data[data.scene.isin(train_scenes)]
        model.fit(train_data["mbstoi"], train_data["correctness"])

        # Make the intelligibility predictions with the fitted model
        # Applying them only to the test set scenes
        data.loc[data.scene.isin(test_scenes), ["predicted"]] = model.predict(
            data[data.scene.isin(test_scenes)]["mbstoi"]
        )

    # There should be no scenes without a prediction
    assert data["predicted"].isna().sum() == 0

    # Save data as csv
    data[["scene", "listener", "system", "predicted"]].to_csv(prediction_file_csv, index=False)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("mbstoi_csv_file", help="csv file containing MBSTOI predictions")
    parser.add_argument(
        "cpc1_train_json_file", help="JSON file containing the CPC1 training metadata"
    )
    parser.add_argument(
        "out_csv_file", help="output csv file containing the intelligibility predictions"
    )
    args = parser.parse_args()

    main(args.mbstoi_csv_file, args.cpc1_train_json_file, args.out_csv_file)
