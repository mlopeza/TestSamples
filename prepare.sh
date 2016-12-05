#!/bin/bash -f
DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
ENV_DIR_NAME=".byenv"
# Deactivate current environment if we are in it
deactivate &> /dev/null || true
rm -rf $ENV_DIR_NAME
if [[ ! -z "$PYPATH" ]]; then
	PYPATH=$(type -P "$PYPATH")
else
	PYPATH=$(type -P python2.7)
fi
if [[ -z "$PYPATH" ]];then
	echo "Python2.7 wasn't found. Please specify the PATH with export PY_PATH"
	exit 1
fi
virtualenv --no-site-packages -p "$PYPATH" $ENV_DIR_NAME
source "$ENV_DIR_NAME/bin/activate"
pip install -r "$DIR/requirements.txt"
echo "VirtualEnv is ready. Please execute:"
echo "source \"$ENV_DIR_NAME/bin/activate\""
