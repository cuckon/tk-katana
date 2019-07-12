#!/bin/bash

#
# usage: build-docs.sh [OUTPUT_DIR]
#
# Create sphinx documentations when run from repository root.
#
# By default, the docs will be output to docs/_build relative to the
# repository's root folder. Pass in a custom folder

set -eu -o pipefail

PYTHON_ONLY_DIR=$(mktemp -d)
OUTPUT_DIR="${1:-docs/_build}"

# Copy only .py files, ensure leading folders have a __init__.py
find * -name '*.py' ! -path 'docs/*' -printf "${PYTHON_ONLY_DIR}/%h\n" | xargs mkdir -vp
find ${PYTHON_ONLY_DIR}/* -type d -exec touch {}/__init__.py \;
find * -name '*.py' ! -path 'docs/*' -exec cp -fv {} ${PYTHON_ONLY_DIR}/{} \;
cp -rv docs ${PYTHON_ONLY_DIR}

cd ${PYTHON_ONLY_DIR}
mkdir -vp docs/${API_RELATIVE_DIR}
sphinx-apidoc -o docs/${API_RELATIVE_DIR} --separate --no-toc .

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
rm -rf ${OUTPUT_DIR}/*
mkdir -vp ${OUTPUT_DIR}
sphinx-build docs ${OUTPUT_DIR}
chown -R $(stat -c '%u' ${OUTPUT_DIR}):$(stat -c '%g' ${OUTPUT_DIR}) ${OUTPUT_DIR}/*
