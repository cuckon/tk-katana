# tk-katana

[![Build Status][]](https://travis-ci.com/wwfxuk/tk-katana)
[![Docs GitHub Pages][]](https://wwfxuk.github.io/tk-katana)
[![GitHub release][]](https://github.com/wwfxuk/tk-katana/releases)
[![Linting][]](https://houndci.com)
[![Katana Minimum 3.1v1][]](https://learn.foundry.com/katana/3.1/Content/release_notes/Katana%203.1v1%20Release%20Notes.html)


This engine provides Shotgun Toolkit integration for The Foundry's Katana.

For more information and documentation, check out the
[GitHub Pages for this project](https://wwfxuk.github.io/tk-katana/)

This repository is forked from [robblau's v0.1.0][]
to hopefully make it production capable again for:

* Shotgun 8 and above
* Katana 3.1 (PyQt5) using [Qt.py 1.1.0][]


[robblau's v0.1.0]: https://github.com/robblau/tk-katana/tree/b9cca6e4009ff84870d6e691c2b25e818dc99d1a
[Qt.py 1.1.0]: https://github.com/mottosso/Qt.py/tree/1.1.0
[Build Status]: https://travis-ci.com/wwfxuk/tk-katana.svg?branch=master
[Docs GitHub Pages]: https://img.shields.io/badge/docs-GitHub%20Pages-blue.svg
[GitHub release]: https://img.shields.io/github/release/wwfxuk/tk-katana.svg
[Linting]: https://img.shields.io/badge/PEP8%20by-Hound%20CI-a873d1.svg
[Katana Minimum 3.1v1]: https://img.shields.io/badge/minimum-3.1v1-yellow.svg?logo=data:image/png;base64,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