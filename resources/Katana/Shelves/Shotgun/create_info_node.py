"""SCRATCH PAD for making a node exposing key/value of current context idea."""

'''
from Katana import NodegraphAPI
import errno
import sgtk

try:
    import sgtk
except ImportError:
    raise EnvironmentError(errno.ENOTCONN, 'Not connected to Shotgun')

engine = sgtk.platform.current_engine()
tank, shotgun, context =  engine.sgtk, engine.shotgun, engine.context

context.user
context.source_entity
context.step
# shotgun.find_one(self, entity_type, filters, fields=None, order=None, filter_operator=None, retired_only=False, include_archived_projects=True, additional_filter_presets=None)
shotgun.find_one(context.step['type'], [['id', 'is', context.step['id']]], fields=['sg_folder_name'] )['sg_folder_name']


# https://learn.foundry.com/katana/dev-guide/ArgsFiles/WidgetsAndHints.html?highlight=scriptbutton#common-hints
# https://learn.foundry.com/katana/dev-guide/Scripting/WorkingWithNodes/Parameters/ParameterHints.html
# https://learn.foundry.com/katana/dev-guide/ParameterExpressions/PythonExpressions.html

dot = NodegraphAPI.GetNode('Dot')
root = dot.getParameters()
root.getXML()
dot.getParameter('user/newParameter')
sgg = root.createChildGroup('Shotgun')
sgg.setName('Context')
cstr = sgg.createChildString('Department Folder', '')
cstr.setHintString(repr({'readOnly': True}))
cstr.setValue(shotgun.find_one(
    context.step['type'],
    [['id', 'is', context.step['id']]],
    fields=['sg_folder_name']
)['sg_folder_name'], 0)
'''