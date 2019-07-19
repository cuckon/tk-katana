#!/bin/bash

#
# usage: build-docs.sh [OUTPUT_DIR]
#
# Create sphinx documentations when run from repository root.
#
# By default, the docs will be output to docs/_build relative to the
# repository's root folder. Pass in a custom folder
#

set -eu +f -o pipefail
shopt -s dotglob

PYTHON_ONLY_DIR=$(mktemp -d)
DOCS_DIR="${DOCS_DIR:-docs}"
API_RST_DIR="${PYTHON_ONLY_DIR}/${DOCS_DIR}/${API_RELATIVE_DIR:-api}"
OUTPUT_DIR=$(readlink --canonicalize-missing "${1:-docs/_build}")

STAT_FROM_DIR="${OUTPUT_DIR}"
[ -d OUTPUT_DIR ] || STAT_FROM_DIR="${DOCS_DIR}"
OUTPUT_OWN=$(stat -c '%u' "${STAT_FROM_DIR}"):$(stat -c '%g' "${STAT_FROM_DIR}")
OUTPUT_PERM=$(stat -c '%a' "${STAT_FROM_DIR}")

echo "
###
### ==== Running '${0}' from '$(pwd)' ====
###         Using docs (conf.py) from: '$(readlink --canonicalize ${DOCS_DIR})'
###  Setting up Python source code in: '${PYTHON_ONLY_DIR}'
### Temporary API (RST) sphinx-apidoc: '${API_RST_DIR}'
###            Final HTML docs output: '${OUTPUT_DIR}'
###
"

# Clean, create output folder and set permissions to match original docs owner
rm -rf "${OUTPUT_DIR}"/*
for NEW_DIR in $(mkdir -vp "${OUTPUT_DIR}" | sed 's/.*created directory .//; s/.$//')
do
    chown "${OUTPUT_OWN}" "${NEW_DIR}" &> /dev/null || echo '
Unable to set owner for "'${NEW_DIR}'" to be same as "'${STAT_FROM_DIR}'".
Please try again as root, e.g.

sudo chown "'${OUTPUT_OWN}'" "'${NEW_DIR}'"/*

'
done

# Copy only .py files, ensure leading folders have a __init__.py
find * -name '*.py' ! -path "${DOCS_DIR}/*" -printf "${PYTHON_ONLY_DIR}/%h\n" | xargs mkdir -p
find "${PYTHON_ONLY_DIR}"/* -type d -exec touch {}/__init__.py \; -printf 'Created %p/__init__.py\n'
find * -name '*.py' ! -path "${DOCS_DIR}/*" -exec cp -fv {} "${PYTHON_ONLY_DIR}"/{} \;
cp -rv '.travis.yml' "${DOCS_DIR}" "${PYTHON_ONLY_DIR}"


# -- Generate API docs first with dash so it matches existing folders/files --
cd "${PYTHON_ONLY_DIR}"
mkdir -p "${API_RST_DIR}"
sphinx-apidoc -o "${API_RST_DIR}" --separate --no-toc .

# Replace - with _ so sphinx build can import modules
sed -i '/automodule:: / s/-/_/g' "${API_RST_DIR}"/*.rst

# Rename folder first before renaming .py files
for DASH_FOLDER in $(find -type d -name '*-*')
do
    mv -v "${DASH_FOLDER}" "${DASH_FOLDER//-/_}"
done
for DASH_PY_FILE in $(find -name '*-*.py')
do
    cp -v "${DASH_PY_FILE}" "${DASH_PY_FILE//-/_}"
done


# Generate HTML output and set permissions to match original docs owner
sphinx-build "${DOCS_DIR}" "${OUTPUT_DIR}"
chown --recursive "${OUTPUT_OWN}" "${OUTPUT_DIR}"/* &> /dev/null || echo '
Unable to set owner for generated HTML to be same as "'${STAT_FROM_DIR}'".
Please try again as root, e.g.

    sudo chown --recursive "'${OUTPUT_OWN}'" "'${OUTPUT_DIR}'"/*

'