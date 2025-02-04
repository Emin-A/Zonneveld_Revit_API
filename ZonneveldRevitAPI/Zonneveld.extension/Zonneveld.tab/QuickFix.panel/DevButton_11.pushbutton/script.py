__title__ = "Select Same \n Category "
__doc__ = """Selects all elements in the current project that belong to the same category as the selected element."""

from Autodesk.Revit.DB import *
from Autodesk.Revit.DB import (
    FilteredElementCollector,
    FamilyInstanceFilter,
    ElementId,
    Transaction,
    BuiltInCategory,
)
from pyrevit import revit, forms
from System.Collections.Generic import List

# Access Revit document

uidoc = revit.uidoc
doc = revit.doc

# uidoc = __revit__.ActiveUIDocument
# doc = uidoc.Document
app = __revit__.Application
doc = __revit__.ActiveUIDocument.Document


import clr

clr.AddReference("System")
clr.AddReference("RevitAPI")
clr.AddReference("RevitAPIUI")
clr.AddReference("RevitServices")
clr.AddReference("RevitNodes")
clr.AddReference("System.Windows.Forms")
clr.AddReference("System.Drawing")
clr.AddReference("System.Collections")


# Debug flag: set to False to disable logs
DEBUG = False


def debug_log(message):
    """Helper function to print debug messages."""
    if DEBUG:
        print(message)


def get_selected_category():
    """Get the category of the selected element."""
    selection = uidoc.Selection.GetElementIds()
    if not selection:
        forms.alert(
            "Please select an element to continue.",
            title="No Selection",
            exitscript=True,
        )
    selected_element = doc.GetElement(selection[0])
    return selected_element.Category if selected_element else None


def select_by_category(category):
    """Select all elements of the same category as the provided category."""
    collector = (
        FilteredElementCollector(doc)
        .OfCategoryId(category.Id)
        .WhereElementIsNotElementType()
    )
    elements_to_select = [el.Id for el in collector]

    if elements_to_select:
        uidoc.Selection.SetElementIds(List[ElementId](elements_to_select))
        uidoc.RefreshActiveView()
        forms.alert(
            "Selected {} elements of category: {}".format(
                len(elements_to_select), category.Name
            ),
            title="Selection Complete",
        )
    else:
        forms.alert(
            "No elements found for the selected category.", title="No Elements Found"
        )


# Main execution
category = get_selected_category()
if category:
    select_by_category(category)
