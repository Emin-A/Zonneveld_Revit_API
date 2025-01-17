# -*- coding: utf-8 -*-
__title__ = "Set Plane"
__doc__ = """Version = 1.0
Date    = 20.12.2024
________________________________________________________________
Description:

Set Work Plane to Selected Face.

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
from pyrevit import revit, DB, forms

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


def set_work_plane():
    try:
        # Prompt user to select a face
        face = revit.pick_face()
        if not face:
            forms.alert(
                "No face selected. Operation cancelled.", title="Set Work Plane"
            )
            return

        # Get current document and view
        doc = revit.doc
        uidoc = revit.uidoc
        curview = revit.active_view

        # Ensure the view is a 3D view
        if not isinstance(curview, DB.View3D):
            forms.alert(
                "Work plane can only be set in a 3D view.", title="Set Work Plane"
            )
            return

        # Compute normal vector and create work plane
        if HOST_APP.is_newer_than(2015):
            normal_vec = face.ComputeNormal(UV(0, 0))
            plane = DB.Plane.CreateByNormalAndOrigin(normal_vec, face.Origin)
        else:
            plane = DB.Plane(face.Normal, face.Origin)

        # Create and Assign sketch plane
        with revit.Transaction("Set Work Plane"):
            sketch_plane = DB.SketchPlane.Create(doc, plane)
            curview.SketchPlane = sketch_plane
            uidoc.RefreshActiveView()

        forms.alert(
            "Work plane successfully set to selected face.", title="Set Work Plane"
        )

    except Exception as e:
        forms.alert("An error occurred: {0}".format(e), title="Set Work Plane")


# Execute the script
set_work_plane()
