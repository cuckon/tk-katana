FROM centos:7

#
# From repository root, run:
#
#   (Run once FIRST) Create "local/tk-katana-docs" image to build docs with:
#
#       docker build --rm -t local/tk-katana-docs docs/docker
#
#   (Run when you update docs) Build docs into "docs/_build", deletes existing:
#
#       docker run --rm \
#           -v $(pwd):/repo \
#           -v $(pwd)/docs/_build:/output \
#           local/tk-katana-docs
#

WORKDIR /usr/local/bin/
COPY build-docs.sh .

RUN chmod a+x build-docs.sh \
    && yum install -y pyqt4 \
    & curl -L https://bootstrap.pypa.io/get-pip.py | python - \
    && pip install sphinx-rtd-theme \
    & curl -LO 'https://raw.githubusercontent.com/wwfxuk/tk-doc-generator/v1.0.0%2Bwwfx.0.4.1/scripts/get-tk-core-packages.sh' \
    && source get-tk-core-packages.sh /usr/local/python \
    & wait

ENV PYTHONPATH=${PYTHONPATH}:/usr/local/python
ENV API_RELATIVE_DIR=api

WORKDIR /repo
VOLUME /repo

CMD build-docs.sh