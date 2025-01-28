# -*- coding: utf-8 -*-
__title__ = "Join/Unjoin \n Analytical & Physcial"
__doc__ = """Version = 1.0
Date    = 20.12.2024
________________________________________________________________
Description:

Simulates Revit's 'Allow Join' and 'Disallow Join' for analytical and physcial elements.
________________________________________________________________
Author: Emin Avdovic"""

# ╦╔╦╗╔═╗╔═╗╦═╗╔╦╗╔═╗
# ║║║║╠═╝║ ║╠╦╝ ║ ╚═╗
# ╩╩ ╩╩  ╚═╝╩╚═ ╩ ╚═╝
# ==================================================
# .NET Imports
import clr

clr.AddReference("RevitAPI")
clr.AddReference("RevitServices")
clr.AddReference("RevitNodes")

from Autodesk.Revit.DB import *
from RevitServices.Persistence import DocumentManager
from pyrevit import revit  # Proper Revit document handling


# ╦  ╦╔═╗╦═╗╦╔═╗╔╗ ╦  ╔═╗╔═╗
# ╚╗╔╝╠═╣╠╦╝║╠═╣╠╩╗║  ║╣ ╚═╗
#  ╚╝ ╩ ╩╩╚═╩╩ ╩╚═╝╩═╝╚═╝╚═╝
# ==================================================
# Ensure proper Revit document access
uidoc = revit.uidoc
doc = revit.doc

# ╔╦╗╔═╗╦╔╗╔
# ║║║╠═╣║║║║
# ╩ ╩╩ ╩╩╝╚╝
# ==================================================

# Supported analytical categories
SUPPORTED_CATEGORIES = [
    BuiltInCategory.OST_Walls,  # Physical Walls
    BuiltInCategory.OST_StructuralFraming,  # Physical Beams
    BuiltInCategory.OST_StructuralColumns,  # Physical Columns
    BuiltInCategory.OST_WallAnalytical,  # Analytical Walls
    BuiltInCategory.OST_BeamAnalytical,  # Analytical Beams
    BuiltInCategory.OST_ColumnAnalytical,  # Analytical Columns
]


# Function to enable analytical models if disabled
def enable_analytical_model(element, transaction):
    param = element.get_Parameter(BuiltInParameter.STRUCTURAL_ANALYTICAL_MODEL)
    if param and param.AsInteger() == 0:
        param.Set(1)


# Function to get valid elements from selection
def get_valid_elements():
    selection = uidoc.Selection.GetElementIds()
    if not selection:
        print("No elements selected.")
        return []

    selected_elements = [doc.GetElement(el_id) for el_id in selection]
    valid_elements = []

    for el in selected_elements:
        if el.Category and el.Category.Id.IntegerValue in [
            int(cat) for cat in SUPPORTED_CATEGORIES
        ]:
            valid_elements.append(el)

    return valid_elements


# Function to join/unjoin walls
def toggle_wall_join(elements, allow, transaction):
    for e in elements:
        try:
            (
                WallUtils.AllowWallJoinAtEnd(e, 0)
                if allow
                else WallUtils.DisallowWallJoinAtEnd(e, 0)
            )
            (
                WallUtils.AllowWallJoinAtEnd(e, 1)
                if allow
                else WallUtils.DisallowWallJoinAtEnd(e, 1)
            )
        except Exception as ex:
            print("Error processing wall join:", str(ex))


# Function to join/unjoin structural framing
def toggle_framing_join(elements, allow, transaction):
    for e in elements:
        try:
            (
                StructuralFramingUtils.AllowJoinAtEnd(e, 0)
                if allow
                else StructuralFramingUtils.DisallowJoinAtEnd(e, 0)
            )
            (
                StructuralFramingUtils.AllowJoinAtEnd(e, 1)
                if allow
                else StructuralFramingUtils.DisallowJoinAtEnd(e, 1)
            )
        except Exception as ex:
            print("Error processing framing join:", str(ex))


# Function to process analytical join/unjoin
def toggle_analytical_join(elements, transaction):
    joined = 0
    unjoined = 0
    failed = 0

    for i in range(len(elements)):
        for j in range(i + 1, len(elements)):
            elem1 = elements[i]
            elem2 = elements[j]

            # Handle Analytical Model
            analytical_model1 = (
                elem1.GetAnalyticalModel()
                if hasattr(elem1, "GetAnalyticalModel")
                else None
            )
            analytical_model2 = (
                elem2.GetAnalyticalModel()
                if hasattr(elem2, "GetAnalyticalModel")
                else None
            )

            if analytical_model1 and analytical_model2:
                try:
                    if analytical_model1.HasAnalyticalAssociation(analytical_model2):
                        analytical_model1.RemoveAnalyticalAssociation(analytical_model2)
                        analytical_model2.RemoveAnalyticalAssociation(analytical_model1)
                        unjoined += 1
                    else:
                        analytical_model1.AddAnalyticalAssociation(analytical_model2)
                        analytical_model2.AddAnalyticalAssociation(analytical_model1)
                        joined += 1
                except Exception as e:
                    print("Error processing analytical join:", str(e))
                    failed += 1

    print("\nJoin/Unjoin Summary")
    print("Elements Joined:", joined)
    print("Elements Unjoined:", unjoined)
    print("Elements Failed:", failed)


# Main Execution
valid_selection = get_valid_elements()

if valid_selection:
    walls = [
        el
        for el in valid_selection
        if el.Category.Id.IntegerValue == int(BuiltInCategory.OST_Walls)
    ]
    framing = [
        el
        for el in valid_selection
        if el.Category.Id.IntegerValue == int(BuiltInCategory.OST_StructuralFraming)
    ]
    analytical = [
        el
        for el in valid_selection
        if el.Category.Id.IntegerValue
        in [
            int(BuiltInCategory.OST_WallAnalytical),
            int(BuiltInCategory.OST_BeamAnalytical),
            int(BuiltInCategory.OST_ColumnAnalytical),
        ]
    ]

    # ✅ Correct Transaction Handling (Only One Transaction)
    t = Transaction(doc, "Join/Unjoin Elements")
    try:
        t.Start()

        # Enable analytical model if missing
        for element in valid_selection:
            enable_analytical_model(element, t)

        # Process walls, framing, and analytical joins
        if walls:
            toggle_wall_join(
                walls, allow=True, transaction=t
            )  # Change to False to disallow
        if framing:
            toggle_framing_join(
                framing, allow=True, transaction=t
            )  # Change to False to disallow
        if analytical:
            toggle_analytical_join(analytical, transaction=t)

        t.Commit()
    except Exception as e:
        print("Transaction failed:", str(e))
        t.RollBack()
else:
    print("No valid elements selected.")
