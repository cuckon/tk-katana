Change Log/History
==================

See also the `GitHub Releases page`_

v0.1.0+wwfx.1.8.0 (19 Jul 2019)
-------------------------------
- Removed unused hooks
- Using docker to build docs
- Fixed broken docstrings

v0.1.0+wwfx.1.7.0 (11 Jul 2019)
-------------------------------
- Added ``tk-framework-shotgunutils`` v5.x.x
- Switched to standard 256x256 icon
- Moved ``QtPyImporter`` into ``utils``
- Minimal working support for older Katana using PyQt4

v0.1.0+wwfx.1.6.0 (26 Jun 2019)
-------------------------------
- Added render publishing
- Moved icons to 'icons' folder

v0.1.0+wwfx.1.5.0 (11 Jun 2019)
-------------------------------
- Moved documentation to GitHub Pages from GitHub Wiki
- Added CI for making docs

v0.1.0+wwfx.1.4.0 (5 Jun 2019)
------------------------------
- Qt patches
- Logging updates
- Resource loading
- Publishing and loading updates

v0.1.0+wwfx.1.3.1 (29 May 2019)
-------------------------------
- Wiki/Documentation updated
- Updated ``configs`` for specific app/engine/framework requirements.

v0.1.0+wwfx.1.3.0 (29 May 2019)
-------------------------------
Initial working GUI for Katana 3.1 (PyQt5)

Still rough and switching context is not working but hey, we have GUI!

- Used `Qt.py 1.1.0`_ to achieve
  a initial working Qt binding for Katana 3.1 (PyQt5)
- Updated ``configs`` folder for example ``tk-multi-*``
- Removed test panels, deferred Qt imports in ``tk_katana``

v0.1.0+wwfx.1.2.3 (12 Apr 2019)
-------------------------------

- Cheeky icons for "Jump to" menu actions
- Removed ``os.system``, using unified open with ``QDesktopService.openUrl()``
- Fixed pre-mature call to generate Shotgun menu

v0.1.0+wwfx.1.2.2 (11 Apr 2019)
-------------------------------

- Logging in ``engine.py``
- Plugin-logger in ``ShotgunAssetPlugin``
- Remove print/refactor to python 3 print
- Remove unused, e.g. ``_non_pane_menu_callback_wrapper``

v0.1.0+wwfx.1.2.1 (10 Apr 2019)
-------------------------------

- Fixed and updated ``startup/bootstrap.py`` from ``tk-natron`` code.
- Initial move to "SGTK_*" environment variables.

v0.1.0+wwfx.1.2.0 (04 Apr 2019)
-------------------------------

- Re-created package using Cookiecutter for Python.

v0.1.0+wwfx.1.1.0 (03 Apr 2019)
-------------------------------

- Merged in ``demon7x/tk-katana`` fork's, master branch's `adb98c1`_

v0.1.0+wwfx.1.0.0 (22 Jan 2019)
-------------------------------

- Added patches by Rodeo FX up to `v0.1.1_rdo3`_
- Added ``AppCommand`` changes by `Gael-Honorez-sb`_

v0.1.0 (03 Mar 2016)
--------------------

- Initial tag, pre-release by `Rob Blau`_ (`b9cca6e`_).


.. _`Rob Blau`: https://github.com/robblau
.. _`b9cca6e`: https://github.com/robblau/tk-katana/tree/b9cca6e4009ff84870d6e691c2b25e818dc99d1a
.. _`v0.1.1_rdo3`: https://github.com/rodeofx/tk-katana/commit/0ddace4f285ff7f9642c165d3d225754584bbaf9
.. _`Gael-Honorez-sb`: https://github.com/Gael-Honorez-sb/tk-katana/commit/e06ab6b6b38960efbbdb18dc73b139aae278b040
.. _`adb98c1`: https://github.com/demon7x/tk-katana/commit/adb98c1ded02fa2de2d78177396e97d4ae56c4b0
.. _`Qt.py 1.1.0`: https://github.com/mottosso/Qt.py/tree/1.1.0
.. _`GitHub Releases page`: https://github.com/wwfxuk/tk-katana/releases
