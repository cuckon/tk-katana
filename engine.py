#
# Copyright (c) 2013 Shotgun Software, Inc
# ----------------------------------------------------
#
"""
A Katana engine for Shotgun Toolkit.
"""
from distutils.version import StrictVersion
from functools import partial, wraps
import glob
import logging
import os
import re
import traceback

import sgtk

from Katana import Callbacks
from Katana import Configuration
import UI4.App.MainWindow


__all__ = ('delay_until_ui_visible', 'KatanaEngine')


def delay_until_ui_visible(show_func):
    """Wrapper to delay showing dialogs until Katana Main UI is visible.

    If it is not possible to show right now, ``None`` will be returned.

    Args:
        show_func (callable): Show dialog method to wrap.

    Returns:
        callable: Wrapped function

    """
    @wraps(show_func)
    def wrapper(self, *args, **kwargs):
        result = None
        ui_state = self.has_ui
        window_title = '"{args[0]}" ({args[2].__name__})'.format(args=args)

        if ui_state == self.UI_MAINWINDOW_VISIBLE:
            # Remove added kwarg from Katana's Callbacks.addCallback
            kwargs.pop('objectHash', None)
            result = show_func(self, *args, **kwargs)

        elif ui_state:
            self.logger.info(
                'Delaying %s for %s until Katana main window is showing.',
                show_func.__name__, window_title,
            )
            func = partial(wrapper, self, *args, **kwargs)
            Callbacks.addCallback(Callbacks.Type.onStartupComplete, func)
        else:
            self.logger.error(
                "Sorry, this environment doesn't support UI display! Can't"
                ' show the requested window %s.', window_title,
            )

        # lastly, return the instantiated widget
        return result

    return wrapper


def frames_from_path(path):
    """Get sorted list of frame numbers from a given path.

    Limited currently to only finding frame number directly before the
    file extension, i.e. first part from `os.path.splitext(path)`.

    Supports extracting frame numbers from these sequence definitions:

    - Just numbers: `1023` or `000` or `99`
    - Just hashes: `####` for to match frames like `0909` or `1182`
    - `0*d` with optional `%`: `%03d` to match frames like `023` and `248`

    See Also:
        `NukeActions._sequence_range_from_path()` from
        `tk-multi-loader2(v1.19.3)/hooks/tk-nuke_actions.py`

    Args:
        path (str): File path with a sequence definition in it.

    Returns:
        list[int]: Sorted list of frame numbers.
    """
    frames = []
    sequence_pattern = re.compile(
        r"(?P<numbers>[0-9]+)$"        # e.g. 1023 or 000 or 99
        r"|(?P<hashes>#+)$"            # e.g. ####
        r"|[%]0(?P<percentage>\d+)d$"  # e.g. 02d or %04d or 010d
    )
    root, ext = os.path.splitext(path)
    matched = sequence_pattern.search(root)
    if matched:
        glob_expr = "[0-9]"
        for style, text in matched.groupdict().items():
            if text is not None:
                if style in ['hashes', 'numbers']:
                    glob_expr *= len(text)  # "[0-9][0-9]" for "00" or "##"
                elif style == 'percentage':
                    glob_expr *= int(text)  # "[0-9][0-9]" for "2" in "%02d"
                else:
                    glob_expr = "*"
                break

        # e.g. "/path/to/file_*.png", "/path/to/file.[0-9][0-9][0-9].exr"
        glob_path = "%s%s" % (sequence_pattern.sub(glob_expr, root), ext)

        # e.g. "\d+$" or "[0-9][0-9][0-9]$"
        frames_pattern = "%s$" % (r'\d+' if glob_expr == "*" else glob_expr)

        for file_path in glob.iglob(glob_path):
            root = os.path.splitext(file_path)[0]
            frame_text = re.search(frames_pattern, root).group(0)
            frames.append(int(frame_text))

    return list(sorted(frames)) or None


class KatanaEngine(sgtk.platform.Engine):
    """
    An engine that supports Katana.
    """
    UI_MAINWINDOW_NONE = 1
    UI_MAINWINDOW_INVISIBLE = 2
    UI_MAINWINDOW_VISIBLE = 3

    def __init__(self, *args, **kwargs):
        self._ui_enabled = bool(Configuration.get('KATANA_UI_MODE'))
        super(KatanaEngine, self).__init__(*args, **kwargs)

        # Add Katana's handlers to engine's Shotgun logger
        for katana_handler in logging.getLogger().handlers:
            self.logger.addHandler(katana_handler)

        # Cache all sgtk.SequenceKey from all templates
        sequence_keys = set()
        for template in self.sgtk.templates.values():
            for key in template.keys.values():
                if isinstance(key, sgtk.SequenceKey):
                    sequence_keys.add(key)
        self._sequence_keys = tuple(sequence_keys)

    @property
    def sequence_keys(self):
        """Get stored cached of all templates' sequnce keys.

        Returns:
            tuple[sgtk.SequenceKey]: All templates' sequence keys.
        """
        return self._sequence_keys

    @property
    def has_ui(self):
        """Whether Katana is running as a GUI/interactive session.

        If it is, return the corresponding UI state enum.

        Returns:
            False or int: Main Window state, else False if not in GUI mode.
        """
        if self._ui_enabled:
            window = UI4.App.MainWindow.GetMainWindow()
            if window is None:
                return self.UI_MAINWINDOW_NONE
            elif window.isVisible():
                return self.UI_MAINWINDOW_VISIBLE
            else:
                return self.UI_MAINWINDOW_INVISIBLE
        return self._ui_enabled

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
                if self.has_ui > self.UI_MAINWINDOW_NONE:
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
        if self.has_ui > self.UI_MAINWINDOW_NONE:
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

    @delay_until_ui_visible
    def show_dialog(self, title, bundle, widget_class, *args, **kwargs):
        """Overridden to delay showing until UI is fully initialised.

        If it is not possible to show right now, ``None`` will be returned.

        Args:
            title (str):
                Title of the window. This will appear in the Toolkit title bar.
            bundle (sgtk.platform.bundle.TankBundle):
                The app, engine or framework associated with this window.
            widget_class (QtWidgets.QWidget):
                Class of the UI to be constructed, must subclass from QWidget.
            args (list):
                Arguments for the ``widget_class`` constructor.
            kwargs (list):
                Keyword arguments for the ``widget_class`` constructor.

        Returns:
            QtWidgets.QWidget or None: Widget of dialog shown, if any.
        """
        return super(KatanaEngine, self).show_dialog(
            title, bundle, widget_class, *args, **kwargs
        )

    @delay_until_ui_visible
    def show_modal(self, title, bundle, widget_class, *args, **kwargs):
        """Overridden to delay showing until UI is fully initialised.

        If it is not possible to show right now, ``None`` will be returned.

        Args:
            title (str):
                Title of the window. This will appear in the Toolkit title bar.
            bundle (sgtk.platform.bundle.TankBundle):
                The app, engine or framework associated with this window.
            widget_class (QtWidgets.QWidget):
                Class of the UI to be constructed, must subclass from QWidget.
            args (list):
                Arguments for the ``widget_class`` constructor.
            kwargs (list):
                Keyword arguments for the ``widget_class`` constructor.

        Returns:
            (int, QtWidgets.QWidget) or None: Widget of dialog shown, if any.
        """
        return super(KatanaEngine, self).show_modal(
            title, bundle, widget_class, *args, **kwargs
        )

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
