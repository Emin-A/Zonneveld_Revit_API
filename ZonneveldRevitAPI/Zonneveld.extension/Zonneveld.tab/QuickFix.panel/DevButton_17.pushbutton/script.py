__title__ = "Adjust \nSheet Numbers"
__doc__ = """Shift the sheet numbers of selected sheets by a specified value."""

from pyrevit import revit, DB, forms, script

# Access Revit document
doc = revit.doc
# Logger setup
logger = script.get_logger()


# Helper function to increment/decrement sheet numbers
def adjust_sheet_number(sheet_number, shift_value):
    """Adjusts the numeric portion of the sheet number."""
    # Split into prefix and numeric part
    prefix = "".join([c for c in sheet_number if not c.isdigit()])
    numeric_part = "".join([c for c in sheet_number if c.isdigit()])

    if numeric_part:
        new_numeric_part = str(int(numeric_part) + shift_value).zfill(len(numeric_part))
        return prefix + new_numeric_part
    else:
        # If no numeric part is found, just return the original sheet number
        return sheet_number


# Step 1: Collect all sheets
all_sheets = (
    DB.FilteredElementCollector(revit.doc)
    .OfClass(DB.ViewSheet)
    .WhereElementIsNotElementType()
    .ToElements()
)

if not all_sheets:
    forms.alert("No sheets found in the project.", exitscript=True)

# Step 2: Show selection window
selected_sheets = forms.SelectFromList.show(
    [sheet.SheetNumber + " - " + sheet.Name for sheet in all_sheets],
    multiselect=True,
    title="Select Sheets to Adjust",
    button_name="Select Sheets",
)

if not selected_sheets:
    forms.alert("No sheets were selected. Exiting script.", exitscript=True)

# Step 3: Prompt for shift value
shift_value_str = forms.ask_for_string(
    prompt="Enter the shift value (e.g., 1 to increment or -1 to decrement):",
    title="Adjust Sheet Numbers",
)

if not shift_value_str or not shift_value_str.strip().lstrip("-").isdigit():
    forms.alert("Invalid shift value provided. Exiting script.", exitscript=True)

shift_value = int(shift_value_str.strip())

# Step 4: Map selected sheet names back to sheet elements
selected_sheet_elements = [
    sheet
    for sheet in all_sheets
    if sheet.SheetNumber + " - " + sheet.Name in selected_sheets
]

# Step 5: Sort sheets by current sheet number
sorted_sheets = sorted(selected_sheet_elements, key=lambda x: x.SheetNumber)

# Reverse sorting if decrementing to avoid conflicts
if shift_value > 0:
    sorted_sheets.reverse()

# Step 6: Apply the shift and update sheet numbers
with revit.Transaction("Adjust Sheet Numbers"):
    for sheet in sorted_sheets:
        try:
            current_number = sheet.SheetNumber
            new_number = adjust_sheet_number(current_number, shift_value)

            # Set new sheet number
            sheet_num_param = sheet.LookupParameter("Sheet Number")
            sheet_num_param.Set(new_number)

            logger.info(
                "Updated sheet number: {} -> {}".format(current_number, new_number)
            )
        except Exception as e:
            logger.error(
                "Failed to update sheet number for {}: {}".format(sheet.SheetNumber, e)
            )

    revit.doc.Regenerate()

# Final message
forms.alert("Sheet numbers adjusted successfully.")
