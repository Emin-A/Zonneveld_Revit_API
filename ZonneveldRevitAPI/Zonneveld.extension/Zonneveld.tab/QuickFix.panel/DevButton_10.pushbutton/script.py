# -*- coding: utf-8 -*-
__title__ = "Select All Objects Of Selected Type"
__doc__ = """Version = 1.0
Date    = 17.01.2025
________________________________________________________________
Description:

Select all elements of the same type as the selected element.

________________________________________________________________
How-To:

1. [Hold ALT + CLICK] on the button to open its source folder.
You will be able to override this placeholder.

2. Automate Your Boring Work ;)

________________________________________________________________
TODO:
[FEATURE] - Describe Your ToDo Tasks Here
________________________________________________________________
Last Updates:
- [15.06.2024] v1.0 Change Description
- [10.06.2024] v0.5 Change Description
- [05.06.2024] v0.1 Change Description 
________________________________________________________________
Author: Emin Avdovic"""

# ╦╔╦╗╔═╗╔═╗╦═╗╔╦╗╔═╗
# ║║║║╠═╝║ ║╠╦╝ ║ ╚═╗
# ╩╩ ╩╩  ╚═╝╩╚═ ╩ ╚═╝
# ==================================================
from Autodesk.Revit.DB import *
from pyrevit import revit, DB
from pyrevit import forms

# .NET Imports
import clr

clr.AddReference("System")
from System.Collections.Generic import List


# ╦  ╦╔═╗╦═╗╦╔═╗╔╗ ╦  ╔═╗╔═╗
# ╚╗╔╝╠═╣╠╦╝║╠═╣╠╩╗║  ║╣ ╚═╗
#  ╚╝ ╩ ╩╩╚═╩╩ ╩╚═╝╩═╝╚═╝╚═╝
# ==================================================
app = __revit__.Application
uidoc = __revit__.ActiveUIDocument
doc = __revit__.ActiveUIDocument.Document  # type:Document


# ╔╦╗╔═╗╦╔╗╔
# ║║║╠═╣║║║║
# ╩ ╩╩ ╩╩╝╚╝
# ==================================================

# Get active selection
selection = revit.get_selection()
if not selection:
    forms.alert("At least one object must be selected.", exitscript=True)

filtered_elements = []
model_items = []
view_specific_items = []

# Process each selected element
for selected_element in selection:
    # Check if the element is view-specific
    is_view_specific = selected_element.ViewSpecific

    # Get the TypeId or LineStyle Id (for curve elements)
    if isinstance(selected_element, DB.CurveElement):
        type_id = selected_element.LineStyle.Id
    else:
        type_id = selected_element.GetTypeId()

    # Determine whether to filter by class or category
    by_class = category_id = None
    if isinstance(selected_element, DB.Dimension):
        by_class = DB.Dimension
    else:
        category_id = selected_element.Category.Id

    # Collect elements matching the class or category
    if by_class:
        same_type_elements = (
            DB.FilteredElementCollector(revit.doc)
            .OfClass(by_class)
            .WhereElementIsNotElementType()
            .ToElements()
        )
    else:
        same_type_elements = (
            DB.FilteredElementCollector(revit.doc)
            .OfCategoryId(category_id)
            .WhereElementIsNotElementType()
            .ToElements()
        )

    # Filter elements by type
    for element in same_type_elements:
        if isinstance(element, DB.CurveElement):
            element_type_id = element.LineStyle.Id
        else:
            element_type_id = element.GetTypeId()

        if element_type_id == type_id:
            filtered_elements.append(element.Id)

            # Group elements into view-specific or model items
            if is_view_specific:
                owner_view_id = element.OwnerViewId
                owner_view_name = revit.query.get_name(
                    revit.doc.GetElement(owner_view_id)
                )
                if owner_view_name in view_specific_items:
                    view_specific_items[owner_view_name].append(element)
                else:
                    view_specific_items[owner_view_name] = [element]
            else:
                model_items.append(element)

# Provide feedback
if len(filtered_elements) == 0:
    forms.alert("No matching elements found.", exitscript=True)

# Highlight elements in Revit
revit.get_selection().set_to(filtered_elements)

# Log results
if model_items:
    print("SELECTING MODEL ITEMS:")
    for model_element in model_items:
        print(
            "ID: {0} | Type: {1}".format(model_element.Id, model_element.GetType().Name)
        )

if view_specific_items:
    print("VIEW-SPECIFIC ITEMS:")
    for view_name, elements in view_specific_items.items():
        print("OWNER VIEW: {0}".format(view_name))
        for element in elements:
            print("ID: {0} | Type: {1}".format(element.Id, element.GetType().Name))
