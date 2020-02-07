Installation
============

.. warning::
    **CURRENTLY INCOMPLETE**

    Ideally, this would be as informative as the
    excellent `tk-natron's README`_


After `taking over the project configurations`_ (`see also here`_):

1. Go to where you installed the project configurations.
2. Copy/integrate the ``yml`` files in the ``config`` folder into the
   ``config`` folder.

   Relative to the below picture:

   - ``config/core/templates.yml`` goes into "Templates" ``templates.yml``
   - ``config/env/*`` goes into "Artist Environments" folders

   .. image:: https://raw.githubusercontent.com/shotgunsoftware/developer.shotgunsoftware.com/846e31710bd386715a3330511fe8607786081424/docs/images/toolkit/learning-resources/tutorial/image_11.png
      :width: 50 %

3. Cache the updated the apps/framework/engine locations using the
   ``tank cache_apps`` command in the project configurations folder.

   Relative to the above image, it is the "Tank command" executable/program.

   .. code-block:: bash

       ./tank cache_apps


.. _`taking over the project configurations`: https://developer.shotgunsoftware.com/cb8926fc/?title=Pipeline+Tutorial#taking-over-the-project-config
.. _`see also here`: https://support.shotgunsoftware.com/hc/en-us/articles/115000067493-Integrations-Admin-Guide#Taking%20over%20a%20Pipeline%20Configuration
.. _`tk-natron's README`: https://github.com/diegogarciahuerta/tk-natron/blob/master/README.md
