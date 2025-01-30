# -*- coding: utf-8 -*-
__title__ = "Align \n Box"
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

clr.AddReference("RevitAPI")
clr.AddReference("RevitServices")
from System.Collections.Generic import List


# ╦  ╦╔═╗╦═╗╦╔═╗╔╗ ╦  ╔═╗╔═╗
# ╚╗╔╝╠═╣╠╦╝║╠═╣╠╩╗║  ║╣ ╚═╗
#  ╚╝ ╩ ╩╩╚═╩╩ ╩╚═╝╩═╝╚═╝╚═╝
# ==================================================
app = __revit__.Application
# uidoc = __revit__.ActiveUIDocument
# doc = __revit__.ActiveUIDocument.Document  # type:Document
uidoc = revit.uidoc
doc = revit.doc

# ╔╦╗╔═╗╦╔╗╔
# ║║║╠═╣║║║║
# ╩ ╩╩ ╩╩╝╚╝
# ==================================================
# Debug toggle
DEBUG = False


def debug_log(message):
    """Log debug messages if DEBUG is enabled."""
    if DEBUG:
        print(message)


def orient_section_box(view):
    try:
        # Prompt user to pick a face
        face_reference = uidoc.Selection.PickObject(
            UI.Selection.ObjectType.Face, "Select a face to align section box."
        )
        selected_face = doc.GetElement(
            face_reference.ElementId
        ).GetGeometryObjectFromReference(face_reference)

        if not selected_face:
            raise Exception("Selected object is not a valid face.")

        # Get the section box and face normal
        section_box = view.GetSectionBox()
        face_normal = selected_face.ComputeNormal(UV(0, 0)).Normalize()
        box_normal = section_box.Transform.Basis[0].Normalize()

        debug_log("Face Normal: {0}".format(face_normal))
        debug_log("Section Box Normal: {0}".format(box_normal))

        # Calculate rotation angle and axis
        angle = face_normal.AngleTo(box_normal)
        rotation_axis = XYZ(0, 0, 1.0)  # Z-axis rotation

        box_center = XYZ(
            (section_box.Min.X + section_box.Max.X) / 2,
            (section_box.Min.Y + section_box.Max.Y) / 2,
            (section_box.Min.Z + section_box.Max.Z) / 2,
        )

        debug_log("Angle to rotate: {0} radians".format(angle))

        # Determine rotation transformation
        rotation = Transform.CreateRotationAtPoint(rotation_axis, angle, box_center)

        # Apply the rotation to the section box
        new_transform = section_box.Transform.Multiply(rotation)
        section_box.Transform = new_transform

        # Commit the changes in a transaction
        t = Transaction(doc, "Orient Section Box to Face")
        t.Start()
        view.SetSectionBox(section_box)
        t.Commit()

        debug_log("Section box successfully oriented to the selected face.")

    except Exception as e:
        debug_log("Error: {0}".format(e))


# Get the current view
curview = revit.active_view

# Validate the view and section box status
if isinstance(curview, View3D):
    if curview.IsSectionBoxActive:
        orient_section_box(curview)
    else:
        debug_log("The section box for the current 3D view is not active.")
else:
    debug_log("You must be in a 3D view for this tool to work.")
