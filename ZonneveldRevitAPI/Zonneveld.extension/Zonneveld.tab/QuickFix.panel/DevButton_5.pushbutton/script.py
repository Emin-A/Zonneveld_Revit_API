# -*- coding: utf-8 -*-
__title__ = "Join/Unjoin \n Analytical"
__doc__ = """Version = 1.0
Date    = 20.12.2024
________________________________________________________________
Description:

Enable join/unjoin functionality for analytical elements in Revit.
________________________________________________________________
Author: Emin Avdovic"""

# ╦╔╦╗╔═╗╔═╗╦═╗╔╦╗╔═╗
# ║║║║╠═╝║ ║╠╦╝ ║ ╚═╗
# ╩╩ ╩╩  ╚═╝╩╚═ ╩ ╚═╝
# ==================================================
from Autodesk.Revit.DB import *
from Autodesk.Revit.UI import TaskDialog

# .NET Imports
import clr

clr.AddReference("RevitAPI")
clr.AddReference("RevitAPIUI")


# ╦  ╦╔═╗╦═╗╦╔═╗╔╗ ╦  ╔═╗╔═╗
# ╚╗╔╝╠═╣╠╦╝║╠═╣╠╩╗║  ║╣ ╚═╗
#  ╚╝ ╩ ╩╩╚═╩╩ ╩╚═╝╩═╝╚═╝╚═╝
# ==================================================
# Get Revit document and UI document
uidoc = __revit__.ActiveUIDocument
doc = uidoc.Document

# ╔╦╗╔═╗╦╔╗╔
# ║║║╠═╣║║║║
# ╩ ╩╩ ╩╩╝╚╝
# ==================================================

# Supported analytical categories
ANALYTICAL_CATEGORIES = [
    BuiltInCategory.OST_WallAnalytical,  # Analytical Walls
    BuiltInCategory.OST_BeamAnalytical,  # Analytical Beams
    BuiltInCategory.OST_ColumnAnalytical,  # Analytical Columns
]


def select_analytical_elements():
    """Prompt user to select analytical elements and filter them."""
    selection = uidoc.Selection.GetElementIds()

    if len(selection) < 2:
        print(
            "Selection Error: Please select at least two analytical elements to join/unjoin."
        )
        return None

    selected_elements = [doc.GetElement(el_id) for el_id in selection]
    analytical_elements = []

    for el in selected_elements:
        # Check if the element is in a supported category
        if el.Category and el.Category.Id.IntegerValue in [
            int(cat) for cat in ANALYTICAL_CATEGORIES
        ]:
            analytical_model = (
                el.GetAnalyticalModel() if hasattr(el, "GetAnalyticalModel") else None
            )

            # Log detailed information for debugging
            print(
                "Selected Analytical Element:",
                el.Id,
                el.Category.Name if el.Category else "No Category",
                "Analytical Model:",
                "Exists" if analytical_model else "None",
                "Analyze As:",
                (
                    el.LookupParameter("Analyze As").AsString()
                    if el.LookupParameter("Analyze As")
                    else "Not Set"
                ),
                "Enable Analytical Model:",
                (
                    el.LookupParameter("Enable Analytical Model").AsString()
                    if el.LookupParameter("Enable Analytical Model")
                    else "Not Set"
                ),
            )

            if analytical_model:
                analytical_elements.append(el)
            else:
                print(
                    "Invalid analytical element:",
                    el.Id,
                    el.Category.Name,
                    "Analytical Model: None",
                )
        else:
            print(
                "Invalid analytical element:",
                el.Id,
                el.Category.Name if el.Category else "No Category",
                "Analytical Model: None",
            )

    if not analytical_elements:
        print(
            "No valid analytical elements selected. Ensure the elements have analytical models enabled in Revit."
        )
        return None

    return analytical_elements


def process_analytical_join_unjoin(elements):
    """Join or unjoin analytical elements."""
    joined_elements = []
    unjoined_elements = []
    failed_elements = []

    t = Transaction(doc, "Join/Unjoin Analytical Elements")
    t.Start()

    for i in range(len(elements)):
        for j in range(i + 1, len(elements)):
            elem1 = elements[i]
            elem2 = elements[j]

            # Get analytical models
            analytical_model1 = elem1.GetAnalyticalModel()
            analytical_model2 = elem2.GetAnalyticalModel()

            if analytical_model1 and analytical_model2:
                try:
                    # Add or remove association between analytical models
                    if analytical_model1.HasAnalyticalAssociation(analytical_model2):
                        analytical_model1.RemoveAnalyticalAssociation(analytical_model2)
                        unjoined_elements.append((elem1.Id, elem2.Id))
                    else:
                        analytical_model1.AddAnalyticalAssociation(analytical_model2)
                        joined_elements.append((elem1.Id, elem2.Id))
                except Exception as e:
                    failed_elements.append((elem1.Id, elem2.Id))
                    print(
                        "Error processing analytical join:", elem1.Id, elem2.Id, str(e)
                    )
            else:
                failed_elements.append((elem1.Id, elem2.Id))
                print("Invalid analytical models for elements:", elem1.Id, elem2.Id)

    t.Commit()

    # Display results in console
    print(
        "Operation completed:\n"
        + str(len(joined_elements))
        + " elements joined.\n"
        + str(len(unjoined_elements))
        + " elements unjoined.\n"
        + str(len(failed_elements))
        + " elements failed to process."
    )


# Main Execution
selection = select_analytical_elements()

if selection:
    process_analytical_join_unjoin(selection)
else:
    print("No valid analytical elements selected.")
