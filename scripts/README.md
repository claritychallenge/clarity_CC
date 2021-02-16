# Scripts

Top level scripts for implementing baseline enhancement and enhancement evaluation pathways.

```bash
./run_all.sh 
```

`run_all.sh` is broken into the following four stages:

1. check_data.sh - check that data needed for generation stage is correctly installed.
2. generate.sh - generate hearing aid inputs for a given scene.
3. enhance.sh - run the hearing aid and hearing aid postprocessing.
4. predict.sh - run the hearing loss model and then the speech intelligibility model to obtain an objective score.
