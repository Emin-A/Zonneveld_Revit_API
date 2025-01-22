# -*- coding: utf-8 -*-
__title__ = "Allow Join"
__doc__ = """Version = 1.0
Date    = 20.12.2024
________________________________________________________________
Description:

Enable join for selected structural framing elements.

________________________________________________________________
How-To:

1. [Hold ALT + CLICK] on the button to open its source folder.
You will be able to override this placeholder.

2. Automate Your Boring Work ;)

________________________________________________________________
TODO:
[FEATURE] - Describe Your ToDo Tasks Here
________________________________________________________________
Last Updates:
- [15.06.2024] v1.0 Change Description
- [10.06.2024] v0.5 Change Description
- [05.06.2024] v0.1 Change Description 
________________________________________________________________
Author: Emin Avdovic"""

# ╦╔╦╗╔═╗╔═╗╦═╗╔╦╗╔═╗
# ║║║║╠═╝║ ║╠╦╝ ║ ╚═╗
# ╩╩ ╩╩  ╚═╝╩╚═ ╩ ╚═╝
# ==================================================
from Autodesk.Revit.DB import *
from Autodesk.Revit.UI import *
from pyrevit import forms
import sys

# .NET Imports
import clr
import time

clr.AddReference("RevitAPI")
clr.AddReference("RevitAPIUI")

# ╦  ╦╔═╗╦═╗╦╔═╗╔╗ ╦  ╔═╗╔═╗
# ╚╗╔╝╠═╣╠╦╝║╠═╣╠╩╗║  ║╣ ╚═╗
#  ╚╝ ╩ ╩╩╚═╩╩ ╩╚═╝╩═╝╚═╝╚═╝
# ==================================================
# uidoc = __revit__.ActiveUIDocument
# doc = __revit__.ActiveUIDocument.Document  # type:Document

# Get the current Revit document and UI document
uiapp = __revit__.ActiveUIDocument.Application
uidoc = __revit__.ActiveUIDocument
doc = uidoc.Document

# Use UIApplication for UI-level commands
uiapp = UIApplication(doc.Application)

# ╔╦╗╔═╗╦╔╗╔
# ║║║╠═╣║║║║
# ╩ ╩╩ ╩╩╝╚╝
# ==================================================
# Validate selection
selection_ids = uidoc.Selection.GetElementIds()
if not selection_ids:
    forms.alert("Please select structural beams or columns.")
    sys.exit()

# Get the selected elements
selected_elements = [doc.GetElement(el_id) for el_id in selection_ids]

# Filter only structural framing elements (beams/columns)
framing_elements = []
for e in selected_elements:
    if e.Category and e.Category.Id in [
        ElementId(BuiltInCategory.OST_StructuralFraming),
        ElementId(BuiltInCategory.OST_StructuralColumns),
    ]:
        framing_elements.append(e)

if not framing_elements:
    forms.alert("No structural beams or columns selected.")
    sys.exit()

try:
    # Ensure the selected elements remain active before running the command
    uidoc.Selection.SetElementIds(selection_ids)

    # Add a slight delay to allow Revit to process the selection
    time.sleep(0.5)

    # Inform the user
    forms.alert(
        "Beam/Column Join tool is now active. Click on a beam to adjust the joins."
    )

    # Run the command interactively by selecting the command from Revit's UI
    command_id = RevitCommandId.LookupPostableCommandId(PostableCommand.CutGeometry)
    uiapp.PostCommand(command_id)

    print(
        "Beam/Column Join tool has been invoked. Click on a beam to adjust the joins."
    )

except Exception as e:
    print("Failed to invoke Beam/Column Join tool: {0}".format(e))
