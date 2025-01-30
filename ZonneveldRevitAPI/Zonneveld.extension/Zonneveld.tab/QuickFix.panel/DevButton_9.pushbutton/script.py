# -*- coding: utf-8 -*-
__title__ = "Create \n Worksets"
__doc__ = """Version = 1.0
Date    = 20.12.2024
________________________________________________________________
Description:

Create custom worksets using user-provided names.

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
from Autodesk.Revit.DB import (
    Workset,
    Transaction,
    FilteredWorksetCollector,
    WorksetKind,
    # WorksetId,
    # WorksetTable,
    # WorksharingUtils,
    # ElementId,
    # RelinquishOptions,
)

# .NET Imports
import clr

clr.AddReference("System")
clr.AddReference("RevitAPI")
clr.AddReference("RevitAPIUI")
clr.AddReference("System.Windows.Forms")
clr.AddReference("System.Drawing")

from System.Windows.Forms import (
    Application,
    Button,
    Form,
    Label,
    TextBox,
    ListBox,
    MessageBox,
    MessageBoxButtons,
    MessageBoxIcon,
    DialogResult,
    FormBorderStyle,
    FormStartPosition,
)
from System.Drawing import Point, Size

# ╦  ╦╔═╗╦═╗╦╔═╗╔╗ ╦  ╔═╗╔═╗
# ╚╗╔╝╠═╣╠╦╝║╠═╣╠╩╗║  ║╣ ╚═╗
#  ╚╝ ╩ ╩╩╚═╩╩ ╩╚═╝╩═╝╚═╝╚═╝
# ==================================================
# app = __revit__.Application
# doc = __revit__.ActiveUIDocument.Document  # type:Document
uidoc = __revit__.ActiveUIDocument
doc = uidoc.Document

# Check Revit version
# revit_version = __revit__.Application.VersionNumber

# ╔╦╗╔═╗╦╔╗╔
# ║║║╠═╣║║║║
# ╩ ╩╩ ╩╩╝╚╝
# ==================================================


# Function to show input dialog for creating a workset
def input_dialog(title, prompt, default_value=""):
    form = Form()
    form.Text = title
    form.Width = 400
    form.Height = 180
    form.StartPosition = FormStartPosition.CenterScreen
    form.FormBorderStyle = FormBorderStyle.FixedDialog  # Non-resizable window

    label = Label()
    label.Text = prompt
    label.Location = Point(10, 10)
    label.Width = 360
    form.Controls.Add(label)

    textbox = TextBox()
    textbox.Text = default_value
    textbox.Location = Point(10, 40)
    textbox.Width = 360
    form.Controls.Add(textbox)

    button_ok = Button()
    button_ok.Text = "OK"
    button_ok.Location = Point(80, 90)
    button_ok.DialogResult = DialogResult.OK
    form.Controls.Add(button_ok)

    button_cancel = Button()
    button_cancel.Text = "Cancel"
    button_cancel.Location = Point(200, 90)
    button_cancel.DialogResult = DialogResult.Cancel
    form.Controls.Add(button_cancel)

    form.AcceptButton = button_ok
    form.CancelButton = button_cancel

    result = form.ShowDialog()
    if result == DialogResult.OK:
        return textbox.Text
    return None


# Workset management form
class WorksetForm(Form):
    def __init__(self):
        self.Text = "Manage Worksets"
        self.Width = 500
        self.Height = 450
        self.StartPosition = FormStartPosition.CenterScreen
        self.FormBorderStyle = FormBorderStyle.FixedDialog  # Non-resizable window

        # Label for existing worksets
        self.label = Label()
        self.label.Text = "Existing Worksets:"
        self.label.Location = Point(10, 10)
        self.label.Width = 200
        self.Controls.Add(self.label)

        # Listbox for displaying existing worksets
        self.listbox = ListBox()
        self.listbox.Width = 460
        self.listbox.Height = 300
        self.listbox.Location = Point(10, 40)
        self.load_existing_worksets()
        self.Controls.Add(self.listbox)

        # Create workset button
        self.create_button = Button()
        self.create_button.Text = "Create Workset"
        self.create_button.Size = Size(150, 30)
        self.create_button.Location = Point(30, 360)
        self.create_button.Click += self.on_create_click
        self.Controls.Add(self.create_button)

        # Cancel button
        self.cancel_button = Button()
        self.cancel_button.Text = "Cancel"
        self.cancel_button.Size = Size(150, 30)
        self.cancel_button.Location = Point(250, 360)
        self.cancel_button.Click += self.on_cancel_click
        self.Controls.Add(self.cancel_button)

    def load_existing_worksets(self):
        """Load existing worksets into the listbox."""
        self.listbox.Items.Clear()
        existing_worksets = [
            ws.Name
            for ws in FilteredWorksetCollector(doc).OfKind(WorksetKind.UserWorkset)
        ]
        for ws in existing_worksets:
            self.listbox.Items.Add(ws)

    def on_create_click(self, sender, event):
        """Create a new workset."""
        workset_name = input_dialog("Create Workset", "Enter new workset name:")
        if workset_name:
            t = Transaction(doc, "Create Workset")
            t.Start()
            try:
                Workset.Create(doc, workset_name)
                t.Commit()
                MessageBox.Show(
                    "Workset '{}' created successfully.".format(workset_name), "Success"
                )
                self.load_existing_worksets()
            except Exception as e:
                t.RollBack()
                MessageBox.Show(
                    "Error creating workset: " + str(e),
                    "Error",
                    MessageBoxButtons.OK,
                    MessageBoxIcon.Error,
                )

    def on_cancel_click(self, sender, event):
        """Close the form."""
        self.Close()


# Run the form
form = WorksetForm()
Application.Run(form)
