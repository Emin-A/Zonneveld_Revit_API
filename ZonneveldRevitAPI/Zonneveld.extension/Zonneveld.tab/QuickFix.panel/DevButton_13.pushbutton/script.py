# -*- coding: utf-8 -*-
__title__ = "Super \n Purge"
__doc__ = """Combines Revit's Purge Unused with pyRevit's Wipe features."""

from pyrevit import revit, DB, forms, script
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
logger = script.get_logger()


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


#  Purge/Wipe Functions


def run_revit_purge_unused():
    """Run Revit's built-in Purge Unused command."""
    purge_cmd_id = DB.RevitCommandId.LookupPostableCommandId(
        DB.PostableCommand.PurgeUnused
    )
    if purge_cmd_id and revit.app.CanPostCommand(purge_cmd_id):
        revit.app.PostCommand(purge_cmd_id)
    else:
        forms.alert("Revit's Purge Unused command is not available.")


def wipe_unused_filters():
    """Wipe unused parameter filters."""
    filters = (
        DB.FilteredElementCollector(doc).OfClass(DB.ParameterFilterElement).ToElements()
    )
    views = DB.FilteredElementCollector(doc).OfClass(DB.View).ToElements()

    used_filters = {
        filter_id.IntegerValue for v in views for filter_id in v.GetFilters()
    }
    unused_filters = {f.Id.IntegerValue for f in filters} - used_filters

    if not unused_filters:
        forms.alert("No unused filters found.")
        return

    with revit.Transaction("Purge Unused Filters"):
        for filter_id in unused_filters:
            try:
                doc.Delete(DB.ElementId(filter_id))
                debug_log("Deleted Filter: {}".format(filter_id))
            except Exception as e:
                logger.error("Error deleting filter: {} | {}".format(filter_id, e))


def wipe_unused_view_templates():
    """Wipe unused view templates."""
    views = DB.FilteredElementCollector(doc).OfClass(DB.View).ToElements()
    template_ids = {v.Id.IntegerValue for v in views if v.IsTemplate}
    used_templates = {
        v.ViewTemplateId.IntegerValue
        for v in views
        if v.ViewTemplateId.IntegerValue > 0
    }

    unused_templates = template_ids - used_templates

    if not unused_templates:
        forms.alert("No unused view templates found.")
        return

    with revit.Transaction("Purge Unused View Templates"):
        for template_id in unused_templates:
            try:
                doc.Delete(DB.ElementId(template_id))
                debug_log("Deleted View Template: {}".format(template_id))
            except Exception as e:
                logger.error(
                    "Error deleting view template: {} | {}".format(template_id, e)
                )


def wipe_elevation_markers():
    """Wipe empty elevation markers."""
    markers = DB.FilteredElementCollector(doc).OfClass(DB.ElevationMarker).ToElements()
    empty_markers = [m for m in markers if m.CurrentViewCount == 0]

    if not empty_markers:
        forms.alert("No empty elevation markers found.")
        return

    with revit.Transaction("Purge Empty Elevation Markers"):
        for marker in empty_markers:
            try:
                doc.Delete(marker.Id)
                debug_log("Deleted Elevation Marker: {}".format(marker.Id))
            except Exception as e:
                logger.error(
                    "Error deleting elevation marker: {} | {}".format(marker.Id, e)
                )


def remove_all_constraints():
    """Remove all attached constraints."""
    constraints = (
        DB.FilteredElementCollector(doc)
        .OfCategory(DB.BuiltInCategory.OST_Constraints)
        .ToElements()
    )

    if not constraints:
        forms.alert("No constraints found.")
        return

    with revit.Transaction("Remove All Constraints"):
        for constraint in constraints:
            try:
                doc.Delete(constraint.Id)
                debug_log("Deleted Constraint: {}".format(constraint.Id))
            except Exception as e:
                logger.error(
                    "Error deleting constraint: {} | {}".format(constraint.Id, e)
                )


# Define Purge Options and User Interface
purge_actions = {
    "Unused Families & Types": run_revit_purge_unused,
    "Unused Filters": wipe_unused_filters,
    "Unused View Templates": wipe_unused_view_templates,
    "Empty Elevation Markers": wipe_elevation_markers,
    "All Constraints": remove_all_constraints,
}

# Ask user to select purge options
selected_actions = forms.SelectFromList.show(
    sorted(purge_actions.keys()),
    title="Select Purge Options",
    multiselect=True,
    button_name="Run Purge",
)

if not selected_actions:
    forms.alert("No purge options selected. Exiting.")
    script.exit()

# Execute Selected Purge Actions
for action_name in selected_actions:
    purge_action = purge_actions.get(action_name)
    if purge_action:
        try:
            purge_action()
            logger.info("Completed: {}".format(action_name))
        except Exception as e:
            logger.error("Error executing {}: {}".format(action_name, e))
