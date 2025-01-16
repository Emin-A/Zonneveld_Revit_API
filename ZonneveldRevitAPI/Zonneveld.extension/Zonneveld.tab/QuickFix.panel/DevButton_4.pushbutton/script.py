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


# ╔╦╗╔═╗╦╔╗╔
# ║║║╠═╣║║║║
# ╩ ╩╩ ╩╩╝╚╝
# ==================================================

# Conversion factor: Feet to mm
FEET_TO_MM = 304.8
MM_TO_FEET = 1 / FEET_TO_MM


# Helper function to get beam endpounts
def get_endpoints(element):
    location = element.Location
    if isinstance(location, LocationCurve):
        curve = location.Curve
        return curve.GetEndPoint(0), curve.GetEndPoint(1)
    return None, None


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

# Detect and connect beams
t = Transaction(doc, "Allow and Connect Framing")
t.Start()

threshold = 10 * MM_TO_FEET  # Proximity threshold in mm converted to feet
for i, element1 in enumerate(framing_elements):
    endpoints1 = get_endpoints(element1)

    for j, element2 in enumerate(framing_elements):
        if i >= j:
            continue  # Avoid redundant comparisons

        endpoints2 = get_endpoints(element2)

        # Check proximity of endpoints
        for idx1, endpoint1 in enumerate(endpoints1):
            for idx2, endpoint2 in enumerate(endpoints2):
                distance = endpoint1.DistanceTo(endpoint2)
                print(
                    "Checking distance between {} and {}: {:.2f} mm".format(
                        element1.Id, element2.Id, distance * FEET_TO_MM
                    )
                )
                if distance < threshold:  # Threshold for proximity
                    # Adjust endpoints to connect
                    location1 = element1.Location
                    location2 = element2.Location
                    if isinstance(location1, LocationCurve) and isinstance(
                        location2, LocationCurve
                    ):
                        curve1 = location1.Curve
                        curve2 = location2.Curve

                        # Debug: Log current endpoint coordinates in mm
                        print(
                            "Before adjustment: Beam 1 endpoints: {} mm, {} mm".format(
                                [pt * FEET_TO_MM for pt in curve1.GetEndPoint(0)],
                                [pt * FEET_TO_MM for pt in curve1.GetEndPoint(1)],
                            )
                        )
                        print(
                            "Before adjustment: Beam 2 endpoints: {} mm, {} mm".format(
                                [pt * FEET_TO_MM for pt in curve2.GetEndPoint(0)],
                                [pt * FEET_TO_MM for pt in curve2.GetEndPoint(1)],
                            )
                        )

                        if idx1 == 0:
                            new_curve1 = Line.CreateBound(
                                endpoint2, curve1.GetEndPoint(1)
                            )
                        else:
                            new_curve1 = Line.CreateBound(
                                curve1.GetEndPoint(0), endpoint2
                            )

                        if idx2 == 0:
                            new_curve2 = Line.CreateBound(
                                endpoint1, curve2.GetEndPoint(1)
                            )
                        else:
                            new_curve2 = Line.CreateBound(
                                curve2.GetEndPoint(0), endpoint1
                            )

                        # Update beam geometry
                        location1.Curve = new_curve1
                        location2.Curve = new_curve2

                        # Debug: Log updated endpoint coordinates in mm
                        print(
                            "After adjustment: Beam 1 endpoints: {} mm, {} mm".format(
                                [pt * FEET_TO_MM for pt in new_curve1.GetEndPoint(0)],
                                [pt * FEET_TO_MM for pt in new_curve1.GetEndPoint(1)],
                            )
                        )
                        print(
                            "After adjustment: Beam 2 endpoints: {} mm, {} mm".format(
                                [pt * FEET_TO_MM for pt in new_curve2.GetEndPoint(0)],
                                [pt * FEET_TO_MM for pt in new_curve2.GetEndPoint(1)],
                            )
                        )

                        # Enable join at the adjusted endpoints
                        StructuralFramingUtils.AllowJoinAtEnd(element1, idx1)
                        StructuralFramingUtils.AllowJoinAtEnd(element2, idx2)

                        print(
                            "Connected beams: {} and {}".format(
                                element1.Id, element2.Id
                            )
                        )

# Force Revit to regenerate the document geometry
doc.Regenerate()

t.Commit()
print("Operation completed successfully. All possible connections were made.")
