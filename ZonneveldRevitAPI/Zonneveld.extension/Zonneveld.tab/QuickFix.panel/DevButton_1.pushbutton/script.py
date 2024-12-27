# -*- coding: utf-8 -*-
__title__ = "Fix Worksets"
__doc__ = """This manually assigns correct worksets to all existing elements in the project."""

# Manual Workset Assignment Script
from Autodesk.Revit.DB import (
    BuiltInCategory,
    BuiltInParameter,
    Transaction,
    FilteredElementCollector,
)

uidoc = __revit__.ActiveUIDocument
doc = uidoc.Document

# Workset mapping based on WallType prefix
WORKSET_MAPPING = {
    # Grids and Levels-------------------------
    "ZI": 0,  # Example: 01 Stramien en levels
    "Zi": 0,  # Example: 01 Stramien en levels
    "Peil": 0,  # Example: 01 Stramien en levels
    "Reference": 0,  # Example: 01 Stramien en levels
    # Foundation Piles-------------------------
    # "16": 1160,  # Need to change number to 17 or something else not be duplicate Example: 02 Funderingspalen
    "17": 1160,  # Example: 02 Funderingspalen
    # Foundation-------------------------------
    "16": 1161,  # Example: 03 Fundering
    # "Zi": 1161, Change text or number no duplicate for slab edge Example: 03 Fundering
    "13": 1161,  # Example: 03 Fundering
    # Floors-----------------------------------
    # "13": 1161, # Change prefix Example: 04 Vloeren
    "23": 1161,  # Example: 04 Vloeren
    "43": 1161,  # Example: 04 Vloeren
    # Floor Beams------------------------------
    "L2": 1163,  # Example: 05 Balklaag vloeren
    "L6": 1163,  # Example: 05 Balklaag vloeren
    "windverband": 1163,  # Example: 05 Balklaag vloeren
    # "16": 1163,  # Change prefix
    # "21": 1163,  # Change prefix
    # "22": 1163,  # Change prefix
    # "28": 1163,  # Change prefix
    "Vloer": 1163,  # Change prefix
    # Walls Exterior---------------------------
    "21": 1164,  # Example: 06 Buitenwanden
    "L4": 1164,  # Example: 06 Buitenwanden
    # Walls Interior---------------------------
    "22": 1165,  # Example: 07 Binnenwanden
    "42": 1165,  # Example: 07 Binnenwanden
    # Timber Frame Walls-----------------------
    # Roof Beams-------------------------------
    "Dak": 1166,  # Change prefix Example: 09 Dakliggers
    # Columns----------------------------------
    "28": 4796,  # Example: 10 Kolommen
    # Structural Frames (Bracing)--------------
    # "16": 4791, # Change prefix Example: 11 Gebinten
    # "21": 4791, # Change prefix Example: 11 Gebinten
    # "22": 4791, # Change prefix Example: 11 Gebinten
    # "28": 4791, # Change prefix Example: 11 Gebinten
    # "L2": 4791, # Change Prefix Example: 11 Gebinten
    # "L6": 4791, # Change Prefix Example: 11 Gebinten
    # "windverband": 4791 # Change prefix Example: 11 Gebinten
    # Steel Beams------------------------------
    # Give different Pefix
    # Wall Plates------------------------------
    # Roof Sheating----------------------------
    "00": 1167,  # Example: 13 Dakbeschot
    "27": 1167,  # Example: 13 Dakbeschot
    "L3": 1167,  # Example: 13 Dakbeschot
    # Structural Provisions--------------------
    # Mass-------------------------------------
    "Mass": 1173,  # Example: 21 Massa
    # Facade and Roof Openings-----------------
    "31": 1174,  # Example: 22 Gevel- en dakopeningen
    "37": 1174,  # Example: 22 Gevel- en dakopeningen
    # Interior Wall Openings-------------------
    "32": 3447,  # Example: 23 Binnenwandopeningen
    # Point Cloud------------------------------
    ".rcs": 3581,  # Example: 31 Pointcloud
    ".rcp": 3581,  # Example: 31 Point Cloud
    # Clash Test-------------------------------
    # Topography / Toposurface-----------------
}


def log(message):
    """Log messages to the console."""
    print(message)


def get_workset_id_by_element_type(element_type_name):
    """Get the appropriate workset ID based on the element type name."""
    for prefix, workset_id in WORKSET_MAPPING.items():
        if element_type_name.startswith(prefix):
            return workset_id
    return None


def assign_workset(element, workset_id):
    try:
        t = Transaction(doc, "Assign Workset")
        t.Start()
        param = element.get_Parameter(BuiltInParameter.ELEM_PARTITION_PARAM)
        if param and not param.IsReadOnly:
            param.Set(workset_id)
            log("Assigned element {} to WorksetId {}".format(element.Id, workset_id))
        else:
            log(
                "Workset parameter is missing or read-only for element {}.".format(
                    element.Id
                )
            )
        t.Commit()
    except Exception as e:
        log("Failed to assign WorksetId to element {}: {}".format(element.Id, e))


def process_elements():
    """Process elements across multiple categories and assign worksets."""
    # Define categories to process
    categories = [
        BuiltInCategory.OST_Grids,  # Grids
        BuiltInCategory.OST_Levels,  # Levels
        BuiltInCategory.OST_ReferencePlanes,  # ReferencePlanes
        BuiltInCategory.OST_Walls,  # Walls
        BuiltInCategory.OST_Floors,  # Floors
        BuiltInCategory.OST_Roofs,  # Roofs
        BuiltInCategory.OST_Ceilings,  # Ceilings
        BuiltInCategory.OST_StructuralFraming,  # Structural Frames
        BuiltInCategory.OST_StructuralColumns,  # Columns
        BuiltInCategory.OST_StructuralFoundation,  # Foundation
    ]

    for category in categories:
        elements = (
            FilteredElementCollector(doc)
            .OfCategory(category)
            .WhereElementIsNotElementType()
        )
        for element in elements:
            element_type = doc.GetElement(element.GetTypeId())
            element_type_name = element_type.get_Parameter(
                BuiltInParameter.ALL_MODEL_TYPE_NAME
            ).AsString()
            log(
                "Processing element ID {}: Type = {}".format(
                    element.Id, element_type_name
                )
            )

            workset_id = get_workset_id_by_element_type(element_type_name)
            if workset_id:
                assign_workset(element, workset_id)
            else:
                log("No matching workset found for element {}".format(element.Id))


log("Manual workset processing started.")
process_elements()
log("Manual workset processing completed.")
