# -*- coding: utf-8 -*-
__title__ = "Automate Worksets"
__doc__ = """Automatically assigns worksets to walls based on their type."""

from Autodesk.Revit.DB import (
    BuiltInCategory,
    BuiltInParameter,
    Transaction,
    FilteredElementCollector,
)

# Initialize Revit document and application
uidoc = __revit__.ActiveUIDocument
doc = uidoc.Document

# Workset mapping based on WallType prefix
WORKSET_MAPPING = {
    "16": 1161,  # Example: 03 Fundering
    "21": 1164,  # Example: 06 Buitenwanden
    "L4-S-2": 1164,  # Example: 06 Buitenwanden
    "22": 1165,  # Example: 07 Binnenwanden
    "42": 1165,  # Example: 07 Binnenwanden
    "L4-D-1": 1165,  # Example: 07 Binnenwanden
    "L4-H": 1165,  # Example: 07 Binnenwanden
    "L4-K": 1165,  # Example: 07 Binnenwanden
    "L4-S-1": 1165,  # Example: 07 Binnenwanden
    # Add other prefixes and their corresponding WorksetId here
}


def get_workset_id_by_wall_type(wall_type_name):
    """Determine the workset ID based on the wall type prefix."""
    for prefix, workset_id in WORKSET_MAPPING.items():
        if wall_type_name.startswith(prefix):
            return workset_id
    return None  # No match found


def assign_workset(wall, workset_id):
    """Assign a workset to a wall."""
    try:
        t = Transaction(doc, "Assign Workset")
        t.Start()
        param = wall.get_Parameter(BuiltInParameter.ELEM_PARTITION_PARAM)
        if param and not param.IsReadOnly:
            param.Set(workset_id)
            print("Assigned wall {} to WorksetId {}".format(wall.Id, workset_id))
        else:
            print(
                "Workset parameter is missing or read-only for wall {}.".format(wall.Id)
            )
        t.Commit()
    except Exception as e:
        print("Failed to assign WorksetId to wall {}: {}".format(wall.Id, e))


def process_existing_walls():
    """Process all existing walls in the document and assign correct worksets."""
    walls = (
        FilteredElementCollector(doc)
        .OfCategory(BuiltInCategory.OST_Walls)
        .WhereElementIsNotElementType()
    )
    for wall in walls:
        wall_type = doc.GetElement(wall.GetTypeId())
        wall_type_name = wall_type.get_Parameter(
            BuiltInParameter.ALL_MODEL_TYPE_NAME
        ).AsString()
        print("Processing wall ID {}: WallType = {}".format(wall.Id, wall_type_name))
        workset_id = get_workset_id_by_wall_type(wall_type_name)
        if workset_id:
            assign_workset(wall, workset_id)
        else:
            print("No matching workset found for wall {}".format(wall.Id))


# Automatically run the script
process_existing_walls()
print("Workset Automation complete.")
