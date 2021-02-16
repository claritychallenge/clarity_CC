# The 1st Clarity Enhancement Challenge

Clarity challenge baseline code for the first enhancement challenge (CEC1).

For more information about the Clarity Challenge please visit http://claritychallenge.org/the-team

## Installation instructions

The Clarity code is made available as a GitHub repository. To clone the repository, 

```bash
git clone https://github.com/claritychallenge/clarity_CEC1.git
cd clarity_CEC1
```

Then see [INSTALL.md](INSTALL.md) for full installation and usage instructions.

## Licensing terms

All Clarity code is made available under the terms of the Creative Commons Attribution-ShareAlike 4.0 International licence with the exceptions listed below.

If you use this code in publications, please cite it as follows:

```
Details to appear. 
```

License terms for the data are included in the separately-downloaded data packages. They are summarised below.

- The target utterances are part of the Clarity speech database, and are licensed under the terms of the Clarity speech database license 1.00. This is based on Creative Commons Attribution-ShareAlike 4.0 but with some additional constraints concerning the public replay of audio samples. 

If you use this data in publications, please cite it as follows:

```
Details to appear. 
```

- The speech interferer data comes from the SLR83 database  (https://www.openslr.org/83/) made available under the terms of the  Attribution-ShareAlike 4.0 International licence by Google, Inc. 

If you use this data in publications, please cite it as follows:

```
  @inproceedings{demirsahin-etal-2020-open,
    title = {{Open-source Multi-speaker Corpora of the English Accents in the British Isles}},
    author = {Demirsahin, Isin and Kjartansson, Oddur and Gutkin, Alexander and Rivera, Clara},
    booktitle = {Proceedings of The 12th Language Resources and Evaluation Conference (LREC)},
    month = may,
    year = {2020},
    pages = {6532--6541},
    address = {Marseille, France},
    publisher = {European Language Resources Association (ELRA)},
    url = {https://www.aclweb.org/anthology/2020.lrec-1.804},
    ISBN = {979-10-95546-34-4},
  }
```

- The noise interferer data is a collection of samples, mainly from Freesound under Creative Commons No Copyright or Creative Commons Attribution licences. For the purposes of attribution, the source for each sample can be found in metadata files `masker_nonspeech_list.dev.json` and `masker_nonspeech_list.train.json`
  
- The scene generation uses HRIRs from the OlHeadHRTF database, which is released under the Attribution-Noncommercial ShareAlike 4.0 International licence with additional permissions as specified when agreeing to download the data.
