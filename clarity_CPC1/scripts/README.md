# Scripts

Top level scripts for implementing baseline enhancement and enhancement evaluation pathways.

```bash
./run_all.sh 
```

`run_all.sh` is broken into the following four stages:

1. check_data.sh - check that data needed is correctly installed.
2. predict.sh - run the hearing loss model and then the MBSTOI speech intelligibility model to obtain an objective score.

`predict.sh` runs in two steps. It first passes all signals through the MSBG hearing loss model (this stage is currently very slow). It then performs an MBSTOI calculation comparing the hearing loss model output and the original signal. The second step will produce results file `mbstoi.train.csv` in the scripts directory.

The file `mbstoi.train.baseline.csv` contains `mbstoi.train_indep.baseline.csv` contain the complete pre-computed MBSTOI scores for track1 and track2, respectively.