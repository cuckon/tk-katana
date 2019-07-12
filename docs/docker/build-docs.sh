#!/bin/bash

set -eu -o pipefail

find * -name '*.py' ! -path 'docs/*' -printf "/Repository/%h\n" | xargs mkdir -vp
find /Repository/* -type d -exec touch {}/__init__.py \;
find * -name '*.py' ! -path 'docs/*' -exec cp -fv {} /Repository/{} \;
cp -rv docs /Repository

cd /Repository
mkdir -vp docs/${API_RELATIVE_DIR}
sphinx-apidoc -o docs/${API_RELATIVE_DIR} --separate --tocfile index .

# -- Generate API docs first with dash so it matches existing folders/files --
# Replace - with _ so sphinx build can import modules
sed -i '/automodule:: / s/-/_/g' docs/${API_RELATIVE_DIR}/*.rst

# Rename folder first before renaming .py files
for DASH_FOLDER in $(find -type d -name '*-*')
do
    mv -v "${DASH_FOLDER}" "${DASH_FOLDER//-/_}"
done
for DASH_PY_FILE in $(find -name '*-*.py')
do
    cp -v "${DASH_PY_FILE}" "${DASH_PY_FILE//-/_}"
done


# Clean, generate output and set permissions to match original owner
rm -rf /output/*
sphinx-build docs /output
chown -R $(stat -c '%u' /output):$(stat -c '%g' /output) /output/*
