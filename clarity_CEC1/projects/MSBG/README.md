# Python translation of MSBG hearing loss model

This hearing loss simulator is a Python translation of a MATLAB encoded model developed
by members of Auditory Perception Group, University of Cambridge, ca. 1991-2013.
Input sound files must have a 44.1 kHz sampling rate. 

## Installation

```bash
# Download submodules
git submodule update --init --recursive
# Setup python virtual environment
python -m venv env
source env/bin/activate
pip install --upgrade pip
pip install -r requirements-dev.txt
# Build matlab_mldivide submodule
cd packages/matlab_mldivide
python setup.py install
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
cd doc/build/MSBG
python -m http.server 3000
# Now visit http://0.0.0.0:3000
```

## Tests

To run tests:

```bash
coverage run -m py.test tests
coverage report -m
```

Note, will run test coverage. See pytest.ini for configuration.
