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


# ✅ Define Supported Structural Categories (Physical & Analytical)
SUPPORTED_CATEGORIES = [
    BuiltInCategory.OST_Walls,  # Walls (Physical)
    BuiltInCategory.OST_WallAnalytical,  # Walls (Analytical)
    BuiltInCategory.OST_StructuralFraming,  # Beams & Bracing (Physical)
    BuiltInCategory.OST_BeamAnalytical,  # Beams & Bracing (Analytical)
    BuiltInCategory.OST_StructuralColumns,  # Columns (Physical)
    BuiltInCategory.OST_ColumnAnalytical,  # Columns (Analytical)
    BuiltInCategory.OST_Floors,  # Floors (Physical)
    BuiltInCategory.OST_FloorAnalytical,  # Floors (Analytical)
    BuiltInCategory.OST_StructuralFoundation,  # Foundations (Physical)
    BuiltInCategory.OST_FoundationSlabAnalytical,  # Foundations (Analytical)
]


# ✅ Function to Get Selected Structural Elements
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
        and el.Category.Id.IntegerValue in [int(cat) for cat in SUPPORTED_CATEGORIES]
    ]

    return elements


# ✅ Function to Check if a Wall is Joined
def is_wall_joined(wall):
    return WallUtils.IsWallJoinAllowedAtEnd(
        wall, 0
    ) or WallUtils.IsWallJoinAllowedAtEnd(wall, 1)


# ✅ Function to Check if a Beam is Joined
def is_beam_joined(beam):
    return StructuralFramingUtils.IsJoinAllowedAtEnd(
        beam, 0
    ) or StructuralFramingUtils.IsJoinAllowedAtEnd(beam, 1)


# ✅ Function to Check if a Column is Joined
def are_columns_joined(doc, col1, col2):
    return JoinGeometryUtils.AreElementsJoined(doc, col1, col2)


# ✅ Function to Toggle Wall Joins
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


# ✅ Function to Toggle Beam Joins
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


# ✅ Function to Toggle Column Joins
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


# ✅ Function to Toggle Floor & Foundation Joins
def toggle_floor_join(doc, floors, allow):
    count = 0
    for i in range(len(floors)):
        for j in range(i + 1, len(floors)):
            floor1 = floors[i]
            floor2 = floors[j]
            try:
                if allow:
                    if not JoinGeometryUtils.AreElementsJoined(doc, floor1, floor2):
                        JoinGeometryUtils.JoinGeometry(doc, floor1, floor2)
                        print("Joined Floors:", floor1.Id, floor2.Id)
                else:
                    if JoinGeometryUtils.AreElementsJoined(doc, floor1, floor2):
                        JoinGeometryUtils.UnjoinGeometry(doc, floor1, floor2)
                        print("Unjoined Floors:", floor1.Id, floor2.Id)
                count += 1
            except Exception as ex:
                print("Error processing floor join:", str(ex))
    return count


# ✅ Main Execution
elements = get_elements()

if elements:
    # Separate Elements by Category
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
    floors = [
        el
        for el in elements
        if el.Category.Id.IntegerValue == int(BuiltInCategory.OST_Floors)
    ]

    # Detect already joined elements
    joined_walls = [wall for wall in walls if is_wall_joined(wall)]
    joined_beams = [beam for beam in beams if is_beam_joined(beam)]
    joined_columns = [col for col in columns]
    joined_floors = [floor for floor in floors]

    # Start transaction
    t = Transaction(doc, "Join/Unjoin Structural Elements")
    try:
        t.Start()

        wall_count = toggle_wall_join(walls, allow=not joined_walls)
        beam_count = toggle_beam_join(beams, allow=not joined_beams)
        column_count = toggle_column_join(doc, columns, allow=not joined_columns)
        floor_count = toggle_floor_join(doc, floors, allow=not joined_floors)

        t.Commit()

        # Print Summary
        print("Join/Unjoin Summary")
        print("Walls Processed:", wall_count)
        print("Beams Processed:", beam_count)
        print("Columns Processed:", column_count)
        print("Floors Processed:", floor_count)

    except Exception as e:
        print("Transaction failed:", str(e))
        t.RollBack()
else:
    print("No valid structural elements selected.")
