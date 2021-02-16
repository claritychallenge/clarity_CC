# GHA

Python translation of the openMHA MATLAB-based gain table calculation for a 
Camfit prescription and two channels (front and rear). The prescription is based on 
an openMHA implementation, where the original files are named gainrule_camfit_compr.m 
and gainrule_camfit_linear.m. These are based on the following:

Moore, B. C. J., Alcántara, J. I., Stone, M. A., & Glasberg, B. R. (1999). Use 
of a loudness model for hearing aid fitting: II. Hearing aids with multi-channel 
compression. British Journal of Audiology, 33(3), 157-170.

The MATLAB GUI and associated prescription and "noisegate" calculation files are 
replaced by a Python wrapper, which pulls in a template configuration file and
replaces the necessary files before sending to openMHA. openMHA should be installed
separately. See tools/get_openmha.sh.

## Installation

```bash
# Download
git clone --recurse-submodules https://github.com/claritychallenge/GHA
cd GHA
git checkout development
# Set up python virtual environment
python -m venv env
source env/bin/activate
pip install --upgrade pip
pip install -r requirements-dev.txt
```

## To use

Use run_demo.py to choose listeners and scenes to process and run

```bash
python -m run_demo.py
```

## Tests

To run tests:

```bash
coverage run -m py.test tests
coverage report -m
```

## Generating documentation

```bash
cd doc
./build.sh
```

Then to view

```bash
cd doc/build/GHA
python -m http.server 3000
# visit http://0.0.0.0:3000
```

## Generating callgraph

From the GHA directory, generate a callgraph. You may need to install graphviz.

```bash
pip install pycallgraph
pycallgraph -i "GHA*" --max-depth=7 graphviz -- control_openmha.py
```

The result will appear in the file `pycallgraph.png`
