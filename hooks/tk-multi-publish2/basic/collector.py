# Copyright (c) 2017 Shotgun Software Inc.
#
# CONFIDENTIAL AND PROPRIETARY
#
# This work is provided "AS IS" and subject to the Shotgun Pipeline Toolkit
# Source Code License included in this distribution package. See LICENSE.
# By accessing, using, copying or modifying this work you indicate your
# agreement to the Shotgun Pipeline Toolkit Source Code License. All rights
# not expressly granted therein are reserved by Shotgun Software Inc.

from operator import methodcaller
import os
import sgtk

from Katana import FarmAPI, NodegraphAPI

HookBaseClass = sgtk.get_hook_baseclass()


class KatanaSessionCollector(HookBaseClass):
    """
    Collector that operates on the katana session. Should inherit from the
    basic collector hook.
    """

    @property
    def settings(self):
        """
        Dictionary defining the settings that this collector expects to receive
        through the settings parameter in the process_current_session and
        process_file methods.

        A dictionary on the following form::

            {
                "Settings Name": {
                    "type": "settings_type",
                    "default": "default_value",
                    "description": "One line description of the setting"
            }

        The type string should be one of the data types that toolkit accepts as
        part of its environment configuration.
        """

        # grab any base class settings
        collector_settings = super(KatanaSessionCollector, self).settings or {}

        # settings specific to this collector
        katana_session_settings = {
            "Work Template": {
                "type": "template",
                "default": None,
                "description": "Template path for artist work files. Should "
                               "correspond to a template defined in "
                               "templates.yml. If configured, is made available"
                               "to publish plugins via the collected item's "
                               "properties. ",
            },
        }

        # update the base settings with these settings
        collector_settings.update(katana_session_settings)

        return collector_settings

    def process_current_session(self, settings, parent_item):
        """
        Analyzes the current session open in Katana and parents a subtree of
        items under the parent_item passed in.

        :param dict settings: Configured settings for this collector
        :param parent_item: Root item instance

        """
        # create an item representing the current katana session
        item = self.collect_current_katana_session(settings, parent_item)
        self.collect_renders(item)
        self.collect_look_files(item)

    def collect_current_katana_session(self, settings, parent_item):
        """
        Creates an item that represents the current katana session.

        :param parent_item: Parent Item instance

        :returns: Item of type katana.session
        """

        publisher = self.parent

        # get the path to the current file
        path = FarmAPI.GetKatanaFileName()

        # determine the display name for the item
        if path:
            file_info = publisher.util.get_file_path_components(path)
            display_name = file_info["filename"]
        else:
            display_name = "Current Katana Session"

        # create the session item for the publish hierarchy
        session_item = parent_item.create_item(
            "katana.session",
            "Katana Session",
            display_name
        )

        # get the icon path to display for this item
        icon_path = os.path.join(
            self.disk_location,
            os.pardir,
            "icons",
            "katana.png"
        )
        session_item.set_icon_from_path(icon_path)

        # discover the project root which helps in discovery of other
        # publishable items
        project_root = os.path.dirname(FarmAPI.GetKatanaFileName())
        session_item.properties["project_root"] = project_root

        # if a work template is defined, add it to the item properties so
        # that it can be used by attached publish plugins
        work_template_setting = settings.get("Work Template")
        if work_template_setting:

            work_template = publisher.engine.get_template_by_name(
                work_template_setting.value)

            # store the template on the item for use by publish plugins. we
            # can't evaluate the fields here because there's no guarantee the
            # current session path won't change once the item has been created.
            # the attached publish plugins will need to resolve the fields at
            # execution time.
            session_item.properties["work_template"] = work_template
            self.logger.debug("Work template defined for Katana collection.")

        self.logger.info("Collected current Katana scene")

        return session_item

    def collect_look_files(self, parent_item):
        """
        Collect all the SGLookFileBake nodes in the scene. 
        Add to parent item.

        :param parent_item: Parent Item instance
        """
        sg_look_file_nodes = NodegraphAPI.GetAllNodesByType("SGLookFileBake")

        get_name = methodcaller("getName")
        for node in sorted(sg_look_file_nodes, key=get_name):
            parent_item.create_item(
                "katana.session.lookfile",
                "Look File",
                node.getName()
            )

    @staticmethod
    def _get_template(template_name):
        """
        Get the template object from the given name.

        :param template_name: The name of the template to retrieve.
        :returns: The template object.
        """
        engine = sgtk.platform.current_engine()
        return engine.get_template_by_name(template_name)   

    def collect_renders(self, parent_item):
        """
        Collect all the SGRenderOutputDefine nodes in the scene. 
        Add to parent item.

        :param parent_item: Parent Item instance
        """
        sg_nodes = NodegraphAPI.GetAllNodesByType("SGRenderOutputDefine")
        get_name = methodcaller("getName")
        for node in sorted(sg_nodes, key=get_name):
            node_name = node.getName()
            internal_node = node.getChildByIndex(0)
            param = internal_node.getParameter("outputName")
            output = param.getValue(0)
            publish_name = "{}, {}".format(node_name, output)
            item = parent_item.create_item(
                "katana.session.render",
                "Rendered Image",
                publish_name
            )
            item.properties["node"] = node
            item.properties["path"] = node.getParameter("sg_renderLocation").getValue(0)
            item.properties["work_template"] = self._get_template(
                node.getParameter("sg_work_template").getValue(0)
            )
            item.properties["publish_template"] = self._get_template(
                node.getParameter("sg_publish_template").getValue(0)
            )
            item.properties["publish_name"] = publish_name
            item.properties["publish_type"] = "Rendered Image"
            item.properties["__collector"] = self