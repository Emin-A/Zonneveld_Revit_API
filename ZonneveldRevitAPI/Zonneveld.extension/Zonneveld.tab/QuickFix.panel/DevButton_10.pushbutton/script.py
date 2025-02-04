# -*- coding: utf-8 -*-
__title__ = "Batch \n Sheet "
__doc__ = """Create sheets or placeholder sheets from a user-provided list."""

from Autodesk.Revit.DB import *
from pyrevit import forms, revit

uidoc = __revit__.ActiveUIDocument
doc = uidoc.Document

# Access Revit document

doc = revit.doc


# Function to get title blocks
def get_title_blocks():
    """Retrieve all title blocks in the document."""
    titleblocks = (
        FilteredElementCollector(doc)
        .OfCategory(BuiltInCategory.OST_TitleBlocks)
        .WhereElementIsElementType()
        .ToElements()
    )
    return {tb.FamilyName + ": " + tb.Name: tb for tb in titleblocks}


# Function to create a placeholder sheet
def create_placeholder(sheet_num, sheet_name):
    """Create a placeholder sheet in the Revit document."""
    try:
        with Transaction(doc, "Create Placeholder Sheet"):
            new_ph_sheet = ViewSheet.CreatePlaceholder(doc)
            new_ph_sheet.Name = sheet_name
            new_ph_sheet.SheetNumber = sheet_num
        print("✅ Placeholder created: {0} - {1}".format(sheet_num, sheet_name))
    except Exception as e:
        print(
            "❌ Failed to create placeholder: {0} - {1} | Error: {2}".format(
                sheet_num, sheet_name, str(e)
            )
        )


# Function to create a sheet with a title block
def create_sheet(sheet_num, sheet_name, titleblock_id):
    """Create a sheet with a title block in the Revit document."""
    try:
        with Transaction(doc, "Create Sheet"):
            new_sheet = ViewSheet.Create(doc, titleblock_id)
            new_sheet.Name = sheet_name
            new_sheet.SheetNumber = sheet_num
        print("✅ Sheet created: {0} - {1}".format(sheet_num, sheet_name))
    except Exception as e:
        print(
            "❌ Failed to create sheet: {0} - {1} | Error: {2}".format(
                sheet_num, sheet_name, str(e)
            )
        )


# Main execution
if __name__ == "__main__":
    # Get user input for sheet names and numbers
    sheet_input = forms.ask_for_string(
        prompt="Enter sheet numbers and names separated by a tab (e.g., 'A101\tFloor Plan'). One per line.",
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
            if sheet_num and sheet_name:  # Ensure both parts are non-empty
                sheet_data[sheet_num] = sheet_name

    if not sheet_data:
        forms.alert(
            "No valid sheet data provided. Ensure each line has a tab separating the number and name.",
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
