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
# SUPPORTED_CATEGORIES = [
#     BuiltInCategory.OST_Walls,  # Physical Walls
#     BuiltInCategory.OST_StructuralFraming,  # Physical Beams
#     BuiltInCategory.OST_StructuralColumns,  # Physical Columns
#     BuiltInCategory.OST_WallAnalytical,  # Analytical Walls
#     BuiltInCategory.OST_BeamAnalytical,  # Analytical Beams
#     BuiltInCategory.OST_ColumnAnalytical,  # Analytical Columns
# ]


# Function to get valid wall elements
def get_walls():
    selection = uidoc.Selection.GetElementIds()
    if not selection:
        print("No elements selected.")
        return []

    selected_elements = [doc.GetElement(el_id) for el_id in selection]
    walls = [
        el
        for el in selected_elements
        if el.Category and el.Category.Id.IntegerValue == int(BuiltInCategory.OST_Walls)
    ]

    return walls


# Function to check if a wall is joined at both ends
def is_wall_joined(wall):
    return WallUtils.IsWallJoinAllowedAtEnd(
        wall, 0
    ) or WallUtils.IsWallJoinAllowedAtEnd(wall, 1)


# Function to toggle wall joins
def toggle_wall_join(walls, allow):
    count = 0

    for wall in walls:
        try:
            # Allow or Disallow joins at both ends
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


# Main Execution
walls = get_walls()

if walls:
    # Check if walls are already joined
    joined_walls = [wall for wall in walls if is_wall_joined(wall)]

    # Start transaction
    t = Transaction(doc, "Join/Unjoin Walls")
    try:
        t.Start()

        if joined_walls:
            unjoined_count = toggle_wall_join(joined_walls, allow=False)  # Unjoin
            print("Walls Unjoined:", unjoined_count)
        else:
            joined_count = toggle_wall_join(walls, allow=True)  # Join
            print("Walls Joined:", joined_count)

        t.Commit()
    except Exception as e:
        print("Transaction failed:", str(e))
        t.RollBack()
else:
    print("No valid wall elements selected.")
