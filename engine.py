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

from Katana import Configuration
from Katana import Callbacks
import UI4.App.MainWindow


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

        :return: Whether the main window is available.
        :rtype: bool
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
        try:
            from PySide2 import QtGui
        except ImportError:
            # fine, we don't expect PySide2 to be present just yet
            self.logger.debug("PySide2 not detected - trying for PySide now...")
        else:
            # looks like pyside2 is already working! No need to do anything
            self.logger.debug("PySide2 detected - the existing version will be used.")
            return super(KatanaEngine, self)._define_qt_base()

        class QTProxy(object):
            def __getattr__(self,name):
                raise sgtk.TankError("LOOKS")

        base = {"qt_core" : QTProxy(),"qt_gui": QTProxy(),"dialog_base":None}

        try:
            from PyQt4 import QtCore, QtGui
            import PyQt4
            QtCore.Signal = QtCore.pyqtSignal
            QtCore.Slot = QtCore.pyqtSlot
            QtCore.Property = QtCore.pyqtProperty
            QtCore.__version__ = QtCore.QT_VERSION_STR
            base["qt_core"] = QtCore
            base["qt_gui"] = QtGui
            base["dialog_base"] = QtGui.QDialog
            self.logger.debug(
                "Successfully initialized PyQt '%s' located in %s.",
                QtCore.PYQT_VERSION_STR,
                PyQt4.__file__,
            )
        except ImportError as error:
            self.logger.warn(str(error))
        except Exception:
            import traceback
            self.logger.warn(
                "Error setting up PyQt. PyQt based UI support "
                "will not be available\n%s",
                traceback.format_exc(),
            )
        self.logger.debug('qt_base: %s', base)
        return base
