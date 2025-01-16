# -*- coding: utf-8 -*-
__title__ = "Orient Section Box to Face"
__doc__ = """Version = 1.0
Date    = 20.12.2024
________________________________________________________________
Description:

Aligns the section box of the current 3D view to the selected face.

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
from pyrevit.framework import Math
from pyrevit import revit, DB, UI
from pyrevit import forms

# .NET Imports
import clr

clr.AddReference("System")
from System.Collections.Generic import List


# ╦  ╦╔═╗╦═╗╦╔═╗╔╗ ╦  ╔═╗╔═╗
# ╚╗╔╝╠═╣╠╦╝║╠═╣╠╩╗║  ║╣ ╚═╗
#  ╚╝ ╩ ╩╩╚═╩╩ ╩╚═╝╩═╝╚═╝╚═╝
# ==================================================
app = __revit__.Application
uidoc = __revit__.ActiveUIDocument
doc = __revit__.ActiveUIDocument.Document  # type:Document


# ╔╦╗╔═╗╦╔╗╔
# ║║║╠═╣║║║║
# ╩ ╩╩ ╩╩╝╚╝
# ==================================================
def orient_section_box(view):
    try:
        # Prompt user to pick a face
        face = revit.pick_face()

        # Get the section box and face normal
        box = view.GetSectionBox()
        norm = face.ComputeNormal(DB.UV(0, 0)).Normalize()
        box_normal = box.Transform.Basis[0].Normalize()

        # Calculate rotation angle and axis
        angle = norm.AngleTo(box_normal)
        axis = DB.XYZ(0, 0, 1.0)
        origin = DB.XYZ(
            box.Min.X + (box.Max.X - box.Min.X) / 2,
            box.Min.Y + (box.Max.Y - box.Min.Y) / 2,
            0.0,
        )

        # Determine rotation direction
        if norm.Y * box_normal.X < 0:
            rotation = DB.Transform.CreateRotationAtPoint(
                axis, Math.PI / 2 - angle, origin
            )
        else:
            rotation = DB.Transform.CreateRotationAtPoint(axis, angle, origin)

        # Apply the rotation to the section box
        box.Transform = box.Transform.Multiply(rotation)

        # Commit the changes
        with revit.Transaction("Orient Section Box to Face"):
            view.SetSectionBox(box)
            revit.uidoc.RefreshActiveView()

        print("Section box successfully oriented to the selected face.")

    except Exception as e:
        forms.alert("An error occurred: {}".format(e), title="Error")


# Get the current view
curview = revit.active_view

# Validate the view and section box status
if isinstance(curview, DB.View3D):
    if curview.IsSectionBoxActive:
        orient_section_box(curview)
    else:
        forms.alert(
            "The section box for the current 3D view is not active.",
            title="Section Box Inactive",
        )
else:
    forms.alert("You must be in a 3D view for this tool to work.", title="Invalid View")
