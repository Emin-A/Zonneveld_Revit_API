# -*- coding: utf-8 -*-
__title__ = "Custom Worksets"
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

from System.Collections.Generic import List
from System.Windows.Forms import Application, Button, Form, Label, TextBox, DialogResult
from System.Drawing import Point

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
# Custom Form for Workset Names
class WorksetForm(Form):
    def __init__(self):
        self.Text = "Create Worksets"
        self.Width = 300
        self.Height = 400
        self.workset_names = []

        self.label = Label()
        self.label.Text = "Enter Workset Names (one per line):"
        self.label.Location = Point(10, 10)
        self.label.Width = 260
        self.Controls.Add(self.label)

        self.textbox = TextBox()
        self.textbox.Multiline = True
        self.textbox.Width = 260
        self.textbox.Height = 250
        self.textbox.Location = Point(10, 40)
        self.Controls.Add(self.textbox)

        self.create_button = Button()
        self.create_button.Width = 100
        self.create_button.Text = "Create Worksets"
        self.create_button.Location = Point(10, 310)
        self.create_button.Click += self.on_create_click
        self.Controls.Add(self.create_button)

        self.cancel_button = Button()
        self.cancel_button.Text = "Cancel"
        self.cancel_button.Location = Point(160, 310)
        self.cancel_button.Click += self.on_cancel_click
        self.Controls.Add(self.cancel_button)

    def on_create_click(self, sender, event):
        self.workset_names = [
            name.strip() for name in self.textbox.Text.splitlines() if name.strip()
        ]
        self.DialogResult = DialogResult.OK
        self.Close()

    def on_cancel_click(self, sender, event):
        self.DialogResult = DialogResult.Cancel
        self.Close()


# Show the form
form = WorksetForm()
result = Application.Run(form)

if result == DialogResult.Cancel:
    print("Opreation cancelled by user.")
    sys.exit()

if form.workset_names:
    # Collect existing workset names
    existing_worksets = [
        ws.Name for ws in FilteredWorksetCollector(doc).OfKind(WorksetKind.UserWorkset)
    ]

    # Start Transaction
    t = Transaction(doc, "Create Custom Worksets")
    t.Start()

    created_worksets = []
    try:
        for name in form.workset_names:
            if name in existing_worksets:
                print("Workset '{0}' already exists. Skipping.".format(name))
            else:
                Workset.Create(doc, name)
                created_worksets.append(name)

        t.Commit()

        if created_worksets:
            print("Worksets created: {0}".format(", ".join(created_worksets)))
        else:
            print("No new worksets were created.")

    except Exception as e:
        t.RollBack()
        print("An error occurred: {0}".format(e))
else:
    print("No worksets were specified.")
