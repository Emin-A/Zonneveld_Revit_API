# -*- coding: utf-8 -*-
__title__ = "Allow Framing"
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
from RevitServices.Persistence import DocumentManager

# .NET Imports
import clr

clr.AddReference("System")
clr.AddReference("RevitServices")
from System.Collections.Generic import List


# ╦  ╦╔═╗╦═╗╦╔═╗╔╗ ╦  ╔═╗╔═╗
# ╚╗╔╝╠═╣╠╦╝║╠═╣╠╩╗║  ║╣ ╚═╗
#  ╚╝ ╩ ╩╩╚═╩╩ ╩╚═╝╩═╝╚═╝╚═╝
# ==================================================
# app = __revit__.Application
# uidoc = __revit__.ActiveUIDocument
# doc = __revit__.ActiveUIDocument.Document  # type:Document

# Get the active document
doc = DocumentManager.Instance.CurrentDBDocument
uidoc = DocumentManager.Instance.CurrentUIApplication.ActiveUIDocument


# ╔╦╗╔═╗╦╔╗╔
# ║║║╠═╣║║║║
# ╩ ╩╩ ╩╩╝╚╝
# ==================================================

# Collect selected elements
selected_ids = uidoc.Selection.GetElementIds()
if not selected_ids:
    print("No elements selected. Please select structural framing elements.")
    sys.exit()

selected_elements = [doc.GetElement(el_id) for el_id in selected_ids]

# Filter for structural framing elements
framing_elements = [
    e
    for e in selected_elements
    if e.Category and e.Category.Id == ElementId(BuiltInCategory.OST_StructuralFraming)
]

if not framing_elements:
    print("No structural framing elements selected. Please select valid elements.")
    sys.exit()

# Enable join for all framing elements
t = Transaction(doc, "Enable Join for Structural Framing")
t.Start()

for element in framing_elements:
    try:
        StructuralFramingUtils.AllowJoinAtEnd(element, 0)  # Start end
        StructuralFramingUtils.AllowJoinAtEnd(element, 1)  # End end
        print("Join enabled for element with ID: {0}".format(element.Id))
    except Exception as e:
        print(
            "Failed to enable join for element with ID {0}: {1}".format(element.Id, e)
        )

t.Commit()
print("Join operation completed successfully")

# ==================================================
