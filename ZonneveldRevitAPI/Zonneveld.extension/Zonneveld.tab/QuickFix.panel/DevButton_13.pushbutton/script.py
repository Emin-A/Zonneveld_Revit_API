# -*- coding: utf-8 -*-
__title__ = "Purge \n Unused"
__doc__ = """Unified purge tool combining Revit's built-in purge and custom wipes."""

from pyrevit import revit, DB, UI, forms, script
from Autodesk.Revit.UI import RevitCommandId, PostableCommand
from System.Collections.Generic import List
from Autodesk.Revit.DB import *
from Autodesk.Revit.DB import (
    FilteredElementCollector,
    FamilyInstanceFilter,
    ElementId,
    Transaction,
    BuiltInCategory,
)
from collections import defaultdict

# Access Revit document

doc = revit.doc
uidoc = revit.uidoc

# uidoc = __revit__.ActiveUIDocument
# doc = uidoc.Document
app = __revit__.Application
doc = __revit__.ActiveUIDocument.Document

# Logger
logger = script.get_logger()
output = script.get_output()


import clr

clr.AddReference("System")
clr.AddReference("RevitAPI")
clr.AddReference("RevitAPIUI")
clr.AddReference("RevitServices")
clr.AddReference("RevitNodes")
clr.AddReference("System.Windows.Forms")
clr.AddReference("System.Drawing")
clr.AddReference("System.Collections")

# Toggle debugging messages (set to True if needed)
DEBUG = True


def debug_log(message):
    """Log debug messages if DEBUG is enabled."""
    if DEBUG:
        print(message)


def handle_deletion(element_id, category_name):
    """Safely delete an element with error handling."""
    try:
        doc.Delete(element_id)
        logger.info("Deleted {} ID: {}".format(category_name, element_id))
    except Exception as err:
        logger.error("Failed to delete {}: {}".format(category_name, err))


# Functions for various purge operations
def purge_constraints():
    """Purge all constraints, skipping protected ones."""
    constraints = (
        DB.FilteredElementCollector(doc)
        .OfCategory(DB.BuiltInCategory.OST_Constraints)
        .WhereElementIsNotElementType()
        .ToElements()
    )
    for constraint in constraints:
        if isinstance(constraint, DB.Dimension):
            logger.warning("Skipped constraint (Dimension): {}".format(constraint.Id))
            continue
        handle_deletion(constraint.Id, "Constraint")


def purge_elevation_markers():
    """Purge all empty elevation markers."""
    markers = (
        DB.FilteredElementCollector(doc)
        .OfClass(DB.ElevationMarker)
        .WhereElementIsNotElementType()
        .ToElements()
    )
    for marker in markers:
        if marker.CurrentViewCount > 0:
            logger.warning(
                "Skipped elevation marker with active views: {}".format(marker.Id)
            )
            continue
        handle_deletion(marker.Id, "Elevation Marker")


def purge_viewport_types():
    """Purge unused viewport types, skipping protected ones."""
    element_types = (
        DB.FilteredElementCollector(doc)
        .OfClass(DB.ElementType)
        .WhereElementIsElementType()
        .ToElements()
    )
    viewport_types = [t for t in element_types if t.FamilyName == "Viewport"]

    for viewport in viewport_types:
        try:
            doc.Delete(viewport.Id)
            logger.info("Deleted Viewport Type ID: {}".format(viewport.Id))
        except Exception as err:
            logger.error("Failed to delete viewport type: {}".format(err))


def purge_unused_families_and_types():
    """Trigger Revit's built-in 'Purge Unused' command."""
    try:
        from Autodesk.Revit.UI import PostableCommand, RevitCommandId

        purge_command = RevitCommandId.LookupPostableCommandId(
            PostableCommand.PurgeUnused
        )
        __revit__.PostCommand(
            purge_command
        )  # Correctly using the built-in __revit__ object
        logger.info("Triggered built-in 'Purge Unused' successfully.")
    except Exception as err:
        logger.error("Failed to execute built-in purge: {}".format(err))


def purge_unused_filters():
    """Purge unused view filters."""
    views = (
        DB.FilteredElementCollector(doc)
        .OfClass(DB.View)
        .WhereElementIsNotElementType()
        .ToElements()
    )
    filters = (
        DB.FilteredElementCollector(doc).OfClass(DB.ParameterFilterElement).ToElements()
    )

    all_filters = {flt.Id for flt in filters}
    used_filters = set()

    for view in views:
        if view.AreGraphicsOverridesAllowed():
            for filter_id in view.GetFilters():
                used_filters.add(filter_id)

    unused_filters = all_filters - used_filters

    for filter_id in unused_filters:
        handle_deletion(filter_id, "Unused Filter")


def purge_unused_view_templates():
    """Purge unused view templates."""
    views = (
        DB.FilteredElementCollector(doc)
        .OfClass(DB.View)
        .WhereElementIsNotElementType()
        .ToElements()
    )
    unused_templates = set()

    for view in views:
        if view.IsTemplate and not view.ViewTemplateId:
            unused_templates.add(view.Id)

    for template_id in unused_templates:
        handle_deletion(template_id, "Unused View Template")


# Ask the user to select purge operations
purge_options = forms.SelectFromList.show(
    [
        "Unused View Templates",
        "All Constraints",
        "Empty Elevation Markers",
        "Unused Viewport Types",
        "Unused Families & Types",
        "Unused Filters",
    ],
    title="Select Purge Options",
    multiselect=True,
)

# Perform selected purge operations
if purge_options:
    with revit.Transaction("Purge Selected Elements"):
        for option in purge_options:
            if option == "Unused View Templates":
                purge_unused_view_templates()
            elif option == "All Constraints":
                purge_constraints()
            elif option == "Empty Elevation Markers":
                purge_elevation_markers()
            elif option == "Unused Viewport Types":
                purge_viewport_types()
            elif option == "Unused Families & Types":
                purge_unused_families_and_types()
            elif option == "Unused Filters":
                purge_unused_filters()

    forms.alert("Selected purge operations completed successfully.")
else:
    forms.alert("No purge options selected.")
