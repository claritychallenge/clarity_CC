DIRECTORY=$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )
export CLARITY_ROOT=$DIRECTORY/..
export CLARITY_DATA="$CLARITY_ROOT"/data/clarity_data
export PYTHON_BIN="$CLARITY_ROOT"/env/bin/python

export LD_LIBRARY_PATH="$CLARITY_ROOT"/tools/openMHA/lib:$LD_LIBRARY_PATH
export PATH="$CLARITY_ROOT"/tools/openMHA/bin:$PATH
