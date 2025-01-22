# -*- coding: utf-8 -*-
__title__ = "Allow Join"
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
    ElementCategoryFilter,
    JoinGeometryUtils,
    Element,
    ElementId,
    Transaction,
    WorksetKind,
)
from Autodesk.Revit.DB import Transaction
from Autodesk.Revit.UI import *
from Autodesk.Revit.UI import TaskDialog
from pyrevit import forms


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

from System.Windows.Forms import MessageBox, MessageBoxButtons, MessageBoxIcon

# Collect all elements in the model
# collector = FilteredElementCollector(doc).WhereElementIsElementType().ToElements()

# ╔╦╗╔═╗╦╔╗╔
# ║║║╠═╣║║║║
# ╩ ╩╩ ╩╩╝╚╝
# ==================================================


def select_elements():
    """Prompt user to select elements in Revit."""
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
    return selected_elements


def filter_walls(elements):
    """Filter only wall elements from the selection."""
    walls = [
        e
        for e in elements
        if e.Category and e.Category.Id.IntegerValue == int(BuiltInCategory.OST_Walls)
    ]
    return walls


def join_or_unjoin_elements(elements):
    """Join or unjoin multiple selected wall elements."""
    t = Transaction(doc, "Join/Unjoin Walls")
    t.Start()
    joined_count = 0
    unjoined_count = 0

    for i in range(len(elements)):
        for j in range(i + 1, len(elements)):
            elem1 = elements[i]
            elem2 = elements[j]

            if JoinGeometryUtils.AreElementsJoined(doc, elem1, elem2):
                JoinGeometryUtils.UnjoinGeometry(doc, elem1, elem2)
                unjoined_count += 1
            else:
                try:
                    JoinGeometryUtils.JoinGeometry(doc, elem1, elem2)
                    joined_count += 1
                except Exception as e:
                    MessageBox.Show(
                        "Error in joining elements: {}".format(str(e)),
                        "Error",
                        MessageBoxButtons.OK,
                        MessageBoxIcon.Error,
                    )
    t.Commit()

    MessageBox.Show(
        "{} elements joined, {} elements unjoined.".format(
            joined_count, unjoined_count
        ),
        "Operation Completed",
        MessageBoxButtons.OK,
        MessageBoxIcon.Information,
    )


# Main Execution
selection = select_elements()

if selection:
    walls = filter_walls(selection)
    if len(walls) < 2:
        MessageBox.Show(
            "Please select at least two valid wall elements.",
            "Selection Error",
            MessageBoxButtons.OK,
            MessageBoxIcon.Warning,
        )
    else:
        join_or_unjoin_elements(walls)
else:
    MessageBox.Show(
        "No valid elements selected.",
        "Selection Error",
        MessageBoxButtons.OK,
        MessageBoxIcon.Warning,
    )
