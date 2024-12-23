# -*- coding: utf-8 -*-
__title__ = "Dynamic Workset Automation (Ignore Thickness)"
__doc__ = (
    """Automatically assigns walls to worksets based on WallType, ignoring thickness."""
)

from Autodesk.Revit.DB import BuiltInParameter, Transaction, Workset
import re  # Import regex module for removing thickness

# Revit document and application
uidoc = __revit__.ActiveUIDocument
doc = uidoc.Document

# Workset Mapping by Exact Base Wall Types
WORKSET_MAPPING = {
    "21_NCG_HSB": "06 Buitenwanden",
    "21_NCG_HSB kozijn": "06 Buitenwanden",
    "21_NCG_ihwg beton": "06 Buitenwanden",
    "21_NCG_lichtgewicht schoorsteen": "06 Buitenwanden",
    "21_NCG_metselwerk (halfsteens)": "06 Buitenwanden",
    "21_NCG_metselwerk (steens)": "06 Buitenwanden",
    "21_NCG_prefab beton": "06 Buitenwanden",
    "21_NCG_spouw - mw/kzs": "06 Buitenwanden",
    "21_NCG_spouw - mw/mw": "06 Buitenwanden",
    "22_NCG_gasbeton": "05 Balklaag vloeren",
    "22_NCG_HSB": "05 Balklaag vloeren",
    "22_NCG_ihwg beton": "05 Balklaag vloeren",
    "22_NCG_kalkzandsteen": "05 Balklaag vloeren",
    "22_NCG_lichte scheidingswand": "05 Balklaag vloeren",
    "22_NCG_metselwerk (halfsteens)": "05 Balklaag vloeren",
    "22_NCG_metselwerk (steens)": "05 Balklaag vloeren",
    "22_NCG_prefab beton": "05 Balklaag vloeren",
}


# Utility: Remove Thickness from WallType
def remove_thickness(wall_type_name):
    """Remove numerical thickness (e.g., 100mm) from the WallType name."""
    return re.sub(r"\s\d+mm$", "", wall_type_name)


# Fetch Workset ID by Name
def get_workset_id_by_name(doc, workset_name):
    """Retrieve the workset ID by its name."""
    worksets = Workset.GetWorksets(doc)
    for workset in worksets:
        if workset.Name == workset_name:
            return workset.Id
    return None


# Assign Workset to Wall
def assign_workset(doc, wall, workset_name, built_in_param):
    """Assign the correct workset to a wall."""
    try:
        workset_id = get_workset_id_by_name(doc, workset_name)
        if not workset_id:
            print("Workset '{}' not found for wall {}.".format(workset_name, wall.Id))
            return

        # Start a transaction to update the workset
        with Transaction(doc, "Assign Workset"):
            param = wall.get_Parameter(built_in_param.ELEM_PARTITION_PARAM)
            if param and not param.IsReadOnly:
                param.Set(workset_id.IntegerValue)
                print("Assigned wall {} to workset '{}'.".format(wall.Id, workset_name))
            else:
                print(
                    "Workset parameter is missing or read-only for wall {}.".format(
                        wall.Id
                    )
                )
    except Exception as e:
        print("Failed to assign workset to wall {}: {}".format(wall.Id, e))


# Process Newly Added Walls
def process_walls(doc, walls, workset_mapping, built_in_param):
    """Process newly added walls and assign worksets dynamically."""
    for wall in walls:
        # Get the WallType
        wall_type = doc.GetElement(wall.GetTypeId())
        if not wall_type:
            print("WallType is missing for wall {}.".format(wall.Id))
            continue

        # Get the WallType name
        wall_type_name = wall_type.get_Parameter(
            built_in_param.ALL_MODEL_TYPE_NAME
        ).AsString()
        if not wall_type_name:
            print("WallType name is missing for wall {}.".format(wall.Id))
            continue

        # Remove thickness from WallType name
        base_wall_type = remove_thickness(wall_type_name)

        # Log the WallType name
        print(
            "Processing wall ID {}: WallType = {}, Base Type = {}".format(
                wall.Id, wall_type_name, base_wall_type
            )
        )

        # Determine the workset based on the Base WallType name
        workset_name = workset_mapping.get(base_wall_type)
        if workset_name:
            assign_workset(doc, wall, workset_name, built_in_param)
        else:
            print("No matching workset found for wall ID {}.".format(wall.Id))


# Document Changed Event Handler Wrapper
def document_changed_handler_wrapper(
    doc, workset_mapping, process_function, built_in_param
):
    """Create a handler function with access to the active document and workset mapping."""

    def on_document_changed(sender, args):
        """Handle newly created walls dynamically."""
        try:
            added_elements = args.GetAddedElementIds()
            if not added_elements:
                print("No added elements detected.")
                return

            print(
                "Document changed. Added elements count: {}".format(len(added_elements))
            )

            # Filter and process only walls
            walls = [
                doc.GetElement(elem_id)
                for elem_id in added_elements
                if doc.GetElement(elem_id).Category.Name == "Walls"
            ]
            process_function(doc, walls, workset_mapping, built_in_param)
        except Exception as e:
            print("Error in DocumentChanged handler: {}".format(e))

    return on_document_changed


# Subscribe to Document Changed Event
app = __revit__.Application
event_handler = document_changed_handler_wrapper(
    doc, WORKSET_MAPPING, process_walls, BuiltInParameter
)
app.DocumentChanged += event_handler

print("Dynamic Workset Automation (Ignore Thickness) activated.")
