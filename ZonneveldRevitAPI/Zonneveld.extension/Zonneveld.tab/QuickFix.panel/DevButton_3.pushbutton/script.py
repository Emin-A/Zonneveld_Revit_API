# -*- coding: utf-8 -*-
__title__ = "Align \n View"
__doc__ = """Version = 1.0
Date    = 20.12.2024
________________________________________________________________
Description:

Align the current 3D view to the selected face in Revit.

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
from pyrevit import HOST_APP
from pyrevit import revit, DB, UI
from pyrevit import forms

# .NET Imports
# import clr

# clr.AddReference("RevitAPI")
# clr.AddReference("RevitServices")
# clr.AddReference("System")
# from RevitServices.Persistence import DocumentManager
# from System.Collections.Generic import List


# ╦  ╦╔═╗╦═╗╦╔═╗╔╗ ╦  ╔═╗╔═╗
# ╚╗╔╝╠═╣╠╦╝║╠═╣╠╩╗║  ║╣ ╚═╗
#  ╚╝ ╩ ╩╩╚═╩╩ ╩╚═╝╩═╝╚═╝╚═╝
# ==================================================

# Check for active document and view
# print("Checking environment...")
# doc = __revit__.ActiveUIDocument.Document if __revit__.ActiveUIDocument else None
# uidoc = __revit__.ActiveUIDocument
# curview = uidoc.ActiveView  # current view
# app = __revit__.Application

# ╔╦╗╔═╗╦╔╗╔
# ║║║╠═╣║║║║
# ╩ ╩╩ ╩╩╝╚╝
# ==================================================


def reorient():
    # Pick a face
    face = revit.pick_face()

    if face:
        with revit.Transaction("Orient to Selected Face"):
            # Calculate the normal vector
            if HOST_APP.is_newer_than(2015):
                normal_vec = face.ComputeNormal(DB.UV(0, 0))
            else:
                normal_vec = face.Normal

            # Create the base plane for sketchplane
            if HOST_APP.is_newer_than(2016):
                base_plane = DB.Plane.CreateByNormalAndOrigin(normal_vec, face.Origin)
            else:
                base_plane = DB.Plane(normal_vec, face.Origin)

            # Create the sketchplane
            sp = DB.SketchPlane.Create(revit.doc, base_plane)

            # Orient the 3D view to the face
            revit.active_view.OrientTo(normal_vec.Negate())
            # Set the sketchplane to active
            revit.uidoc.ActiveView.SketchPlane = sp

        # Refresh the active view
        revit.uidoc.RefreshActiveView()


# Get the current view
curview = revit.active_view

# Check if the current view is 3D
if isinstance(curview, DB.View3D):
    reorient()
else:
    forms.alert("You must be on a 3D view for this tool to work.")
