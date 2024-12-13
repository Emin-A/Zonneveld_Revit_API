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
import platform
import re

# venv_path = os.path.join(os.path.dirname(__file__), ".venv", "Lib", "site-packages")
# sys.path.append(venv_path)
from Autodesk.Revit.DB import *
from Autodesk.Revit.UI import TaskDialog

# from Autodesk.Revit.UI import UIApplication
from pyrevit import EXEC_PARAMS
from pyrevit import (
    forms,
)  # By importing forms you also get refereces to WPF package! Very IMPORTANT

# from pyrevit import HOST_APP
# from pyrevit import versionmgr
import wpf  # wpf can be imported only after pyrevit.forms!
import clr


# pyRevit imports
# from pyrevit.pyutils import get_pyrevit_version

# .NET Imports
clr.AddReference("System")
# clr.AddReference("System.Windows.Forms")
# clr.AddReference("System.Drawing")
# from System.Windows.Forms import Form, Label, Button, DockStyle
# from System.Drawing import Point, Size, Font, FontStyle, Color
from System.Collections.Generic import List
from System.Windows import Application, Window, ResourceDictionary
from System.Windows.Controls import CheckBox, Button, TextBox, ListBoxItem
from System.Diagnostics.Process import Start
from System.Windows.Window import DragMove
from System.Windows.Input import MouseButtonState
from System import Uri

VENV_PATH = r"C:\Zonneveld\Zonneveld_Revit_API\.venv\Lib\site-packages"
if VENV_PATH not in sys.path:
    sys.path.append(VENV_PATH)

# Path to pyrevitlib
PYREVIT_LIB_PATH = r"C:\Users\bim3d\AppData\Roaming\pyRevit-Master\pyrevitlib"
if PYREVIT_LIB_PATH not in sys.path:
    sys.path.append(PYREVIT_LIB_PATH)


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


def get_environment_variable(var_name, default="Unknown"):
    return os.getenv(var_name, default)


# Extract environment variables
pyrevit_version = get_pyrevit_version()
cpy_version = get_environment_variable("PYREVIT_CPYVERSION")
ipy_version = get_environment_variable("PYREVIT_IPYVERSION")


# ╔═╗╦  ╔═╗╔═╗╔═╗╔═╗╔═╗
# ║  ║  ╠═╣╚═╗╚═╗║╣ ╚═╗
# ╚═╝╩═╝╩ ╩╚═╝╚═╝╚═╝╚═╝
# ====================================================================================================
# class ListItem:
#     """Helper Class for defining items in the ListBox."""

#     def __init__(self, Name="Unnamed", element=None, checked=False):
#         self.Name = Name
#         self.IsChecked = checked
#         self.element = element

#     def __str__(self):
#         return self.Name


# ╔╦╗╔═╗╦╔╗╔  ╔═╗╔═╗╦═╗╔╦╗
# ║║║╠═╣║║║║  ╠╣ ║ ║╠╦╝║║║
# ╩ ╩╩ ╩╩╝╚╝  ╚  ╚═╝╩╚═╩ ╩ MAIN FORM
# ====================================================================================================


# class AboutWindow(Form):
#     def __init__(self):
#         self.Text = "About Plugin"
#         self.Size = Size(400, 300)
#         self.StartPosition = 0  # Center the window
#         self.FormBorderStyle = 1  # Fixed dialog

#         self.initialize_components()

#     def initialize_components(self):
#         title_label = Label()
#         title_label.Text = "Plugin Information"
#         title_label.Font = Font("Arial", 12, FontStyle.Bold)
#         title_label.AutoSize = True
#         title_label.Location = Point(20, 20)
#         self.Controls.Add(title_label)

#         self.revit_version_label = Label()
#         self.revit_version_label.Text = self.get_revit_version()
#         self.revit_version_label.Location = Point(20, 60)
#         self.Controls.Add(self.revit_version_label)

#         self.pyrevit_version_label = Label()
#         self.pyrevit_version_label.Text = self.get_pyrevit_version()
#         self.pyrevit_version_label.Location = Point(20, 90)
#         self.Controls.Add(self.pyrevit_version_label)

#         self.ironpython_version_label = Label()
#         self.ironpython_version_label.Text = self.get_ironpython_version()
#         self.ironpython_version_label.Location = Point(20, 120)
#         self.Controls.Add(self.ironpython_version_label)

#         self.cpython_version_label = Label()
#         self.cpython_version_label.Text = self.get_cpython_version()
#         self.cpython_version_label.Location = Point(20, 150)
#         self.Controls.Add(self.cpython_version_label)

#         self.check_button = Button()
#         self.check_button.Text = "Check Compatibility"
#         self.check_button.Location = Point(20, 200)
#         self.check_button.Click += self.check_compatibility
#         self.Controls.Add(self.check_button)

#     def get_revit_version(self):
#         uiapp = UIApplication(HOST_APP.app)
#         revit_version = uiapp.Application.VersionNumber
#         return f"Revit Version: {revit_version}"

#     def get_pyrevit_version(self):
#         try:
#             pyrevit_version = versionmgr.get_installed_pyrevit_version()
#             if pyrevit_version:
#                 return f"pyRevit Version: {pyrevit_version} (✅ Supported)"
#             else:
#                 return f"pyRevit Version: Unknown (⚠️ Not Supported)"
#         except Exception:
#             return f"pyRevit Version: Unknown (⚠️ Not Supported)"

#     def get_ironpython_version(self):
#         try:
#             ironpython_version = platform.python_version()
#             if "IronPython" in sys.version:
#                 return f"IronPython Version: {ironpython_version} (✅ Supported)"
#             else:
#                 return f"IronPython Version: Unknown (⚠️ Not Supported)"
#         except Exception:
#             return f"IronPython Version: Unknown (⚠️ Not Supported)"

#     def get_cpython_version(self):
#         try:
#             if "CPython" in platform.python_implementation():
#                 cpython_version = platform.python_version()
#                 return f"CPython Version: {cpython_version} (✅ Supported)"
#             else:
#                 return f"CPython Version: Unknown (⚠️ Not Supported)".format()

#     def check_compatibility(self, sender, event):
#         from System.Windows.Forms import MessageBox
#         MessageBox.Show("Compatibility information updated successfully.")


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

        def get_accurate_version(var_name, version_checker):
            """Helper function to get version and check support."""
            version = get_environment_variable(var_name, version_checker())
            return version

        # Version checkers
        def check_pyrevit_version():
            try:
                import pyrevit

                return pyrevit.__version__
            except Exception:
                return "Not Detected"

        def check_ironpython_version():
            if "IronPython" in sys.version:
                return platform.python_version()
            return "Not Detected"

        def check_cpython_version():
            if "CPython" in platform.python_implementation():
                return platform.python_version()
            return "Not Detected"

        compatibility_info = [
            (
                "Revit Version",
                revit_version,
                revit_version in ["2021", "2022", "2023", "2024", "2025"],
            ),
            (
                "pyRevit Version",
                get_accurate_version("PYREVIT_VERSION", check_pyrevit_version),
                get_environment_variable("PYREVIT_VERSION") != "Unknown",
            ),
            (
                "IronPython Version",
                get_accurate_version("PYREVIT_IPYVERSION", check_ironpython_version),
                "IronPython" in sys.version,
            ),
            (
                "CPython Version",
                get_accurate_version("PYREVIT_CPYVERSION", check_cpython_version),
                "CPython" in platform.python_implementation(),
            ),
        ]

        # try:
        #     # Fetch pyRevit environment versions
        #     pyrevit_version = getattr(
        #         EXEC_PARAMS, "pyrevit_version", get_pyrevit_version()
        #     )
        # except Exception:
        #     pyrevit_version = get_pyrevit_version()
        # try:
        #     ironpython_version = getattr(EXEC_PARAMS, "ironpython_version", "Unknown")
        # except AttributeError:
        #     ironpython_version = "Unknown"
        # try:
        #     cpython_version = getattr(EXEC_PARAMS, "cpython_version", "Unknown")
        # except AttributeError:
        #     cpython_version = "Unknown"

        # Build compatibility message
        compatibility_message = ""
        for name, version, is_supported in compatibility_info:
            status = "✅ Supported" if is_supported else "⚠️ Not Supported"
            compatibility_message += f"{name}: {version} ({status})\n"

        # compatibility_message = f"Revit Version: {revit_version}\n"
        # compatibility_message += f"pyRevit Version: {pyrevit_version}\n"
        # compatibility_message += f"IronPython Version: {ironpython_version}\n"
        # compatibility_message += f"CPython Version: {cpython_version}\n"

        # if revit_version in ["2021", "2022", "2023", "2024", "2025"]:
        #     compatibility_message += "Compatibility: ✅ Supported\n"
        # else:
        #     compatibility_message += "Compatibility: ⚠️ Not officially supported\n"

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
            # print(f"Error: {ex}")


# print(f"pyRevit Version: {pyrevit_version}")
# print(f"CPython Version: {cpy_version}")
# print(f"IronPython Version: {ipy_version}")
# print(f"pyRevit Version: {get_pyrevit_version()}")
# print(dir(EXEC_PARAMS))

# Uncomment the following for debugging (log to file if needed)
# with open("debug_log.txt", "w") as log:
#     log.write(f"pyRevit Version: {pyrevit_version}\n")
#     log.write(f"CPython Version: {cpy_version}\n")
#     log.write(f"IronPython Version: {ipy_version}\n")
#     log.write(f"pyRevit Version: {get_pyrevit_version()}\n")
#     log.write(str(dir(EXEC_PARAMS)))


# ╦ ╦╔═╗╔═╗  ╔═╗╔═╗╦═╗╔╦╗
# ║ ║╚═╗║╣   ╠╣ ║ ║╠╦╝║║║
# ╚═╝╚═╝╚═╝  ╚  ╚═╝╩╚═╩ ╩
# ====================================================================================================

# Show form to the user
UI = AboutForm()
# form = AboutWindow()
# form.ShowDialog()
