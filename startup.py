# Copyright (c) 2013 Shotgun Software Inc.
#
# CONFIDENTIAL AND PROPRIETARY
#
# This work is provided "AS IS" and subject to the Shotgun Pipeline Toolkit
# Source Code License included in this distribution package. See LICENSE.
# By accessing, using, copying or modifying this work you indicate your
# agreement to the Shotgun Pipeline Toolkit Source Code License. All rights
# not expressly granted therein are reserved by Shotgun Software Inc.

import os
import sys

import sgtk
from sgtk.platform import constants, SoftwareLauncher, SoftwareVersion, LaunchInformation


class KatanaLauncher(SoftwareLauncher):
    """
    Handles launching Katana executables. Automatically starts up
    a tk-katana engine with the current context in the new session
    of Katana.
    """

    # Named regex strings to insert into the executable template paths when
    # matching against supplied versions and products. Similar to the glob
    # strings, these allow us to alter the regex matching for any of the
    # variable components of the path in one place
    COMPONENT_REGEX_LOOKUP = {
        "version": r"\d+\.\d+v\d+",
    }

    # This dictionary defines a list of executable template strings for each
    # of the supported operating systems. The templates are used for both
    # globbing and regex matches by replacing the named format placeholders
    # with an appropriate glob or regex string.

    EXECUTABLE_TEMPLATES = {
        "win32": [
            "C:/Program Files/Katana{version}/bin/katanaBin.exe",
        ],
        "linux2": [
            "/opt/foundry/katana-program/katana",
        ]
    }

    @property
    def minimum_supported_version(self):
        """
        The minimum software version that is supported by the launcher.
        """
        return "3.1v1"
      
    def _get_resource_paths(self):
        """
        Retrieve any resource paths for any installed apps. 

        Resources live in the "resources/Katana" directory relative the the app's
        root directory.

        :returns: List of paths.
        """
        paths = []
        env_name = self.context.sgtk.execute_core_hook(
            constants.PICK_ENVIRONMENT_CORE_HOOK_NAME,
            context=self.context
        )
        env = self.context.sgtk.pipeline_configuration.get_environment(env_name, self.context)
        apps = env.get_apps("tk-katana")
        for app in apps:
            app_descriptor = env.get_app_descriptor("tk-katana", app)
            path = app_descriptor.get_path()
            resource_path = os.path.join(path, "resources", "Katana")
            if os.path.isdir(resource_path):
                self.logger.debug("Found resource path for '{}': '{}'".format(app.upper(), resource_path))
                paths.append(resource_path)
        return paths

    def prepare_launch(self, exec_path, args, file_to_open=None):
        """
        Prepares an environment to launch Katana in that will automatically
        load Toolkit and the tk-katana engine when Katana starts.

        :param str exec_path: Path to Katana executable to launch.
        :param str args: Command line arguments as strings.
        :param str file_to_open: (optional) Full path name of a file to open on
                                            launch.
        :returns: :class:`LaunchInformation` instance
        """
        required_env = {}

        # Run the engine's init.py file when Katana starts up
        startup_paths = [os.path.join(self.disk_location, "resources", "Katana")]

        # Prepare the launch environment with variables required by the
        # classic bootstrap approach.
        self.logger.debug(
            "Preparing Katana Launch via Toolkit Classic methodology ...")
        required_env["SGTK_ENGINE"] = self.engine_name
        required_env["SGTK_CONTEXT"] = sgtk.context.serialize(self.context)
        required_env["PYTHONPATH"] = os.environ["PYTHONPATH"]
        startup_paths.extend(self._get_resource_paths())
        startup_path = os.pathsep.join(startup_paths)
        required_env["KATANA_RESOURCES"] = startup_path

        if file_to_open:
            # Add the file name to open to the launch environment
            required_env["SGTK_FILE_TO_OPEN"] = file_to_open

        return LaunchInformation(exec_path, args, required_env)

    def scan_software(self):
        """
        Scan the filesystem for katana executables.

        :return: A list of :class:`SoftwareVersion` objects.
        """
        self.logger.debug("Scanning for Katana executables...")

        supported_sw_versions = []
        for sw_version in self._find_software():
            (supported, reason) = self._is_supported(sw_version)
            if supported:
                supported_sw_versions.append(sw_version)
            else:
                self.logger.debug(
                    "SoftwareVersion %s is not supported: %s" %
                    (sw_version, reason)
                )

        return supported_sw_versions

    def _find_software(self):
        """
        Find executables in the default install locations.
        """

        # all the executable templates for the current OS
        executable_templates = self.EXECUTABLE_TEMPLATES.get(sys.platform, [])

        # all the discovered executables
        sw_versions = []

        for executable_template in executable_templates:

            self.logger.debug("Processing template %s.", executable_template)

            executable_matches = self._glob_and_match(
                executable_template,
                self.COMPONENT_REGEX_LOOKUP
            )

            # Extract all products from that executable.
            for (executable_path, key_dict) in executable_matches:

                # extract the matched keys form the key_dict (default to None
                # if not included)
                executable_version = key_dict.get("version")

                sw_versions.append(
                    SoftwareVersion(
                        executable_version,
                        "Katana",
                        executable_path,
                        self.icon_256
                    )
                )

        return sw_versions
