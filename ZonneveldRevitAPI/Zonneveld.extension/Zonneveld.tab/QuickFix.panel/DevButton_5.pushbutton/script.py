# -*- coding: utf-8 -*-
__title__ = "Join/Unjoin \n Analytical"
__doc__ = """Version = 1.0
Date    = 20.12.2024
________________________________________________________________
Description:
Enable or disable join for Walls and Structural Framing (Beams) in Revit.
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
from Autodesk.Revit.DB.Structure import StructuralFramingUtils  # Fixed import for beams
from RevitServices.Persistence import DocumentManager
from pyrevit import revit  # Correct way to access Revit


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
# SUPPORTED_CATEGORIES = [
#     BuiltInCategory.OST_Walls,  # Physical Walls
#     BuiltInCategory.OST_StructuralFraming,  # Physical Beams
#     BuiltInCategory.OST_StructuralColumns,  # Physical Columns
#     BuiltInCategory.OST_WallAnalytical,  # Analytical Walls
#     BuiltInCategory.OST_BeamAnalytical,  # Analytical Beams
#     BuiltInCategory.OST_ColumnAnalytical,  # Analytical Columns
# ]


# Function to get valid walls, beams, and columns
def get_elements():
    selection = uidoc.Selection.GetElementIds()
    if not selection:
        print("No elements selected.")
        return []

    selected_elements = [doc.GetElement(el_id) for el_id in selection]
    elements = [
        el
        for el in selected_elements
        if el.Category
        and el.Category.Id.IntegerValue
        in [
            int(BuiltInCategory.OST_Walls),  # Walls
            int(BuiltInCategory.OST_StructuralFraming),  # Structural Beams
            int(BuiltInCategory.OST_StructuralColumns),  # Structural Columns
        ]
    ]

    return elements


# Function to check if a wall is joined
def is_wall_joined(wall):
    return WallUtils.IsWallJoinAllowedAtEnd(
        wall, 0
    ) or WallUtils.IsWallJoinAllowedAtEnd(wall, 1)


# Function to check if a beam is joined
def is_beam_joined(beam):
    return StructuralFramingUtils.IsJoinAllowedAtEnd(
        beam, 0
    ) or StructuralFramingUtils.IsJoinAllowedAtEnd(beam, 1)


# Function to check if two elements (columns) are joined using JoinGeometryUtils
def are_columns_joined(doc, col1, col2):
    return JoinGeometryUtils.AreElementsJoined(doc, col1, col2)


# Function to toggle wall joins
def toggle_wall_join(walls, allow):
    count = 0
    for wall in walls:
        try:
            if allow:
                WallUtils.AllowWallJoinAtEnd(wall, 0)
                WallUtils.AllowWallJoinAtEnd(wall, 1)
                print("Joined Wall ID:", wall.Id)
            else:
                WallUtils.DisallowWallJoinAtEnd(wall, 0)
                WallUtils.DisallowWallJoinAtEnd(wall, 1)
                print("Unjoined Wall ID:", wall.Id)
            count += 1
        except Exception as ex:
            print("Error processing wall join:", str(ex))
    return count


# Function to toggle beam joins
def toggle_beam_join(beams, allow):
    count = 0
    for beam in beams:
        try:
            if allow:
                StructuralFramingUtils.AllowJoinAtEnd(beam, 0)
                StructuralFramingUtils.AllowJoinAtEnd(beam, 1)
                print("Joined Beam ID:", beam.Id)
            else:
                StructuralFramingUtils.DisallowJoinAtEnd(beam, 0)
                StructuralFramingUtils.DisallowJoinAtEnd(beam, 1)
                print("Unjoined Beam ID:", beam.Id)
            count += 1
        except Exception as ex:
            print("Error processing beam join:", str(ex))
    return count


# Function to toggle column joins using JoinGeometryUtils
def toggle_column_join(doc, columns, allow):
    count = 0
    for i in range(len(columns)):
        for j in range(i + 1, len(columns)):
            col1 = columns[i]
            col2 = columns[j]
            try:
                if allow:
                    if not are_columns_joined(doc, col1, col2):
                        JoinGeometryUtils.JoinGeometry(doc, col1, col2)
                        print("Joined Columns:", col1.Id, col2.Id)
                else:
                    if are_columns_joined(doc, col1, col2):
                        JoinGeometryUtils.UnjoinGeometry(doc, col1, col2)
                        print("Unjoined Columns:", col1.Id, col2.Id)
                count += 1
            except Exception as ex:
                print("Error processing column join:", str(ex))
    return count


# Main Execution
elements = get_elements()

if elements:
    # Separate Walls, Beams, and Columns
    walls = [
        el
        for el in elements
        if el.Category.Id.IntegerValue == int(BuiltInCategory.OST_Walls)
    ]
    beams = [
        el
        for el in elements
        if el.Category.Id.IntegerValue == int(BuiltInCategory.OST_StructuralFraming)
    ]
    columns = [
        el
        for el in elements
        if el.Category.Id.IntegerValue == int(BuiltInCategory.OST_StructuralColumns)
    ]

    # Detect already joined elements
    joined_walls = [wall for wall in walls if is_wall_joined(wall)]
    joined_beams = [beam for beam in beams if is_beam_joined(beam)]
    joined_columns = [
        col1
        for col1 in columns
        if any(
            are_columns_joined(doc, col1, col2)
            for col2 in columns
            if col1.Id != col2.Id
        )
    ]

    # Start transaction
    t = Transaction(doc, "Join/Unjoin Walls, Beams & Columns")
    try:
        t.Start()

        wall_count = 0
        beam_count = 0
        column_count = 0

        if joined_walls:
            wall_count = toggle_wall_join(joined_walls, allow=False)  # Unjoin walls
        else:
            wall_count = toggle_wall_join(walls, allow=True)  # Join walls

        if joined_beams:
            beam_count = toggle_beam_join(joined_beams, allow=False)  # Unjoin beams
        else:
            beam_count = toggle_beam_join(beams, allow=True)  # Join beams

        if joined_columns:
            column_count = toggle_column_join(
                doc, joined_columns, allow=False
            )  # Unjoin columns
        else:
            column_count = toggle_column_join(doc, columns, allow=True)  # Join columns

        t.Commit()

        # Print summary
        print("Join/Unjoin Summary")
        print("Walls Processed:", wall_count)
        print("Beams Processed:", beam_count)
        print("Columns Processed:", column_count)

    except Exception as e:
        print("Transaction failed:", str(e))
        t.RollBack()
else:
    print("No valid walls, beams, or columns selected.")
