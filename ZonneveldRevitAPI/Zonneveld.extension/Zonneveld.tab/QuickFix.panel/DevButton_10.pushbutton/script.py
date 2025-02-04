# -*- coding: utf-8 -*-
__title__ = "Batch \n Sheet "
__doc__ = """Create sheets or placeholder sheets from a user-provided list."""

from Autodesk.Revit.DB import *
from pyrevit import revit
from pyrevit import forms

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
clr.AddReference("System.Windows.Forms")
clr.AddReference("System.Drawing")


# Debug flag: set to False to disable logs
DEBUG = False


def debug_log(message):
    """Log debug messages if DEBUG is enabled."""
    if DEBUG:
        print(message)


# Function to get title blocks
def get_title_blocks():
    """Retrieve all title blocks in the document."""
    titleblocks = (
        FilteredElementCollector(doc)
        .OfCategory(BuiltInCategory.OST_TitleBlocks)
        .WhereElementIsElementType()
        .ToElements()
    )

    # Use LookupParameter to get names instead of direct property access
    titleblock_dict = {}
    for tb in titleblocks:
        family_name = tb.FamilyName
        type_name_param = tb.LookupParameter("Type Name")
        type_name = type_name_param.AsString() if type_name_param else "Unnamed"
        key = "{}: {}".format(family_name, type_name)
        titleblock_dict[key] = tb
        debug_log("Found Title Block: {}".format(key))

    return titleblock_dict


# Function to create a placeholder sheet
def create_placeholder(sheet_num, sheet_name):
    """Create a placeholder sheet in the Revit document."""
    try:
        with Transaction(doc, "Create Placeholder Sheet") as t:
            t.Start()
            new_ph_sheet = ViewSheet.CreatePlaceholder(doc)
            new_ph_sheet.Name = sheet_name
            new_ph_sheet.SheetNumber = sheet_num
            t.Commit()
            debug_log("✅ Placeholder created: {} - {}".format(sheet_num, sheet_name))
    except Exception as e:
        debug_log(
            "❌ Failed to create placeholder: {} - {} | Error: {}".format(
                sheet_num, sheet_name, e
            )
        )


# Function to create a sheet with a title block
def create_sheet(sheet_num, sheet_name, titleblock_id):
    """Create a sheet with a title block in the Revit document."""
    try:
        with Transaction(doc, "Create Sheet") as t:
            t.Start()
            new_sheet = ViewSheet.Create(doc, titleblock_id)
            new_sheet.Name = sheet_name
            new_sheet.SheetNumber = sheet_num
            t.Commit()
            debug_log("✅ Sheet created: {} - {}".format(sheet_num, sheet_name))
    except Exception as e:
        debug_log(
            "❌ Failed to create sheet: {} - {} | Error: {}".format(
                sheet_num, sheet_name, e
            )
        )


# Main execution
if __name__ == "__main__":
    # Get user input for sheet names and numbers
    sheet_input = forms.ask_for_string(
        prompt="Enter sheet numbers and names separated by a tab or spaces (e.g., 'A101 Floor Plan'). One per line.",
        title="Enter Sheet Data",
        multiline=True,
    )

    if not sheet_input:
        forms.alert(
            "No input provided. Exiting script.", title="No Input", exitscript=True
        )

    # Parse sheet data
    sheet_data = {}
    for line in sheet_input.splitlines():
        # Normalize whitespace and validate the line
        line = line.strip()
        if "\t" in line:
            sheet_num, sheet_name = map(str.strip, line.split("\t", 1))
        elif " " in line:
            sheet_num, sheet_name = map(
                str.strip, line.split(None, 1)
            )  # Split on first space
        else:
            continue

        if sheet_num and sheet_name:
            sheet_data[sheet_num] = sheet_name

    if not sheet_data:
        forms.alert(
            "No valid sheet data provided. Ensure each line has a tab or spaces separating the number and name.",
            title="Invalid Data",
            exitscript=True,
        )

    # Ask user whether to create placeholders or full sheets
    create_type = forms.alert(
        "Choose sheet creation type:",
        options=["Create Placeholder Sheets", "Create Sheets with Title Block"],
        exitscript=True,
    )

    # Handle sheet creation based on user choice
    if create_type == "Create Placeholder Sheets":
        for sheet_num, sheet_name in sheet_data.items():
            create_placeholder(sheet_num, sheet_name)
    else:
        # Ask for title block selection
        titleblocks = get_title_blocks()
        if not titleblocks:
            forms.alert(
                "No title blocks found in the document. Exiting script.",
                exitscript=True,
            )

        selected_titleblock = forms.SelectFromList.show(
            sorted(titleblocks.keys()), title="Select Title Block", multiselect=False
        )
        if not selected_titleblock:
            forms.alert("No title block selected. Exiting script.", exitscript=True)

        titleblock_id = titleblocks[selected_titleblock].Id

        # Create sheets with the selected title block
        for sheet_num, sheet_name in sheet_data.items():
            create_sheet(sheet_num, sheet_name, titleblock_id)
