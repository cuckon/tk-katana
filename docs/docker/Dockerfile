FROM centos:7

# From repository root, run:
# docker build --rm -t local/tk-katana-docs docs/docker
# docker run -it --rm -v $(pwd):/repo -v $(pwd)/docs/_build:/output local/tk-katana-docs

RUN mkdir -vp /output /Repository \
    && yum install -y pyqt4 \
    & curl -L https://bootstrap.pypa.io/get-pip.py | python - \
    && pip install sphinx-rtd-theme \
    & curl -L 'https://raw.githubusercontent.com/wwfxuk/tk-doc-generator/v1.0.0%2Bwwfx.0.4.1/scripts/get-tk-core-packages.sh' \
    | bash /dev/stdin /usr/local/python \
    & wait

ENV PYTHONPATH=${PYTHONPATH}:/usr/local/python
ENV API_RELATIVE_DIR=api
WORKDIR /repo

VOLUME /repo
VOLUME /output

COPY build-docs.sh /usr/local/bin/
CMD build-docs.sh