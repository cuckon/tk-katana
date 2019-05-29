#
# Copyright (c) 2013 Shotgun Software, Inc
# ----------------------------------------------------
#
from collections import defaultdict
import os
import traceback
import unicodedata

# sgtk.platform.qt imports deferred to fix engine import_module errors

import UI4.App


class MenuGenerator(object):
    """
    A Katana specific menu generator.
    """

    def __init__(self, engine, menu_name):
        """
        Initializes a new menu generator.

        :param engine: The currently-running engine.
        :type engine: :class:`sgtk.platform.Engine`
        :param menu_name: The name of the menu to be created.
        """
        self._engine = engine
        self._menu_name = menu_name
        self._app_commands = self.get_all_app_commands()
        self.root_menu = self.setup_root_menu()

        # now add the context item on top of the main menu
        self._context_menu = self._add_context_menu()
        self.root_menu.addSeparator()

        apps_commands = defaultdict(list)
        for app_command in self._app_commands:
            if app_command.favourite:
                app_command.add_command_to_menu(self.root_menu)

            if app_command.type == "context_menu":
                app_command.add_command_to_menu(self._context_menu)
            else:
                app_name = app_command.app_name
                apps_commands[app_name].append(app_command)
        self.root_menu.addSeparator()

        self._add_app_menu(apps_commands)

    @property
    def engine(self):
        """The currently-running engine."""
        return self._engine

    @property
    def menu_name(self):
        """The name of the menu to be generated."""
        return self._menu_name

    def get_all_app_commands(self):
        commands = []
        favourites = self.engine.get_setting("menu_favourites", default=[])

        for cmd_name, cmd_details in sorted(self.engine.commands.items()):
            app_command = AppCommand(self.engine, cmd_name, cmd_details)
            app_command.favourite = any(
                app_command == item
                for item in favourites
            )
            commands.append(app_command)
        return commands

    def setup_root_menu(self):
        """
        Attempts to find an existing menu of the specified title.

        If it can't be found, it creates one.
        """
        from sgtk.platform.qt import QtGui
        # Get the "main menu" (the bar of menus)
        main_menu_bar = self.get_katana_main_bar()

        # Attempt to find existing menu
        for menu in main_menu_bar.children():
            is_menu = isinstance(menu, QtGui.QMenu)
            if is_menu and menu.title() == self.menu_name:
                return menu

        # Otherwise, create a new menu
        return main_menu_bar.addMenu(self.menu_name)

    @classmethod
    def get_katana_main_bar(cls):
        """Get Katana GUI's main menu bar.

        :raises RuntimeError: Cannot get Katana GUI's main menu bar.
        :return: Katana GUI's main menu bar.
        :rtype: UI4.App.MainMenu.MainMenu
        """
        from sgtk.platform.qt import QtGui
        main_window = UI4.App.MainWindow.GetMainWindow()
        if main_window is not None:
            return main_window.getMenuBar()

        # Using LayoutsMenu to get main Katana menu bar instead'
        for layout_menu in QtGui.qApp.topLevelWidgets():
            if isinstance(layout_menu, UI4.App.MainMenu.LayoutsMenu):
                return layout_menu.parent()

        raise RuntimeError('Failed to get main Katana menu bar')

    def destroy_menu(self):
        """
        Destroys the Shotgun menu.
        """
        if self.root_menu is not None:
            self.root_menu.clear()

    ###########################################################################
    # context menu and UI

    def _add_context_menu(self):
        """
        Adds a context menu which displays the current context.
        """
        from sgtk.platform.qt import QtGui
        # create the context menu
        ctx = self.engine.context
        menu = self.root_menu.addMenu(str(ctx))
        style = menu.style()

        action = menu.addAction('Jump to File System')
        action.triggered.connect(self._jump_to_fs)
        action.setIcon(style.standardIcon(style.SP_DialogOpenButton))

        action = menu.addAction('Jump to Shotgun')
        action.triggered.connect(self._jump_to_sg)
        try:
            import sgtk.platform.qt.resources_rc
        except ImportError:
            self.engine.logger.warn(traceback.format_exc())
        else:
            action.setIcon(QtGui.QIcon(':/Tank.Platform.Qt/tank_logo.png'))

        menu.addSeparator()
        return menu

    def _open_path(self, path):
        """Open a given folder path/url using QDesktopServices.

        This should offer a unified, cross platform way of opening links and
        folders on disks that doesn't raise errors on fail, only logs warnings.

        :param path: Folder path/URL to open.
        :type path: str
        """
        from sgtk.platform.qt import QtGui, QtCore
        url = QtCore.QUrl(path)
        error = ''
        if not url.isValid():
            error = 'Unable to open path as it did not convert to QUrl: "%s"'
        elif not QtGui.QDesktopServices.openUrl(url):
            error = 'Failed to open path "%s". Check logs and console output.'

        if error:
            self.engine.logger.warn(error, path)

    def _jump_to_sg(self):
        """
        Opens current context's Shotgun URL.
        """
        self._open_path(self.engine.context.shotgun_url)

    def _jump_to_fs(self):
        """
        Opens current context's folders on the file system.
        """
        # launch one window for each location on disk
        for disk_location in self.engine.context.filesystem_locations:
            path = os.path.abspath(os.path.expanduser(disk_location))
            self._open_path('file:///' + path.replace('\\', '/'))

    ###########################################################################
    # app menus

    def _add_app_menu(self, commands_by_app):
        """
        Add all apps to the main menu, process them one by one.
        """
        for app_name, commands in sorted(commands_by_app.items()):
            if len(commands) == 1:
                # Single entry, display on root menu
                # todo: Should this be labelled with the name of the app
                # or the name of the menu item? Not sure.
                app_menu = self.root_menu
                # Skip if favourite (since it is already on the menu)
                commands = [] if commands[0].favourite else commands
            else:
                # More than one menu entry for this app
                # make a sub menu and put all items in the sub menu
                app_menu = self.root_menu.addMenu(app_name)

            for app_command in commands:
                app_command.add_command_to_menu(app_menu)


class AppCommand(object):
    """
    Wraps around a single command that you get from engine.commands
    """

    def __init__(self, engine, name, command_dict):
        """Create a named wrapped command using given engine and information.

        :param engine: The currently-running engine.
        :type engine: :class:`sgtk.platform.Engine`
        :param name: The name/label of the app command.
        :type name: str
        :param command_dict: Command's information, e.g. properties, callback.
        :type command_dict: dict[str]
        """
        self._name = name
        self._engine = engine
        self._properties = command_dict["properties"]
        self._callback = command_dict["callback"]
        self._favourite = False
        self._type = self._properties.get("type", "default")
        self._app = self._properties.get("app")

        self._app_name = "Other Items"
        self._app_instance_name = None

        if self._app:
            try:
                self._app_name = self._app.display_name
            except AttributeError:
                pass

            for app_instance_name, app_instance_obj in engine.apps.items():
                if self._app == app_instance_obj:
                    self._app_instance_name = app_instance_name
                    break

    def __eq__(self, other):
        """Check if our app command matches a given dictionary of attributes.

        :param other: Another AppCommand or dictionary of attributes.
        :type other: :class:`AppCommand` or dict[str]
        :returns: Whether the other object is equivalent to this one.
        :rtype: bool
        """
        if isinstance(other, AppCommand):
            return (
                self.app == other.app and
                self.app_instance_name == other.app_instance_name and
                self.app_name == other.app_name and
                self.name == other.name and
                self.engine == other.engine and
                self.properties == other.properties and
                self.callback == other.callback and
                self.favourite == other.favourite and
                self.type == other.type
            )
        elif isinstance(other, dict) and (
                "name" in other and "app_instance" in other):
            return (
                self.name == other["name"] and
                self.app_instance_name == other["app_instance"]
            )
        else:
            return NotImplemented

    @property
    def app(self):
        """The command's parent app."""
        return self._app

    @property
    def app_instance_name(self):
        """The instance name of the parent app."""
        return self._app_instance_name

    @property
    def app_name(self):
        """The name of the parent app."""
        return self._app_name

    @property
    def name(self):
        """The name of the command."""
        return self._name

    @name.setter
    def name(self, name):
        self._name = str(name)

    @property
    def engine(self):
        """The currently-running engine."""
        return self._engine

    @property
    def properties(self):
        """The command's properties dictionary."""
        return self._properties

    @property
    def callback(self):
        """The callback function associated with the command."""
        return self._callback

    @property
    def favourite(self):
        """Whether the command is a favourite."""
        return self._favourite

    @favourite.setter
    def favourite(self, state):
        self._favourite = bool(state)

    @property
    def type(self):
        """The command's type as a string."""
        return self._type

    def get_documentation_url_str(self):
        """
        Returns the documentation URL.
        """
        doc_url = None
        if self.app:
            doc_url = self.app.documentation_url
            if isinstance(doc_url, unicode):
                doc_url = unicodedata.normalize('NFKD', doc_url)
                doc_url = doc_url.encode('ascii', 'ignore')
        return doc_url

    def add_command_to_menu(self, menu):
        """
        Add a new QAction representing this AppCommand to a given QMenu.
        """
        from sgtk.platform.qt import QtGui
        action = menu.addAction(self.name)

        key_sequence = self.properties.get("hotkey")
        if key_sequence:
            action.setShortcut(QtGui.QKeySequence(key_sequence))

        icon_path = self.properties.get("icon")
        if icon_path:
            icon = QtGui.QIcon(icon_path)
            if not icon.isNull():
                action.setIcon(icon)

        # Wrap to avoid passing args
        action.triggered.connect(lambda: self.callback())
        return action
