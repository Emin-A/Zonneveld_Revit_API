# -*- coding: utf-8 -*-
__title__ = "Create \n Print Set"
__doc__ = """Create a print set from selected views in the Revit model."""

from Autodesk.Revit.DB import (
    Transaction,
    FilteredElementCollector,
    PrintRange,
    View,
    ViewSet,
    ViewSheetSet,
)
from pyrevit import revit, forms, script

# Access Revit document
doc = revit.doc
uidoc = revit.uidoc
logger = script.get_logger()

# Step 1: Collect all views in the document
all_views = (
    FilteredElementCollector(doc)
    .OfClass(View)
    .WhereElementIsNotElementType()
    .ToElements()
)

# Filter out template views
available_views = [view for view in all_views if not view.IsTemplate]

# Step 2: Open a selection window for views
selected_views = forms.SelectFromList.show(
    sorted(available_views, key=lambda v: v.ViewType.ToString() + ": " + v.Name),
    title="Select Views for Print Set",
    multiselect=True,
    name_attr="Name",
)

# Exit if no views are selected
if not selected_views:
    forms.alert("No views selected. Print set creation cancelled.", exitscript=True)

# Step 3: Ask the user for a print set name
print_set_name = forms.ask_for_string(
    prompt="Enter a name for the print set (default is 'ViewPrintSet').",
    title="Print Set Name",
    default="ViewPrintSet",
)

if not print_set_name:
    forms.alert("Print set creation cancelled. No name provided.", exitscript=True)

# Step 4: Prepare the print manager and view sheet setting
print_manager = doc.PrintManager
print_manager.PrintRange = PrintRange.Select
view_sheet_setting = print_manager.ViewSheetSetting

# Convert selected views to a ViewSet
view_set = ViewSet()
for view in selected_views:
    view_set.Insert(view)

# Step 5: Check for existing print sets and create the new one
existing_print_sets = {
    vss.Name: vss
    for vss in FilteredElementCollector(doc)
    .OfClass(ViewSheetSet)
    .WhereElementIsNotElementType()
    .ToElements()
}

with Transaction(doc, "Create Print Set") as transaction:
    transaction.Start()

    # Delete existing print set with the same name
    if print_set_name in existing_print_sets:
        view_sheet_setting.CurrentViewSheetSet = existing_print_sets[print_set_name]
        view_sheet_setting.Delete()
        logger.info("Deleted existing print set: " + print_set_name)

    # Create and save the new print set
    view_sheet_setting.CurrentViewSheetSet.Views = view_set
    view_sheet_setting.SaveAs(print_set_name)
    transaction.Commit()

forms.alert("Print set '" + print_set_name + "' created successfully.")
