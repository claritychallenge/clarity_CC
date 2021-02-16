# SceneGenerator

SceneGenerator is used to produce input signals for the hearing aid model (GHA).
The main function is generate_HA_inputs.py. The generator is driven by json files
to compile the training and test data from raw inputs. This includes the core
signal processing steps, including convolution with binaural room impulse responses.

## Documentation

To build documentation using pdoc:

```bash
cd doc
./build.sh
```

(Note, pdoc3 and pdoc are the same)

To view

```bash
cd doc/build/SceneGenerator
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
