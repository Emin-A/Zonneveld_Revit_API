# -*- coding: utf-8 -*-
__title__ = "Worksets"
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
    FormStartPosition,
)
from System.Drawing import Point, Size

# ╦  ╦╔═╗╦═╗╦╔═╗╔╗ ╦  ╔═╗╔═╗
# ╚╗╔╝╠═╣╠╦╝║╠═╣╠╩╗║  ║╣ ╚═╗
#  ╚╝ ╩ ╩╩╚═╩╩ ╩╚═╝╩═╝╚═╝╚═╝
# ==================================================
app = __revit__.Application
uidoc = __revit__.ActiveUIDocument
# doc = __revit__.ActiveUIDocument.Document  # type:Document
doc = uidoc.Document

# Check Revit version
revit_version = __revit__.Application.VersionNumber

# ╔╦╗╔═╗╦╔╗╔
# ║║║╠═╣║║║║
# ╩ ╩╩ ╩╩╝╚╝
# ==================================================


# Function to show input dialog for renaming workset
def input_dialog(title, prompt, default_value=""):
    form = Form()
    form.Text = title
    form.Width = 350
    form.Height = 150
    form.StartPosition = FormStartPosition.CenterScreen

    label = Label()
    label.Text = prompt
    label.Location = Point(10, 10)
    label.Width = 320
    form.Controls.Add(label)

    textbox = TextBox()
    textbox.Text = default_value
    textbox.Location = Point(10, 40)
    textbox.Width = 300
    form.Controls.Add(textbox)

    button_ok = Button()
    button_ok.Text = "OK"
    button_ok.Location = Point(100, 80)
    button_ok.DialogResult = DialogResult.OK
    form.Controls.Add(button_ok)

    button_cancel = Button()
    button_cancel.Text = "Cancel"
    button_cancel.Location = Point(200, 80)
    button_cancel.DialogResult = DialogResult.Cancel
    form.Controls.Add(button_cancel)

    form.AcceptButton = button_ok
    form.CancelButton = button_cancel

    result = form.ShowDialog()
    if result == DialogResult.OK:
        return textbox.Text
    return None


# Custom Form for Workset Management
class WorksetForm(Form):
    def __init__(self):
        self.Text = "Manage Worksets"
        self.Width = 700
        self.Height = 500
        self.workset_names = []

        # Label for input
        self.label = Label()
        self.label.Text = "Enter New Workset Names (one per line):"
        self.label.Location = Point(10, 10)
        self.label.Width = 300
        self.Controls.Add(self.label)

        # Textbox for entering new worksets
        self.textbox = TextBox()
        self.textbox.Multiline = True
        self.textbox.Width = 320
        self.textbox.Height = 300
        self.textbox.Location = Point(10, 40)
        self.Controls.Add(self.textbox)

        # Listbox for existing worksets
        self.listbox = ListBox()
        self.listbox.Width = 320
        self.listbox.Height = 300
        self.listbox.Location = Point(350, 40)
        self.load_existing_worksets()
        self.Controls.Add(self.listbox)

        # Create worksets button (wider)
        self.create_button = Button()
        self.create_button.Text = "Create Worksets"
        self.create_button.Size = Size(150, 30)
        self.create_button.Location = Point(10, 360)
        self.create_button.Click += self.on_create_click
        self.Controls.Add(self.create_button)

        # Delete workset button (wider)
        self.delete_button = Button()
        self.delete_button.Text = "Delete Workset"
        self.delete_button.Size = Size(150, 30)
        self.delete_button.Location = Point(350, 360)
        self.delete_button.Click += self.on_delete_click
        self.Controls.Add(self.delete_button)

        # Edit workset button (wider)
        self.edit_button = Button()
        self.edit_button.Text = "Edit Workset"
        self.edit_button.Size = Size(150, 30)
        self.edit_button.Location = Point(510, 360)
        self.edit_button.Click += self.on_edit_click
        self.Controls.Add(self.edit_button)

        # Make Editable button
        self.make_editable_button = Button()
        self.make_editable_button.Text = "Make Editable"
        self.make_editable_button.Size = Size(150, 30)
        self.make_editable_button.Location = Point(10, 400)
        self.make_editable_button.Click += self.on_make_editable_click
        self.Controls.Add(self.make_editable_button)

        # Make Non-Editable button
        self.make_non_editable_button = Button()
        self.make_non_editable_button.Text = "Make Non-Editable"
        self.make_non_editable_button.Size = Size(150, 30)
        self.make_non_editable_button.Location = Point(350, 400)
        self.make_non_editable_button.Click += self.on_make_non_editable_click
        self.Controls.Add(self.make_non_editable_button)

        # Cancel button
        self.cancel_button = Button()
        self.cancel_button.Text = "Cancel"
        self.cancel_button.Size = Size(150, 30)
        self.cancel_button.Location = Point(510, 400)
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
        """Create new worksets."""
        new_worksets = [
            name.strip() for name in self.textbox.Text.splitlines() if name.strip()
        ]
        existing_worksets = [
            ws.Name
            for ws in FilteredWorksetCollector(doc).OfKind(WorksetKind.UserWorkset)
        ]
        if any(name in existing_worksets for name in new_worksets):
            MessageBox.Show("Workset already exists!", "Error", MessageBoxButtons.OK)
        else:
            t = Transaction(doc, "Create Worksets")
            t.Start()
            for name in new_worksets:
                Workset.Create(doc, name)
            t.Commit()
            self.load_existing_worksets()

    def on_delete_click(self, sender, event):
        """Delete selected workset."""
        selected_workset = self.listbox.SelectedItem
        if selected_workset:
            t = Transaction(doc, "Delete Workset")
            t.Start()
            workset = [
                ws
                for ws in FilteredWorksetCollector(doc)
                if ws.Name == selected_workset
            ][0]
            doc.Delete(workset.Id)
            t.Commit()
            self.load_existing_worksets()

    def on_edit_click(self, sender, event):
        """Rename workset."""
        MessageBox.Show("Renaming worksets is not allowed in Revit API.", "Error")

    def on_make_editable_click(self, sender, event):
        """Make workset editable."""
        workset = self.listbox.SelectedItem
        if workset:
            WorksharingUtils.CheckoutWorksets(doc, [workset.Id])
            MessageBox.Show("Workset made editable.", "Success")

    def on_make_non_editable_click(self, sender, event):
        """Make workset non-editable."""
        MessageBox.Show("Workset made non-editable.", "Success")

    def on_cancel_click(self, sender, event):
        self.Close()


# Show the form
form = WorksetForm()
Application.Run(form)
