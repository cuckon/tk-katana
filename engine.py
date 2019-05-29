#
# Copyright (c) 2013 Shotgun Software, Inc
# ----------------------------------------------------
#
"""
A Katana engine for Shotgun Toolkit.
"""
import os
import traceback

import sgtk
from sgtk.log import LogManager
from sgtk.util.qt_importer import QtImporter

from Katana import Configuration
from Katana import Callbacks
import UI4.App.MainWindow


__all__ = ('KatanaEngine',)


class KatanaEngine(sgtk.platform.Engine):
    """
    An engine that supports Katana.
    """

    def __init__(self, *args, **kwargs):
        self._ui_enabled = bool(Configuration.get('KATANA_UI_MODE'))
        super(KatanaEngine, self).__init__(*args, **kwargs)

    @property
    def has_ui(self):
        """
        Whether Katana is running as a GUI/interactive session.
        """
        return self._ui_enabled

    @classmethod
    def main_window_ready(cls):
        """
        Whether Katana is fully started and the main window/menu is available.

        Returns:
            bool: Whether the main window is available.
        """
        return bool(UI4.App.MainWindow.GetMainWindow())

    def init_engine(self):
        self.logger.debug("%s: Initializing...", self)
        os.environ["SGTK_KATANA_ENGINE_INIT_NAME"] = self.instance_name

    def add_katana_menu(self, **kwargs):
        self.logger.info("Start creating Shotgun menu.")

        menu_name = "Shotgun"
        if self.get_setting("use_sgtk_as_menu_name", False):
            menu_name = "Sgtk"

        tk_katana = self.import_module("tk_katana")
        self._menu_generator = tk_katana.MenuGenerator(self, menu_name)

    def pre_app_init(self):
        """
        Called at startup.
        """
        tk_katana = self.import_module("tk_katana")

        # Make sure callbacks tracking the context switching are active.
        tk_katana.tank_ensure_callbacks_registered()

    def post_app_init(self):
        if self.has_ui:
            try:
                if self.main_window_ready():
                    self.add_katana_menu()
                else:
                    self.logger.debug(
                        'Adding onStartupComplete callback for '
                        '"KatanaEngine.add_katana_menu" as '
                        'main Katana window is not ready yet.'
                    )
                    Callbacks.addCallback(
                        Callbacks.Type.onStartupComplete,
                        self.add_katana_menu,
                    )
            except Exception:
                self.logger.error(
                    'Failed to add Katana menu\n%s',
                    traceback.format_exc(),
                )

    def destroy_engine(self):
        if self.has_ui and self.main_window_ready():
            self.logger.debug("%s: Destroying...", self)
            try:
                self._menu_generator.destroy_menu()
            except Exception:
                self.logger.error(
                    'Failed to destoy menu\n%s',
                    traceback.format_exc()
                )

    def launch_command(self, cmd_id):
        callback = self._callback_map.get(cmd_id)
        if callback is None:
            self.logger.error("No callback found for id: %s", cmd_id)
            return
        callback()

    def _define_qt_base(self):
        """Override to setup PyQt5 bindings for PySide 1 using Qt.py.

        This is one of the paths-of-least-resistance hack to get
        PyQt5 compatibility quickly.

        Since our patcher and Qt.py is local to tk_katana, we can only
        fetch them here using the engine's ``import_module()``.

        In the future, after some heavy refactoring and big-brain thinking,
        we should up-stream a solid PyQt5 compatibility into `sgtk.util`.

        Returns:
            dict[str]: Mapping of Qt module, class and bindings names.
                - "qt_core", QtCore module to use
                - "qt_gui", QtGui module to use
                - "wrapper", Qt wrapper root module, e.g. PySide
                - "dialog_base", base class for Tank's dialog factory.
        """
        utils = self.import_module("utils")
        vendor = self.import_module("vendor")

        class QtPyImporter(QtImporter):
            """Extend QtImporter to use Qt.py.

            Due to our patcher and Qt.py is local to tk_katana, this class is
            defined within this method to utilise modules imported by
            the engine's ``import_module()``.

            Attributes:
                logger (logging.Logger):
                    Standard Python logger for this Importer.
                interface_version_requested (int):
                    Qt interface version requested during construction.
                base (dict[str]):
                    Mapping of Qt module, class and bindings names.
            To Do:
                Refactor and upstream our attributes to
                ``sgtk.util.qt_importer.QtImporter``.
            """

            def __init__(self, interface_version_requested=QtImporter.QT4):
                """Extended to add local logger.

                Args:
                    interface_version_request (int):
                        Custom version of the Qt API is requested.
                """
                self._interface_version_requested = interface_version_requested
                self._logger = LogManager.get_logger(self.__class__.__name__)
                super(QtPyImporter, self).__init__(interface_version_requested)

            def _import_qt_dot_py_as_pyside(self):
                """Imports using Qt.py, re-map for PySide using PyQt5Patcher.

                This method is where the magic happens. See the class docs
                for ``PyQt5Patcher`` for more details on PyQt5 patching.

                Returns:
                    tuple(str, str, module, dict[str, module], tuple[int]):
                        - Binding name
                        - Binding version
                        - Qt module
                        - QtCore, QtGui, QtNetwork and QtWebKit mapping
                        - Version as a tuple of integers
                """
                patcher_class = utils.PyQt5Patcher
                QtCore, QtGui = patcher_class.patch(
                    vendor.Qt.QtCore,
                    vendor.Qt.QtGui,
                    vendor.Qt.QtWidgets,
                )
                QtNetwork = getattr(vendor.Qt, "QtNetwork", None)

                # Might be ugly mate, see deprecation:
                # https://doc.qt.io/qt-5/qtwebenginewidgets-qtwebkitportingguide.html
                QtWebKit = getattr(vendor.Qt, "QtWebEngineWidgets", None)

                return (
                    "Qt",
                    vendor.Qt.__version__,
                    vendor.Qt,
                    {
                        "QtCore": QtCore,
                        "QtGui": QtGui,
                        "QtNetwork": QtNetwork,
                        "QtWebKit": QtWebKit,
                    },
                    self._to_version_tuple(QtCore.qVersion()),
                )

            def _import_modules(self, interface_version):
                """Import Qt bindings for a given interface version.

                Tries to import binding implementations in the following order:

                - Qt.py (Uses PySide2 standards)
                - PySide2
                - PySide
                - PyQt4

                Returns:
                    tuple(str, str, module, dict[str, module], tuple[int]):
                        - Binding name
                        - Binding version
                        - Qt module
                        - QtCore, QtGui, QtNetwork and QtWebKit mapping
                        - Version as a tuple of integers

                        Or all are ``None`` if no bindings are available.
                """
                self.logger.debug(
                    "Requesting %s-like interface",
                    "Qt4" if interface_version == self.QT4 else "Qt5"
                )

                # First try Qt.Py
                if interface_version == self.QT4:
                    try:
                        qt_dot_py = self._import_qt_dot_py_as_pyside()
                        self.logger.debug("Imported Qt.py as PySide.")
                        return qt_dot_py
                    except ImportError:
                        pass

                # Then try parent class's bindings.
                return super(QtPyImporter, self)._import_modules(
                    interface_version
                )

            @property
            def interface_version_requested(self):
                """Get the interface version requested during construction.

                Returns:
                    int: Qt interface version requested during construction.
                """
                return self._interface_version_requested

            @property
            def logger(self):
                """Get the Python logger

                Returns:
                    logging.Logger: Standard Python logger for this importer.
                """
                return self._logger

            @property
            def base(self):
                """Extends the parent property for older, Qt4 based interfaces.

                The parent ``QtImporter.base`` seems to only be used
                exclusively when ``interface_version_requested`` was Qt5.

                To make it useful for older Qt4 interfaces, the following
                common mappings are used instead for Qt4 as inspired by
                ``tank.platform.engine.Engine._define_qt_base`` :

                - "qt_core", QtCore module to use
                - "qt_gui", QtGui module to use
                - "wrapper", Qt wrapper root module, e.g. PySide
                - "dialog_base", base class for Tank's dialog factory.

                Returns:
                    dict[str]: Mapping of Qt module, class and bindings names.
                """
                base = {"qt_core": None, "qt_gui": None, "dialog_base": None}

                if self._interface_version_requested == self.QT5:
                    base = super(QtPyImporter, self).base

                elif self._interface_version_requested == self.QT4:
                    base = {
                        "qt_core": self.QtCore,
                        "qt_gui": self.QtGui,
                        "dialog_base": getattr(self.QtGui, 'QDialog', None),
                        "wrapper": self.binding,
                    }

                return base

        return QtPyImporter().base
