# By Sam Saxon sam.saxon@thefoundry.com
# Copied from the equivalent Nuke file.

import os
from Katana import KatanaFile

import sgtk
from sgtk.platform.qt import QtGui

HookBaseClass = sgtk.get_hook_baseclass()


class SceneOperation(HookBaseClass):
    """ Hook called to perform an operation with the current scene."""

    def execute(self, operation, file_path, context, parent_action, file_version, read_only, **kwargs):
        """Main hook entry point.

        Args:
            operation (str):
                Scene operation to perform

            file_path (str):
                File path to use if the operation
                requires it (e.g. open)

            context (sgtk.Context):
                The context the file operation is being
                performed in.

            parent_action (str):
                Action that this scene operation is being executed for.
                This can be one of:

                - "open_file"
                - "new_file"
                - "save_file_as"
                - "version_up"

            file_version:
                The version/revision of the file to be opened.
                If this is ``None`` then the latest version should be opened.

            read_only (bool):
                Specifies if the file should be opened read-only or not

        Returns:
            object: Depending on ``operation``:

                - 'current_path': Current scene file path as a ``str``
                - 'reset': ``True`` if scene was reset to an empty state,
                   otherwise ``False``
                - all others: ``None``
        """
        if operation == "current_path":
            # return the current scene path
            return file_path

        elif operation == "open":
            KatanaFile.Load(file_path)

        elif operation == "save":
            if not os.path.exists(os.path.dirname(file_path)):
                os.makedirs(os.path.dirname(file_path))
            KatanaFile.Save(file_path)

        elif operation == "save_as":
            if not os.path.exists(os.path.dirname(file_path)):
                os.makedirs(os.path.dirname(file_path))
            KatanaFile.Save(file_path)

        elif operation == "reset":
            while KatanaFile.IsFileDirty():
                # Changes have been made to the scene
                res = QtGui.QMessageBox.question(None,
                                                 "Save your scene?",
                                                 "Your scene has unsaved changes. Save before proceeding?",
                                                 QtGui.QMessageBox.Yes|QtGui.QMessageBox.No|QtGui.QMessageBox.Cancel)

                if res == QtGui.QMessageBox.Cancel:
                    return False

                elif res == QtGui.QMessageBox.No:
                    break

                else:
                    if not os.path.exists(os.path.dirname(file_path)):
                        os.makedirs(os.path.dirname(file_path))
                KatanaFile.Save(file_path) # TODO: warning: this may not work...

            return True
