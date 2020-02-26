"""
Hook that loads defines all the available actions, broken down by publish type.
Copied from tk-katana_actions
"""
# -*- coding: utf-8 -*-
from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals


import errno
import os
import sgtk
from Katana import KatanaFile, NodegraphAPI

HookBaseClass = sgtk.get_hook_baseclass()


class KatanaActions(HookBaseClass):

    def generate_actions(self, sg_publish_data, actions, ui_area):
        """Get a list of action instances for a particular publish.

        This method is called each time a user clicks a publish somewhere
        in the UI. The data returned from this hook will be used to populate
        the actions menu for a publish.

        The mapping between Publish types and actions are kept in a different
        place (in the configuration) so at the point when this hook is called,
        the loader app has already established *which* actions are appropriate
        for this object.

        The hook should return at least one action for each item passed in via
        the ``actions`` parameter.

        This method needs to return detailed data for those actions, in the
        form of a list of dictionaries, each with name, params, caption
        and description keys.

        Because you are operating on a particular publish, you may tailor the
        output (caption, tooltip etc) to contain custom information suitable
        for this publish.

        The ``ui_area`` parameter is a string and indicates where the publish
        is to be shown:

        - If it will be shown in the main browsing area, "main" is passed.
        - If it will be shown in the details area, "details" is passed.
        - If it will be shown in the history area, "history" is passed.

        Please note that it is perfectly possible to create more than one
        action "instance" for an action! You can for example do scene
        introspection - if the action passed in is "character_attachment"
        you may for example scan the scene, figure out all the nodes where
        this object can be attached and return a list of action instances:
        "attach to left hand", "attach to right hand" etc.
        In this case, when more than one object is returned for an action,
        use the params key to pass additional data into the run_action hook.

        :param sg_publish_data: Shotgun data dictionary with all the standard
                                publish fields.
        :type sg_publish_data: dict[str]
        :param actions: Action strings which have been defined in the
                        app configuration.
        :type actions: list[str]
        :param ui_area: String denoting the UI Area (see above).
        :type ui_area: str
        :returns: List of dictionaries, each with keys name, params,
                  caption and description.
        :rtype: list[dict[str]]
        """
        app = self.parent
        app.log_debug("Generate actions called for UI element %s. "
                      "Actions: %s. Publish Data: %s" % (ui_area, actions, sg_publish_data))

        action_instances = []

        if "import_project" in actions:
            action_instances.append( {"name": "import_project",
                                      "params": None,
                                      "caption": "Import Project",
                                      "description": "This will open the Katana project file."} )

        if "import_look_file" in actions:
            action_instances.append( {"name": "import_look_file",
                                      "params": None,
                                      "caption": "Import Look File",
                                      "description": "This will create an LookFileAssign node corresponding to this published Look File."} )

        if "import_alembic" in actions:
            action_instances.append( {"name": "import_alembic",
                                      "params": None,
                                      "caption": "Import Alembic",
                                      "description": "This will create an Alembic_In node corresponding to this cache."} )

        if "import_image" in actions:
            action_instances.append( {"name": "import_image",
                                      "params": None,
                                      "caption": "Import image",
                                      "description": "Creates an ImageRead node for the selected item."} )

        if "texture_shader" in actions:
            action_instances.append( {"name": "texture_shader",
                                      "params": None,
                                      "caption": "Shading Texture Node",
                                      "description": "Create a renderer specific, shading node for image"} )

        return action_instances

    def execute_multiple_actions(self, actions):
        """
        Executes the specified action on a list of items.

        The default implementation dispatches each item from ``actions`` to
        the ``execute_action`` method.

        The ``actions`` is a list of dictionaries holding all the actions to
        execute. Each entry will have the following values:

            - ``name``: Name of the action to execute
            - ``sg_publish_data``: Publish information coming from Shotgun
            - ``params``: Parameters passed from the ``generate_actions`` hook

        .. note::
            This is the default entry point for the hook. It reuses the
            ``execute_action`` method for backward compatibility with hooks
            written for the previous version of the loader.

        .. note::
            The hook will stop applying the actions on the selection if an
            error is raised midway through.

        :param actions: Action dictionaries.
        :type actions: list[dict]
        """
        for single_action in actions:
            name = single_action["name"]
            sg_publish_data = single_action["sg_publish_data"]
            params = single_action["params"]
            self.execute_action(name, params, sg_publish_data)

    def execute_action(self, name, params, sg_publish_data):
        """Execute a given action.

        The data sent to this be method will represent one of the actions
        enumerated by the ``generate_actions`` method.

        :param name: Action name string representing one of the items
                     returned by ``generate_actions``.
        :type name: str
        :param params: Params data, as specified by ``generate_actions``.
        :param sg_publish_data: Shotgun data dictionary with all the standard
                                publish fields.
        :type sg_publish_data: dict[str]
        """
        # resolve path
        path = self.get_publish_path(sg_publish_data)

        if name == "import_project":
            self._import_project(path)

        if name == "import_look_file":
            node = self._create_node(
                "LookFileAssign",
                path,
                sg_publish_data,
                path_parameter="args.lookfile.asset.value"
            )
            node.getParameter('args.lookfile.asset.enable').setValue(1.0, 0)

        if name == "import_alembic":
            self._create_node(
                "Alembic_In",
                path,
                sg_publish_data,
                path_parameter="abcAsset",
            )

        if name == "import_image":
            self._create_node(
                "ImageRead",
                path,
                sg_publish_data,
                path_parameter="file",
            )

        if name == "texture_shader":
            # PublishedFile "name" with anything after "." removed
            name = bytes(sg_publish_data['code'].split('.', 1)[0])
            self._create_texture_node(path, name=name)

    ##############################################################################################################
    # helper methods which can be subclassed in custom hooks to fine tune the behaviour of things

    @staticmethod
    def _import_project(path):
        """
        Import a katana project into the current session.

        :param path: The file path to import.
        :type path: str
        """
        root = NodegraphAPI.GetRootNode()
        return KatanaFile.Import(path, floatNodes=True, parentNode=root)

    def _create_node(self, node_type, path, sg_publish_data, path_parameter="file"):
        """
        Generic node creation method.
        """
        # if not os.path.exists(path):
        #     raise IOError(errno.ENOENT, "File not found on disk", path)

        entity = {
            "type": sg_publish_data.get("entity", {}).get("name", "UNKNOWN"),
            "name": sg_publish_data.get("name", "UNKNOWN")
        }

        # Create node
        root = NodegraphAPI.GetRootNode()
        node = NodegraphAPI.CreateNode(node_type, parent=root)

        # if node_type == 'ImageRead':
        #     path = entity["name"]  # typically %04d Katana

        node.getParameter(path_parameter).setValue(path, 0)
        node.setName(os.path.basename(path).split('.', 1)[0])
        return node

    def _create_texture_node(self, filename, name=None, parent=None):
        """Create texture input node for renderer, or just for viewer.

        Based off ``DEFAULT_RENDERER`` environment variable, either:

        - ``arnold``: Arnold Shading Node with file path for image
          ``filename``.
        - ``prman``: Prman Shading Node with file path for ``PxrTexture``.
        - Otherwise, a ``Material`` node with file path for texture
          ``viewerSurfaceShader``.

        :param filename: File path for image ``filename`` parameter.
        :type filename: str
        :keyword name: Name of the node.
        :type name: str
        :keyword parent: Parent ``GroupNode`` for our node.
        :type parent: GroupNode
        :return: The created Texture shading node.
        """
        parent = parent or NodegraphAPI.GetRootNode()
        renderer = os.environ['DEFAULT_RENDERER']

        if renderer == 'arnold':
            node = NodegraphAPI.CreateNode("ArnoldShadingNode", parent=parent)
            node.getParameter('nodeType').setValue(b'image', 0)
            node.checkDynamicParameters()
            filename_param = node.getParameter('parameters.filename')
            filename_param.getChild('value').setValue(filename, 0)
            filename_param.getChild('enable').setValue(True, 0)

        elif renderer == 'prman':
            node = NodegraphAPI.CreateNode("PrmanShadingNode", parent=parent)
            node.getParameter('nodeType').setValue(b'PxrTexture', 0)
            node.checkDynamicParameters()
            filename_param = node.getParameter('parameters.filename')
            filename_param.getChild('value').setValue(filename, 0)
            filename_param.getChild('enable').setValue(True, 0)

        else:
            warning = 'No idea how to import textures for renderer: "{}"'
            self.logger.warning(warning.format(renderer))
            self.logger.warning('Creating Katana viewerSurfaceShader')

            shader_type = 'viewerSurface'
            node = NodegraphAPI.CreateNode("Material", parent=parent)
            shader_param = node.addShaderType(shader_type)
            shader_param.getChild('enable').setValue(True, 0)
            shader_param.getChild('value').setValue(b'texture', 0)
            node.checkDynamicParameters()
            node.setShaderParam(shader_type, 'filename', filename)

        if name is not None:
            node.getParameter('name').setValue(name, 0)
        return node
