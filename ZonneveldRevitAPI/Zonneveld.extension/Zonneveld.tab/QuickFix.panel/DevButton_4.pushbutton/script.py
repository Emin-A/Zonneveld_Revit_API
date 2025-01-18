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
from Autodesk.Revit.DB.Structure import StructuralFramingUtils
from pyrevit import forms

# .NET Imports
import clr

clr.AddReference("RevitAPI")
clr.AddReference("RevitAPIUI")

# ╦  ╦╔═╗╦═╗╦╔═╗╔╗ ╦  ╔═╗╔═╗
# ╚╗╔╝╠═╣╠╦╝║╠═╣╠╩╗║  ║╣ ╚═╗
#  ╚╝ ╩ ╩╩╚═╩╩ ╩╚═╝╩═╝╚═╝╚═╝
# ==================================================
# uidoc = __revit__.ActiveUIDocument
# doc = __revit__.ActiveUIDocument.Document  # type:Document

# Get the current Revit document and UI document
app = __revit__.Application
doc = __revit__.ActiveUIDocument.Document
uidoc = __revit__.ActiveUIDocument
selection_ids = uidoc.Selection.GetElementIds()

# Conversion factors
FEET_TO_MM = 304.8
MM_TO_FEET = 1 / FEET_TO_MM

# ╔╦╗╔═╗╦╔╗╔
# ║║║╠═╣║║║║
# ╩ ╩╩ ╩╩╝╚╝
# ==================================================
# Validate selection
if not selection_ids:
    forms.alert(
        "No elements selected. Please select structural framing elements.",
        exitscript=True,
    )

# Filter for structural framing elements
selected_elements = [doc.GetElement(el_id) for el_id in selection_ids]
framing_elements = [
    e
    for e in selected_elements
    if e.Category and e.Category.Id == ElementId(BuiltInCategory.OST_StructuralFraming)
]

if not framing_elements:
    forms.alert(
        "No structural framing elements selected. Operation cancelled.", exitscript=True
    )

# Prompt user for join type
join_options = ["Butt", "Miter", "Square Off"]
selected_join = forms.ask_for_one_item(
    join_options,
    default="Butt",
    prompt="Select the join type to apply:",
    title="Join Options",
)

if not selected_join:
    forms.alert("No join type selected. Operation cancelled.", exitscript=True)

# Start transaction
t = Transaction(doc, "Apply Beam Join Options")
t.Start()

joined_count = 0

for i, element1 in enumerate(framing_elements):
    for j, element2 in enumerate(framing_elements):
        if i >= j:
            continue

        try:
            # Attempt to join geometry
            if not JoinGeometryUtils.AreElementsJoined(doc, element1, element2):
                JoinGeometryUtils.JoinGeometry(doc, element1, element2)
                joined_count += 1
                print(
                    "Successfully joined beams: {0} and {1}".format(
                        element1.Id, element2.Id
                    )
                )

                # Apply join type logic (placeholder for specific behaviors)
                if selected_join == "Butt":
                    print(
                        "Applied 'Butt' join to beams: {0} and {1}".format(
                            element1.Id, element2.Id
                        )
                    )
                elif selected_join == "Miter":
                    print(
                        "Applied 'Miter' join to beams: {0} and {1}".format(
                            element1.Id, element2.Id
                        )
                    )
                elif selected_join == "Square Off":
                    print(
                        "Applied 'Square Off' join to beams: {0} and {1}".format(
                            element1.Id, element2.Id
                        )
                    )
            else:
                print(
                    "Beams already joined: {0} and {1}".format(element1.Id, element2.Id)
                )

        except Exception as e:
            print(
                "Failed to join beams {0} and {1}: {2}".format(
                    element1.Id, element2.Id, e
                )
            )

# Commit transaction
t.Commit()

# Feedback
if joined_count > 0:
    print("Operation completed successfully. {0} joins made.".format(joined_count))
else:
    print("No joins were made. Ensure beams are intersecting or close enough.")
