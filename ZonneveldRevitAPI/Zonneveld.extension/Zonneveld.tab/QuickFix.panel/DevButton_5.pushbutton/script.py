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
# app = __revit__.Application
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
        TaskDialog.Show(
            "Selection Error",
            "Please select at least two analytical elements to join/unjoin.",
        )
        return None

    selected_elements = [doc.GetElement(el_id) for el_id in selection]
    analytical_elements = []

    print("Selected Elements:")
    for el in selected_elements:
        category_name = el.Category.Name if el.Category else "None"
        print("Element ID:", el.Id, "Category:", category_name)

        if el.Category and el.Category.Id.IntegerValue in [
            int(cat) for cat in ANALYTICAL_CATEGORIES
        ]:
            analytical_elements.append(el)
        else:
            print("Ignored element:", el.Id, "Category:", category_name)

    if len(analytical_elements) < 2:
        TaskDialog.Show(
            "Selection Error",
            "Please select at least two valid analytical walls, beams, or columns.",
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

            if not analytical_model1 or not analytical_model2:
                print(
                    "Skipping elements due to missing analytical model:",
                    elem1.Id,
                    elem2.Id,
                )
                continue

            print("Processing elements:", elem1.Id, elem2.Id)

            try:
                if analytical_model1.HasAnalyticalAssociation(analytical_model2):
                    analytical_model1.RemoveAnalyticalAssociation(analytical_model2)
                    analytical_model2.RemoveAnalyticalAssociation(analytical_model1)
                    unjoined_elements.append((elem1.Id, elem2.Id))
                    print("Unjoined:", elem1.Id, elem2.Id)
                else:
                    analytical_model1.AddAnalyticalAssociation(analytical_model2)
                    analytical_model2.AddAnalyticalAssociation(analytical_model1)
                    joined_elements.append((elem1.Id, elem2.Id))
                    print("Joined:", elem1.Id, elem2.Id)

            except Exception as e:
                failed_elements.append((elem1.Id, elem2.Id))
                print("Error processing analytical join:", elem1.Id, elem2.Id, str(e))

    t.Commit()

    TaskDialog.Show(
        "Join/Unjoin Analytical Summary",
        "Operation completed:\n"
        + str(len(joined_elements))
        + " elements joined.\n"
        + str(len(unjoined_elements))
        + " elements unjoined.\n"
        + str(len(failed_elements))
        + " elements failed to process.",
    )
