#
# Copyright (c) 2013 Shotgun Software, Inc
# ----------------------------------------------------
#
"""
A Katana engine for Shotgun Toolkit.
"""
from distutils.version import StrictVersion
import logging
import os
import traceback

import sgtk

from Katana import Callbacks
from Katana import Configuration
import UI4.App.MainWindow


katana_logger = logging.getLogger("tk-katana.engine")

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
        katana_version = os.environ['KATANA_RELEASE'].replace('v', '.')
        if StrictVersion(katana_version) < StrictVersion('3.1'):
            # Hint to Qt.Py older Katana uses SIP v1 (PyQt4).
            os.environ['QT_SIP_API_HINT'] = '1'

        vendor = self.import_module("vendor")
        utils = self.import_module("utils")
        return utils.QtPyImporter(vendor.Qt).base

    def _emit_log_message(self, handler, record):
        """
        Called by the engine to log messages in Katana.
        All log messages from the toolkit logging namespace will be passed to this method.

        :param handler: Log handler that this message was dispatched from.
                        Its default format is "[levelname basename] message".
        :type handler: :class:`~python.logging.LogHandler`
        :param record: Standard python logging record.
        :type record: :class:`~python.logging.LogRecord`
        """
        # Give a standard format to the message:
        #     Shotgun <basename>: <message>
        # where "basename" is the leaf part of the logging record name,
        # for example "tk-multi-shotgunpanel" or "qt_importer".
        if record.levelno < logging.INFO:
            formatter = logging.Formatter("Debug: Shotgun %(basename)s: %(message)s")
        else:
            formatter = logging.Formatter("Shotgun %(basename)s: %(message)s")

        msg = formatter.format(record)
        katana_logger.log(record.levelno, msg)
