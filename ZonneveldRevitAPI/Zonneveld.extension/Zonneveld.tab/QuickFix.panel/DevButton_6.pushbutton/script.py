# -*- coding: utf-8 -*-
__title__ = "Join/Unjoin \n Analytical"
__doc__ = """Version = 1.0
Date    = 20.12.2024
________________________________________________________________
Description:

Simulates Revit's 'Allow Join' and 'Disallow Join' behaviour for analytical elements.
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


# Supported analytical categories
ANALYTICAL_CATEGORIES = [
    BuiltInCategory.OST_WallAnalytical,  # AnalyticalWalls
    BuiltInCategory.OST_BeamAnalytical,  # AnalyticalBeams
    BuiltInCategory.OST_ColumnAnalytical,  # AnalyticalColumns
]


# Function to select analytical elements
def select_analytical_elements():
    selection = uidoc.Selection.GetElementIds()
    if len(selection) < 1:
        MessageBox.Show(
            "Please select at least one analytical element.",
            "Selection Error",
            MessageBoxButtons.OK,
            MessageBoxIcon.Warning,
        )
        return None

    selected_elements = [doc.GetElement(el_id) for el_id in selection]

    # Filter elements by analytical categories
    analytical_elements = [
        el
        for el in selected_elements
        if el.Category
        and el.Category.Id.IntegerValue in [int(cat) for cat in ANALYTICAL_CATEGORIES]
    ]

    if not analytical_elements:
        MessageBox.Show(
            "No valid analytical elements selected.\nPlease select analytical walls, beams, or columns.",
            "Selection Error",
            MessageBoxButtons.OK,
            MessageBoxIcon.Warning,
        )
        return None

    return analytical_elements


# Function to toggle join status
def toggle_join_status(elements):
    joined_elements = []
    unjoined_elements = []
    failed_elements = []

    t = Transaction(doc, "Toggle Join Status")
    t.Start()

    for element in elements:
        analytical_model = element.GetAnalyticalModel()
        if analytical_model and analytical_model.IsJoined:
            try:
                analytical_model.DisallowJoin()
                unjoined_elements.append(element.Id)
            except Exception as e:
                failed_elements.append(element.Id)
                print("Error disallowing join:", element.Id, str(e))
        else:
            try:
                analytical_model.AllowJoin()
                joined_elements.append(element.Id)
            except Exception as e:
                failed_elements.append(element.Id)
                print("Error allowing join:", element.Id, str(e))

    t.Commit()

    # Summary popup
    MessageBox.Show(
        "Operation completed:\n"
        + str(len(joined_elements))
        + " elements joined.\n"
        + str(len(unjoined_elements))
        + " elements unjoined.\n"
        + str(len(failed_elements))
        + " elements failed to process.",
        "Join/Unjoin Analytical Summary",
        MessageBoxButtons.OK,
        MessageBoxIcon.Information,
    )


# Main Execution
selection = select_analytical_elements()

if selection:
    toggle_join_status(selection)
else:
    print("No valid analytical elements selected.")
