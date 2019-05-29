"""PyQt5 to PySide 1 patcher, extending ``PySide2Patcher`` in ``sgtk.util``."""
# -*- coding: utf-8 -*-
from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

from sgtk.util.pyside2_patcher import PySide2Patcher

__all__ = ('PyQt5Patcher', 'PatchedBoundSignal')


class PatchedBoundSignal(object):
    """Wrap original PyQt BoundSignal signal instances.

    Attributes:
        original_signal (PyQt5.BoundSignal): Original, wrapped signal.
    """

    def __init__(self, original_signal):
        """Wrap the original signal like a burrito.

        Args:
            original_signal (PyQt5.BoundSignal): Signal to wrap.
        """
        self.original_signal = original_signal

    def __getitem__(self, item):
        """Get original signal if requesting empty tuple.

        Args:
            item (type or tuple): Specific signal type to fetch.

        Returns:
            PyQt5.BoundSignal: Signal for required signal type.
        """
        if item is tuple():
            return self.original_signal
        else:
            return self.original_signal[item]

    def __getattr__(self, attr):
        """Get attributes from original signal.

        Args:
            attr (str): Name of attribute to fetch.

        Returns:
            object: Attribute from original signal.
        """
        return getattr(self.original_signal, attr)


class PyQt5Patcher(PySide2Patcher):
    """Patch remaining PyQt5 binding after Qt.py for PySide 1.

    So yes, this patcher is used **specifically** after Qt.py patched
    most of PyQt5 bindings for PySide2.

    It patches any remaining (Py)Qt5 bindings for PySide 1 since that's what
    Shotgun still seems to mainly target as of May 2019.

    Originally developed for Katana 3.1 for use in ``tk-katana``:

        Katana 3.1 (PyQt5)
                |
                V
              Qt.py
                |
                | Converts PyQt5 for PySide2 compatibility
                V
            PySide2Patcher (parent class from sgtk.util)
                |
                |  Converts PySide2 for PySide 1 compatibility
                V
            PyQt5Patcher (that's me!)
                |
                |  Converts any remaining PyQt5 for PySide 1 compatibility
                V
        KatanaEngine._define_qt_base
                |
                |  Engine then exposes Qt bindings publicly through...
                V
            sgtk.platform.qt
    """

    @classmethod
    def _patch_QAction(cls, QtGui):
        """PyQt5 doesn't take ``triggered[()]``, re-map to ``triggered``."""
        original_QAction = QtGui.QAction

        class QAction(original_QAction):
            """QAction with patched ``triggered`` (bound) signal."""

            def __init__(self, *args, **kwargs):
                """Extend original constructor to override triggered signal."""
                super(QAction, self).__init__(*args, **kwargs)
                self._original_triggered = self.triggered
                self.triggered = PatchedBoundSignal(self._original_triggered)

        QtGui.QAction = QAction

    @classmethod
    def _patch_QPyTextObject(cls, QtCore, QtGui):
        class QPyTextObject(QtCore.QObject, QtGui.QTextObjectInterface):
            """PyQt5 specific, create a backport QPyTextObject.

            See https://doc.bccnsoft.com/docs/PyQt5/pyqt4_differences.html?highlight=qpytextobject#qpytextobject.
            """
        QtGui.QPyTextObject = QPyTextObject

    @classmethod
    def _patch_QtCore__version__(cls, QtCore):
        """PyQt does not have ``__version__``, get it from ``qVersion()``."""
        QtCore.__version__ = QtCore.qVersion()

    @classmethod
    def patch(cls, QtCore, QtGui, QtWidgets):
        """Patches QtCore, QtGui and QtWidgets

        Args:
            QtCore (module): The QtCore module to patch.
            QtGui (module): The QtGui module to patch.
            QtWidgets (module): The QtWidgets module to patch.
        """
        qt_core_shim, qt_gui_shim = PySide2Patcher.patch(
            QtCore, QtGui, QtWidgets, None,
        )

        cls._patch_QtCore__version__(qt_core_shim)
        cls._patch_QPyTextObject(qt_core_shim, qt_gui_shim)
        cls._patch_QAction(qt_gui_shim)
        return qt_core_shim, qt_gui_shim
