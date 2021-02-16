# speechintmodel

 This is a translation of the Modified Binaural Short-Time
 Objective Intelligibility (MBSTOI) measure as described in:
 
 A. H. Andersen, J. M. de Haan, Z.-H. Tan, and J. Jensen, 'Refinement 
 and validation of the binaural short time objective intelligibility 
 measure for spatially diverse conditions,' Speech Communication, 
 vol. 102, pp. 1-13, Sep. 2018. 
 
 Asger Heidemann Andersen, 10-12-2018

MBSTOI:

- mbstoi.py and ec.py are a translation of mbstoi.m into Python; ec.py performs the equalisation-cancellation stage
- stft.py produces the short-time discrete Fourier transforms
- thirdoct.py returns the one-third octave band matrix and its center frequencies
- remove_silent_frames.py removes silent frames of x and y based on x

Use caution:
(1) MBSTOI relies on correct time-alignment of the input clean and 
processed signals. This may require modifications to the code in
scripts/calculate_SI.py for your system. Check that signals are 
aligned for your implementation/system.
(2) MBSTOI is not sensitive to the level of the processed signal. 
Note that MSBG simulates the raising of auditory thresholds by means 
of attenuation. You must check whether your hearing aid processor 
is producing signals that would be audible for a listener corresponding 
to the relevant set of audiograms. 

## Installation

```bash
# Download submodules
git submodule update --init --recursive
# Setup python virtual environment
python -m venv env
source env/bin/activate
pip install --upgrade pip
pip install -r requirements-dev.txt
```

## Documentation

To build documentation using pdoc:

```bash
cd doc
./build.sh
```

(Note, pdoc3 and pdoc are the same)

To view

```bash
cd doc/build/MBSTOI
python -m http.server 3000
# Now visit http://0.0.0.0:3000
```

## Tests

To run tests:

```bash
coverage run -m py.test tests
coverage report -m
```
