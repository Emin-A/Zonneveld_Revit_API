# -*- coding: utf-8 -*-
from pyrevit.forms import WPFWindow, toast, alert
import platform
import sys


class AboutForm:
    def __init__(self):
        try:
            # Load the AboutUI.xaml
            self.window = WPFWindow("AboutUI.xaml")
            toast("Window initialized successfully.")

            # Fetch versions
            self.version_data = self.fetch_versions()

            # Bind Check Compatibility button
            self.window.CheckCompatibility.Click += self.check_compatibility

            # Update the UI with versions
            self.update_ui()

            # Show the window
            self.window.show()
        except Exception as ex:
            alert("Initialization Error: {}".format(ex), title="Error")

    def fetch_versions(self):
        """Fetch all version details safely."""
        try:
            # Fetch Revit Version
            revit_version = __revit__.Application.VersionNumber

            # Fetch pyRevit Version
            try:
                import pyrevit

                pyrevit_version = pyrevit.__version__
            except Exception:
                pyrevit_version = "Not Detected"

            # Fetch IronPython and CPython versions
            ironpython_version = (
                platform.python_version()
                if "IronPython" in sys.version
                else "Not Detected"
            )
            cpython_version = (
                platform.python_version()
                if "CPython" in platform.python_implementation()
                else "Not Detected"
            )

            return {
                "Revit": revit_version,
                "pyRevit": pyrevit_version,
                "IronPython": ironpython_version,
                "CPython": cpython_version,
            }
        except Exception as ex:
            alert("Error fetching versions: {}".format(ex), title="Error")
            return {}

    def update_ui(self):
        """Update the UI elements with fetched versions."""
        self.window.RevitVersionText.Text = "Revit Version: {}".format(
            self.version_data.get("Revit", "Unknown")
        )
        self.window.pyRevitVersionText.Text = "pyRevit Version: {}".format(
            self.version_data.get("pyRevit", "Unknown")
        )
        self.window.IronPythonVersionText.Text = "IronPython Version: {}".format(
            self.version_data.get("IronPython", "Unknown")
        )
        self.window.CPythonVersionText.Text = "CPython Version: {}".format(
            self.version_data.get("CPython", "Unknown")
        )
        self.window.CompatibilityText.Text = "Compatibility Information Displayed."

    def check_compatibility(self, sender, e):
        """Check compatibility and display a single toast notification."""
        try:
            toast("Checking Compatibility...")

            # Fetch versions
            self.version_data = self.fetch_versions()

            # Combine all version info into one toast message
            version_info = (
                "Revit Version: {}\n"
                "pyRevit Version: {}\n"
                "IronPython Version: {}\n"
                "CPython Version: {}"
            ).format(
                self.version_data.get("Revit", "Not Detected"),
                self.version_data.get("pyRevit", "Not Detected"),
                self.version_data.get("IronPython", "Not Detected"),
                self.version_data.get("CPython", "Not Detected"),
            )

            # Display the combined toast notification
            toast(version_info)

            # Update the UI
            self.update_ui()
        except Exception as ex:
            alert("Error during compatibility check: {}".format(ex), title="Error")


TestWindow = AboutForm()
