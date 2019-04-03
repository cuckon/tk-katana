=========
tk-katana
=========

.. image:: https://img.shields.io/pypi/v/tk_katana.svg
        :target: https://pypi.python.org/pypi/tk_katana

.. image:: https://img.shields.io/travis/wwfxuk/tk_katana.svg
        :target: https://travis-ci.org/wwfxuk/tk_katana

.. image:: https://wwfxuk.readthedocs.io/projects/tk-katana/badge/?version=latest
        :target: https://wwfxuk.readthedocs.io/projects/tk-katana/en/latest/?badge=latest
        :alt: Documentation Status


Documentation: https://wwfxuk.readthedocs.io/projects/tk-katana

A Shotgun Engine for Katana

This engine provides Shotgun Toolkit integration for The Foundry's Katana.

WWFX UK
-------

Forked from `robblau's v0.1.0`_ to hopefully make it production capable 
again for:

* Shotgun 8 and above
* Katana 3.0 
    * 3.1 uses PyQt5, yet to decide on how to go about it


Installation
````````````

**CURRENTLY INCOMPLETE**. Ideally, this would be as informative as the 
excellent `tk-natron`_'s ``README``

After `taking over the project configurations`_

1. Locate where you installed the project configurations
2. Add this section to ``config/env/includes/engine_locations.yml``
    
    .. code-block:: yml
    
        # Katana
        engines.tk-katana.location:
        type: git
        path: https://github.com/wwfxuk/tk-katana.git
        branch: master

3. Then, create ``config/env/includes/settings/tk-katana.yml``, placing this 
   inside:
    
    .. code-block:: yml
    
        includes:
        # - ../app_locations.yml
        - ../engine_locations.yml
        # - ./tk-multi-loader2.yml
        # - ./tk-multi-publish2.yml
        # - ./tk-multi-screeningroom.yml
        # - ./tk-multi-shotgunpanel.yml
        # - ./tk-multi-snapshot.yml
        - ./tk-multi-workfiles2.yml    
        
        # shot_step
        settings.tk-katana.shot_step:
        apps:
            # tk-multi-about:
            #   location: "@apps.tk-multi-about.location"
            # tk-multi-breakdown:
            #   location: "@apps.tk-multi-breakdown.location"
            # tk-multi-setframerange:
            #   location: "@apps.tk-multi-setframerange.location"
            # tk-multi-loader2: "@settings.tk-multi-loader2.katana"
            # tk-multi-publish2: "@settings.tk-multi-publish2.katana.shot_step"
            # tk-multi-screeningroom: "@settings.tk-multi-screeningroom.rv"
            # tk-multi-shotgunpanel: "@settings.tk-multi-shotgunpanel.katana"
            # tk-multi-snapshot: "@settings.tk-multi-snapshot.katana.shot_step"
            tk-multi-workfiles2: "@settings.tk-multi-workfiles2.katana.shot_step"
        menu_favourites:
        # - {app_instance: tk-multi-workfiles2, name: File Open...}
        # - {app_instance: tk-multi-snapshot, name: Snapshot...}
        - {app_instance: tk-multi-workfiles2, name: File Save...}
        # - {app_instance: tk-multi-publish2, name: Publish...}
        location: '@engines.tk-katana.location'
    
4. Update the apps using the ``tank`` command in the project configurations 
   folder:
   
   .. code-block:: bash
   
       ./tank cache_apps
   

Credits
-------

* It has been generously made public by Light Chaser Animation with help from 
  The Foundry.
  
  * Thanks to `Ying Jie Kong (Jerry)`_ at Light Chaser and `Sam Saxon`_ at 
    The Foundry for their contributions
  * Thanks to `Rob Blau`_ for initial release `v0.1.0`_

* `Jeremy Boissinot`_ and `Kevin Sallee`_ at RodeoFX for patches up to `v0.1.1_rdo3`_
* `AppCommand` changes by `Gael-Honorez-sb`_
* `Diego Garcia Huerta`_ for 

This package was created with Cookiecutter_ and the `audreyr/cookiecutter-pypackage`_ project template.

.. _`audreyr/cookiecutter-pypackage`: https://github.com/audreyr/cookiecutter-pypackage
.. _`Diego Garcia Huerta`: https://github.com/diegogarciahuerta
.. _`Gael-Honorez-sb`: https://github.com/Gael-Honorez-sb/tk-katana/commit/e06ab6b6b38960efbbdb18dc73b139aae278b040
.. _`Jeremy Boissinot`: http://jboissinot.com
.. _`Kevin Sallee`: https://github.com/kevinsallee
.. _`Rob Blau`: https://github.com/robblau
.. _`robblau's v0.1.0`: https://github.com/robblau/tk-katana/tree/b9cca6e4009ff84870d6e691c2b25e818dc99d1a
.. _`robblau's v0.1.0`: https://github.com/robblau/tk-katana/tree/b9cca6e4009ff84870d6e691c2b25e818dc99d1a
.. _`Sam Saxon`: https://github.com/sam-saxon
.. _`taking over the project configurations`: https://support.shotgunsoftware.com/hc/en-us/articles/219039938-Pipeline-Tutorial#Taking%20Over%20the%20Project%20Config
.. _`tk-natron`: https://github.com/diegogarciahuerta/tk-natron
.. _`v0.1.1_rdo3`: https://github.com/rodeofx/tk-katana/commit/0ddace4f285ff7f9642c165d3d225754584bbaf9
.. _`Ying Jie Kong (Jerry)`: https://github.com/JerryKon
.. _Cookiecutter: https://github.com/audreyr/cookiecutter