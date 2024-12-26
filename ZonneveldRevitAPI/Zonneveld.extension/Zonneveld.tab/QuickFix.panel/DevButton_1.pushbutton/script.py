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


def log(message):
    print(message)


def get_workset_id_by_wall_type(wall_type_name):
    for prefix, workset_id in WORKSET_MAPPING.items():
        if wall_type_name.startswith(prefix):
            return workset_id
    return None


def assign_workset(wall, workset_id):
    try:
        t = Transaction(doc, "Assign Workset")
        t.Start()
        param = wall.get_Parameter(BuiltInParameter.ELEM_PARTITION_PARAM)
        if param and not param.IsReadOnly:
            param.Set(workset_id)
            log("Assigned wall {} to WorksetId {}".format(wall.Id, workset_id))
        else:
            log(
                "Workset parameter is missing or read-only for wall {}.".format(wall.Id)
            )
        t.Commit()
    except Exception as e:
        log("Failed to assign WorksetId to wall {}: {}".format(wall.Id, e))


def process_walls():
    log("Processing all walls...")
    walls = (
        FilteredElementCollector(doc)
        .OfCategory(BuiltInCategory.OST_Walls)
        .WhereElementIsNotElementType()
    )
    if not walls:
        log("No walls found in the document.")
        return

    for wall in walls:
        wall_type = doc.GetElement(wall.GetTypeId())
        wall_type_name = wall_type.get_Parameter(
            BuiltInParameter.ALL_MODEL_TYPE_NAME
        ).AsString()
        log("Processing wall ID {}: WallType = {}".format(wall.Id, wall_type_name))
        workset_id = get_workset_id_by_wall_type(wall_type_name)
        if workset_id:
            assign_workset(wall, workset_id)
        else:
            log("No matching workset found for wall {}".format(wall.Id))

    log("Manual wall processing complete.")


process_walls()
