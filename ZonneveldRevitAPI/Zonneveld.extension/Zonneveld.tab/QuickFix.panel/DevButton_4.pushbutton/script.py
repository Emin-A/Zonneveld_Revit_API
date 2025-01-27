# -*- coding: utf-8 -*-
__title__ = "Join/Unjoin \n Geometry"
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
from Autodesk.Revit.DB import (
    FilteredElementCollector,
    BuiltInCategory,
    BuiltInParameter,
    Element,
    ElementId,
    Transaction,
    WorksetKind,
    JoinGeometryUtils,
    ElementCategoryFilter,
)
from Autodesk.Revit.DB import Transaction
from Autodesk.Revit.UI import *
from Autodesk.Revit.UI import TaskDialog
from pyrevit import forms
from System.Windows.Forms import MessageBox, MessageBoxButtons, MessageBoxIcon


# .NET Imports
import sys
import time
import clr

clr.AddReference("System")
clr.AddReference("RevitAPI")
clr.AddReference("RevitAPIUI")
clr.AddReference("System.Windows.Forms")

# ╦  ╦╔═╗╦═╗╦╔═╗╔╗ ╦  ╔═╗╔═╗
# ╚╗╔╝╠═╣╠╦╝║╠═╣╠╩╗║  ║╣ ╚═╗
#  ╚╝ ╩ ╩╩╚═╩╩ ╩╚═╝╩═╝╚═╝╚═╝
# ==================================================
# uidoc = __revit__.ActiveUIDocument
# doc = __revit__.ActiveUIDocument.Document  # type:Document

# Get the current Revit document and UI document
# uiapp = __revit__.ActiveUIDocument.Application
app = __revit__.Application
uidoc = __revit__.ActiveUIDocument
doc = uidoc.Document

# Use UIApplication for UI-level commands
# uiapp = UIApplication(doc.Application)


# Collect all elements in the model
# collector = FilteredElementCollector(doc).WhereElementIsElementType().ToElements()


# ╔╦╗╔═╗╦╔╗╔
# ║║║╠═╣║║║║
# ╩ ╩╩ ╩╩╝╚╝
# ==================================================


# Define supported categories using correct integer values
SUPPORTED_CATEGORIES = [
    BuiltInCategory.OST_Walls,
    BuiltInCategory.OST_StructuralFraming,  # Beams
    BuiltInCategory.OST_StructuralColumns,  # Columns
]


def select_elements():
    """Prompt user to select elements in Revit and filter them."""
    selection = uidoc.Selection.GetElementIds()

    if len(selection) < 2:
        MessageBox.Show(
            "Please select at least two elements to join/unjoin.",
            "Selection Error",
            MessageBoxButtons.OK,
            MessageBoxIcon.Warning,
        )
        return None

    selected_elements = [doc.GetElement(el_id) for el_id in selection]
    filtered_elements = []

    for el in selected_elements:
        if el.Category and el.Category.Id.IntegerValue in [
            int(cat) for cat in SUPPORTED_CATEGORIES
        ]:
            filtered_elements.append(el)
        else:
            print(
                "Ignored element with ID:",
                el.Id,
                "Category:",
                el.Category.Name if el.Category else "None",
            )

    if len(filtered_elements) < 2:
        MessageBox.Show(
            "Please select at least two valid walls, beams, or columns.",
            "Selection Error",
            MessageBoxButtons.OK,
            MessageBoxIcon.Warning,
        )
        return None

    return filtered_elements


def check_existing_joins(elements):
    """Check which elements are already joined."""
    joined_elements = []
    unjoined_elements = []

    for i in range(len(elements)):
        for j in range(i + 1, len(elements)):
            try:
                if JoinGeometryUtils.AreElementsJoined(doc, elements[i], elements[j]):
                    joined_elements.append((elements[i], elements[j]))
                else:
                    unjoined_elements.append((elements[i], elements[j]))
            except Exception as e:
                print("Error checking join status:", str(e))

    return joined_elements, unjoined_elements


def join_elements(elements):
    """Join selected elements."""
    joined = 0
    failed = 0

    for i in range(len(elements)):
        for j in range(i + 1, len(elements)):
            try:
                if not JoinGeometryUtils.AreElementsJoined(
                    doc, elements[i], elements[j]
                ):
                    JoinGeometryUtils.JoinGeometry(doc, elements[i], elements[j])
                    print("Joined elements:", elements[i].Id, elements[j].Id)
                    joined += 1
            except Exception as e:
                print("Error joining elements:", elements[i].Id, elements[j].Id, str(e))
                failed += 1

    return joined, failed


def unjoin_elements(elements):
    """Unjoin selected elements."""
    unjoined = 0
    failed = 0

    for i in range(len(elements)):
        for j in range(i + 1, len(elements)):
            try:
                if JoinGeometryUtils.AreElementsJoined(doc, elements[i], elements[j]):
                    JoinGeometryUtils.UnjoinGeometry(doc, elements[i], elements[j])
                    print("Unjoined elements:", elements[i].Id, elements[j].Id)
                    unjoined += 1
            except Exception as e:
                print(
                    "Error unjoining elements:", elements[i].Id, elements[j].Id, str(e)
                )
                failed += 1

    return unjoined, failed


# Main Execution
selection = select_elements()

if selection:
    t = Transaction(doc, "Join/Unjoin Elements")
    t.Start()

    joined_pairs, unjoined_pairs = check_existing_joins(selection)

    joined_count = 0
    unjoined_count = 0
    failed_count = 0

    if len(unjoined_pairs) > 0:
        joined_count, failed_count = join_elements(selection)
    elif len(joined_pairs) > 0:
        unjoined_count, failed_count = unjoin_elements(selection)

    t.Commit()

    MessageBox.Show(
        "Operation completed:\n"
        + str(joined_count)
        + " elements joined.\n"
        + str(unjoined_count)
        + " elements unjoined.\n"
        + str(failed_count)
        + " elements failed to process.",
        "Join/Unjoin Summary",
        MessageBoxButtons.OK,
        MessageBoxIcon.Information,
    )
else:
    print("No valid elements selected.")
