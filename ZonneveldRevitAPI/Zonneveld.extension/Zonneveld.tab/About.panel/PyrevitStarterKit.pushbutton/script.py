# -*- coding: utf-8 -*-
__title__ = "Zonneveld V1.0"
__doc__ = """Version = 1.0
Date    = 22.11.2024
____________________________________________
Description:
Zonneveld Toolbar About Form
____________________________________________
How-To:
- Click the Button
____________________________________________
Last update:
- [22.11.2024] - V1.0 RELEASE
____________________________________________
Author: Emin Avdovic"""


# ╦╔╦╗╔═╗╔═╗╦═╗╔╦╗╔═╗
# ║║║║╠═╝║ ║╠╦╝ ║ ╚═╗
# ╩╩ ╩╩  ╚═╝╩╚═ ╩ ╚═╝ IMPORTS
# ====================================================================================================
# from pyrevit.coreutils import (
#     get_pyrevit_version,
#     get_ironpython_version,
#     get_cpython_version,
# )
import os
import sys

VENV_PATH = r"C:\Zonneveld\Zonneveld_Revit_API\.venv\Lib\site-packages"
if VENV_PATH not in sys.path:
    sys.path.append(VENV_PATH)

# Path to pyrevitlib
PYREVIT_LIB_PATH = r"C:\Users\bim3d\AppData\Roaming\pyRevit-Master\pyrevitlib"
if PYREVIT_LIB_PATH not in sys.path:
    sys.path.append(PYREVIT_LIB_PATH)

# venv_path = os.path.join(os.path.dirname(__file__), ".venv", "Lib", "site-packages")
# sys.path.append(venv_path)
from Autodesk.Revit.DB import *
from Autodesk.Revit.UI import TaskDialog
from pyrevit import EXEC_PARAMS
from pyrevit import (
    forms,
)  # By importing forms you also get references to WPF package! Very IMPORTANT
import wpf  # wpf can be imported only after pyrevit.forms!
import clr

# pyRevit imports
# from pyrevit.pyutils import get_pyrevit_version

# .NET Imports
clr.AddReference("System")
from System.Collections.Generic import List
from System.Windows import Application, Window, ResourceDictionary
from System.Windows.Controls import CheckBox, Button, TextBox, ListBoxItem
from System.Diagnostics.Process import Start
from System.Windows.Window import DragMove
from System.Windows.Input import MouseButtonState
from System import Uri

# ╦  ╦╔═╗╦═╗╦╔═╗╔╗ ╦  ╔═╗╔═╗
# ╚╗╔╝╠═╣╠╦╝║╠═╣╠╩╗║  ║╣ ╚═╗
#  ╚╝ ╩ ╩╩╚═╩╩ ╩╚═╝╩═╝╚═╝╚═╝ VARIABLES
# ====================================================================================================
PATH_SCRIPT = os.path.dirname(__file__)
uidoc = __revit__.ActiveUIDocument
app = __revit__.Application
doc = __revit__.ActiveUIDocument.Document  # type: Document


# This function is now defined globally
def get_pyrevit_version():
    return os.getenv("PYREVIT_VERSION", "Unknown")


# Extract environment variables
pyrevit_version = get_pyrevit_version()
cpy_version = os.getenv("PYREVIT_CPYVERSION", "Unknown")
ipy_version = os.getenv("PYREVIT_IPYVERSION", "Unknown")


# ╔═╗╦  ╔═╗╔═╗╔═╗╔═╗╔═╗
# ║  ║  ╠═╣╚═╗╚═╗║╣ ╚═╗
# ╚═╝╩═╝╩ ╩╚═╝╚═╝╚═╝╚═╝
# ====================================================================================================
class ListItem:
    """Helper Class for defining items in the ListBox."""

    def __init__(self, Name="Unnamed", element=None, checked=False):
        self.Name = Name
        self.IsChecked = checked
        self.element = element

    def __str__(self):
        return self.Name


# ╔╦╗╔═╗╦╔╗╔  ╔═╗╔═╗╦═╗╔╦╗
# ║║║╠═╣║║║║  ╠╣ ║ ║╠╦╝║║║
# ╩ ╩╩ ╩╩╝╚╝  ╚  ╚═╝╩╚═╩ ╩ MAIN FORM
# ====================================================================================================
class AboutForm(Window):

    def __init__(self):
        # Connect to .xaml File (in same folder)
        path_xaml_file = os.path.join(PATH_SCRIPT, "AboutUI.xaml")
        wpf.LoadComponent(self, path_xaml_file)

        # Fetch compatibility information
        self.populate_compatibility_info()

        # Show Form
        self.ShowDialog()

    def populate_compatibility_info(self):
        """Fetch and display pyRevit, IronPython, CPython versions and compatibility info."""
        # Get Revit version
        revit_version = app.VersionNumber

        try:
            # Fetch pyRevit environment versions
            pyrevit_version = getattr(
                EXEC_PARAMS, "pyrevit_version", get_pyrevit_version()
            )
        except Exception:
            pyrevit_version = get_pyrevit_version()
        try:
            ironpython_version = getattr(EXEC_PARAMS, "ironpython_version", "Unknown")
        except AttributeError:
            ironpython_version = "Unknown"
        try:
            cpython_version = getattr(EXEC_PARAMS, "cpython_version", "Unknown")
        except AttributeError:
            cpython_version = "Unknown"

        # Compatibility check messages
        compatibility_message = f"Revit Version: {revit_version}\n"
        compatibility_message += f"pyRevit Version: {pyrevit_version}\n"
        compatibility_message += f"IronPython Version: {ironpython_version}\n"
        compatibility_message += f"CPython Version: {cpython_version}\n"

        if revit_version in ["2021", "2022", "2023", "2024", "2025"]:
            compatibility_message += "Compatibility: ✅ Supported\n"
        else:
            compatibility_message += "Compatibility: ⚠️ Not officially supported\n"

        # Update the UI element (assumes a TextBox named 'CompatibilityText')
        self.CompatibilityText.Text = compatibility_message

    # ╔═╗╦  ╦╔═╗╔╗╔╔╦╗╔═╗
    # ║╣ ╚╗╔╝║╣ ║║║ ║ ╚═╗
    # ╚═╝ ╚╝ ╚═╝╝╚╝ ╩ ╚═╝
    # ====================================================================================================
    def button_close(self, sender, e):
        """Stop application by clicking on a <Close> button in the top right corner."""
        self.Close()

    def header_drag(self, sender, e):
        """Drag window by holding LeftButton on the header."""
        if e.LeftButton == MouseButtonState.Pressed:
            self.DragMove()

    def Hyperlink_RequestNavigate(self, sender, e):
        """Forwarding for a Hyperlinks."""
        Start(e.Uri.AbsoluteUri)

    def CheckCompatibility_Click(self, sender, e):
        """Handles the Check Compatibility button click event."""
        try:
            # Fetch updated compatibility information
            self.populate_compatibility_info()
            # Show a confirmation message
            forms.alert(
                "Compatibility information updated successfully.",
                title="Check Compatibility",
            )
        except Exception as ex:
            # Log the error instead of crashing
            forms.alert(
                f"Error fetching compatibility info: {ex}", title="pyRevitStarterKit"
            )
            print(f"Error: {ex}")


# print(f"pyRevit Version: {pyrevit_version}")
# print(f"CPython Version: {cpy_version}")
# print(f"IronPython Version: {ipy_version}")
# print(f"pyRevit Version: {get_pyrevit_version()}")
# print(dir(EXEC_PARAMS))

# Uncomment the following for debugging (log to file if needed)
with open("debug_log.txt", "w") as log:
    log.write(f"pyRevit Version: {pyrevit_version}\n")
    log.write(f"CPython Version: {cpy_version}\n")
    log.write(f"IronPython Version: {ipy_version}\n")
    log.write(f"pyRevit Version: {get_pyrevit_version()}\n")
    log.write(str(dir(EXEC_PARAMS)))


# ╦ ╦╔═╗╔═╗  ╔═╗╔═╗╦═╗╔╦╗
# ║ ║╚═╗║╣   ╠╣ ║ ║╠╦╝║║║
# ╚═╝╚═╝╚═╝  ╚  ╚═╝╩╚═╩ ╩
# ====================================================================================================

# Show form to the user
UI = AboutForm()
