Generating documentations
=========================

Whenever you create a new PR for this repository, documentations will be
built as part of CI.

But during development, you may want to generate the (code) documentations
yourself locally.

.. warning:: Right now this guide only supports Linux.

.. _docs-requirements:

Requirements
------------

Either just `Docker`_ or:

- Python, and
- A Qt binding for Python (e.g. PyQt4), and
- pip, ``PyYAML`` and ``sphinx-rtd-theme`` pip packages

Generating
----------

Locally
^^^^^^^

Docker
''''''

If you have `Docker`_ installed, simply run from the repository's root folder:

.. code-block:: bash

    docker run --rm -v $(pwd):/repo $(docker build --quiet --rm docs/docker)

This builds the `Docker`_ image required to build the documentations and
then generates the documentations in a container, mounting the current folder
(repository root) as ``/repo``.

VirtualEnv or installed dependencies
''''''''''''''''''''''''''''''''''''

If you have the dependencies installed from the above :ref:`docs-requirements`
section, simply run from the repository's root folder:

.. code-block:: bash

    docs/docker/build-docs.sh


GitHub
^^^^^^

Again, documentations will be built as part of CI for sanity check but not
viewable by default.

.. warning::
    The following is really hack-y and not recommended as it will
    override the default documentations viewed by everyone through
    https://wwfxuk.github.io/tk-katana/

If you want to brute-force override the default documentations, you can
temporarily for the PR, change the branch which the documentations will only
be deployed for, i.e.:

.. literalinclude:: /_static/example_travis_docs_hack.yml
    :diff: /_static/example_travis.yml

Just remember to change it back to ``master`` before merging the PR

.. _Docker: https://docs.docker.com/