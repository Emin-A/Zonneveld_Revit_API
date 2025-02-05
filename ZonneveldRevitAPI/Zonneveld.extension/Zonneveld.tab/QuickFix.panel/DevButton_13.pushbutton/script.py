# -*- coding: utf-8 -*-
__title__ = "Purge \n Unused"
__doc__ = """Unified purge tool combining Revit's built-in purge and custom wipes."""

from pyrevit import revit, DB, forms, script
from pyrevit import DB, UI
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


# Function to execute Revit's built-in Purge Unused command
def purge_unused_families_and_types():
    """Executes Revit's built-in Purge Unused command."""
    try:
        purge_command_id = UI.RevitCommandId.LookupPostableCommandId(
            UI.PostableCommand.PurgeUnused
        )
        revit.app.PostCommand(purge_command_id)
        print("✅ Revit's built-in Purge Unused executed.")
    except Exception as e:
        logger.error("Failed to execute built-in purge: {}".format(str(e)))


# Function to remove constraints
def purge_all_constraints():
    """Remove all constraints."""
    try:
        constraints = (
            FilteredElementCollector(doc)
            .OfCategory(BuiltInCategory.OST_Constraints)
            .ToElements()
        )
        with revit.Transaction("Purge All Constraints"):
            for constraint in constraints:
                try:
                    if constraint.IsValidObject:
                        doc.Delete(constraint.Id)
                        debug_log("Deleted Constraint ID: {}".format(constraint.Id))
                except Exception as e:
                    logger.error("Failed to delete constraint: {}".format(e))
    except Exception as e:
        logger.error("Error during constraints purge: {}".format(str(e)))


# Function to remove empty elevation markers
def purge_empty_elevation_markers():
    """Remove all empty elevation markers."""
    try:
        elevation_markers = (
            FilteredElementCollector(doc).OfClass(ElevationMarker).ToElements()
        )
        with revit.Transaction("Purge Empty Elevation Markers"):
            for marker in elevation_markers:
                try:
                    if marker.CurrentViewCount == 0 and marker.IsValidObject:
                        doc.Delete(marker.Id)
                        debug_log("Deleted Elevation Marker ID: {}".format(marker.Id))
                except Exception as e:
                    logger.error("Failed to delete elevation marker: {}".format(e))
    except Exception as e:
        logger.error("Error during elevation marker purge: {}".format(str(e)))


# Function to remove unused filters
def purge_unused_filters():
    """Remove all unused filters."""
    try:
        views = (
            FilteredElementCollector(doc)
            .OfClass(View)
            .WhereElementIsNotElementType()
            .ToElements()
        )
        filters = (
            FilteredElementCollector(doc).OfClass(ParameterFilterElement).ToElements()
        )

        used_filters = set()
        all_filters = set(filter_elem.Id.IntegerValue for filter_elem in filters)

        for view in views:
            if view.AreGraphicsOverridesAllowed():
                for filter_id in view.GetFilters():
                    used_filters.add(filter_id.IntegerValue)

        unused_filters = all_filters - used_filters

        if unused_filters:
            with revit.Transaction("Purge Unused Filters"):
                for filter_id in unused_filters:
                    try:
                        doc.Delete(ElementId(filter_id))
                        debug_log("Deleted Unused Filter ID: {}".format(filter_id))
                    except Exception as e:
                        logger.error("Failed to delete filter: {}".format(e))
        else:
            print("All filters are in use.")
    except Exception as e:
        logger.error("Error during filter purge: {}".format(str(e)))


# Function to remove unused view templates
def purge_unused_view_templates():
    """Remove all unused view templates."""
    try:
        views = (
            FilteredElementCollector(doc)
            .OfClass(View)
            .WhereElementIsNotElementType()
            .ToElements()
        )

        template_ids = set(view.Id.IntegerValue for view in views if view.IsTemplate)
        used_template_ids = set(
            view.ViewTemplateId.IntegerValue
            for view in views
            if not view.IsTemplate and view.ViewTemplateId.IntegerValue != -1
        )

        unused_template_ids = template_ids - used_template_ids

        if unused_template_ids:
            with revit.Transaction("Purge Unused View Templates"):
                for template_id in unused_template_ids:
                    try:
                        doc.Delete(ElementId(template_id))
                        debug_log(
                            "Deleted Unused View Template ID: {}".format(template_id)
                        )
                    except Exception as e:
                        logger.error("Failed to delete view template: {}".format(e))
        else:
            print("All view templates are in use.")
    except Exception as e:
        logger.error("Error during view template purge: {}".format(str(e)))


# Function to purge unused viewport types
def purge_unused_viewport_types():
    """Remove all unused viewport types."""
    try:
        viewport_types = [
            vt
            for vt in FilteredElementCollector(doc).OfClass(ElementType)
            if vt.FamilyName == "Viewport"
        ]

        with revit.Transaction("Purge Unused Viewport Types"):
            for viewport_type in viewport_types:
                try:
                    if viewport_type.IsValidObject:
                        doc.Delete(viewport_type.Id)
                        debug_log(
                            "Deleted Viewport Type ID: {}".format(viewport_type.Id)
                        )
                except Exception as e:
                    logger.error("Failed to delete viewport type: {}".format(e))
    except Exception as e:
        logger.error("Error during viewport type purge: {}".format(str(e)))


# Function to remove unused subcategories
def purge_unused_subcategories():
    """Remove all unused subcategories."""
    try:
        subcategories = revit.query.get_subcategories(doc=doc, purgable=True)

        with revit.Transaction("Purge Unused SubCategories"):
            for subcat in subcategories:
                try:
                    doc.Delete(subcat.Id)
                    debug_log("Deleted SubCategory ID: {}".format(subcat.Id))
                except Exception as e:
                    logger.error("Failed to delete subcategory: {}".format(e))
    except Exception as e:
        logger.error("Error during subcategory purge: {}".format(str(e)))


# Main execution
if __name__ == "__main__":
    purge_options = {
        "All Constraints": purge_all_constraints,
        "Empty Elevation Markers": purge_empty_elevation_markers,
        "Unused Families & Types": purge_unused_families_and_types,
        "Unused Filters": purge_unused_filters,
        "Unused View Templates": purge_unused_view_templates,
        "Unused Viewport Types": purge_unused_viewport_types,
        "Unused SubCategories": purge_unused_subcategories,
    }

    selected_option = forms.SelectFromList.show(
        sorted(purge_options.keys()),
        title="Select Purge Options",
        multiselect=True,
    )

    if selected_option:
        for option in selected_option:
            purge_action = purge_options.get(option)
            if purge_action:
                purge_action()
