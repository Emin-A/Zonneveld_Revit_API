# -*- coding: utf-8 -*-
from pyrevit.forms import WPFWindow


class AboutForm:
    def __init__(self):
        try:
            # Load the AboutUI.xaml
            self.window = WPFWindow("AboutUI.xaml")

            # Attach event handlers programmatically
            self.window.FindName(
                "LogoImage"
            ).MouseLeftButtonDown += self.navigate_to_uri
            self.window.FindName("CloseButton").Click += self.button_close

            # Fetch versions
            self.version_data = self.fetch_versions()

            # Update the UI with versions
            self.update_ui()

            # Show the window
            self.window.show()
        except Exception as ex:
            # Log error in case of failure
            print("Initialization Error: {}".format(ex))

    def fetch_versions(self):
        """Fetch all version details."""
        try:
            # Revit Version
            revit_version = __revit__.Application.VersionNumber

            # Hardcoded pyRevit Version
            pyrevit_version = "4.8.16 (Hardcoded)"

            # Hardcoded IronPython and CPython Versions
            ironpython_version = "2.7.11 (Hardcoded)"
            cpython_version = "3.7.8 (Hardcoded)"

            # Add compatibility status
            ironpython_status = (
                "Supported"
                if ironpython_version == "2.7.11 (Hardcoded)"
                else "Experimental"
            )
            cpython_status = (
                "Supported"
                if cpython_version == "3.7.8 (Hardcoded)"
                else "Experimental"
            )

            return {
                "Revit": revit_version,
                "pyRevit": pyrevit_version,
                "IronPython": "{} ({})".format(ironpython_version, ironpython_status),
                "CPython": "{} ({})".format(cpython_version, cpython_status),
            }
        except Exception:
            return {
                "Revit": "Unknown",
                "pyRevit": "4.8.16 (Hardcoded)",
                "IronPython": "2.7.11 (Hardcoded) (Supported)",
                "CPython": "3.7.8 (Hardcoded) (Supported)",
            }

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

    def navigate_to_uri(self, sender, e):
        """Open the company website."""
        try:
            # Import webbrowser locally
            import webbrowser

            webbrowser.open("https://www.zonneveld.com")
        except Exception as ex:
            # Suppress and  debug output here
            pass

    def button_close(self, sender, e):
        """Close the About window."""
        self.window.Close()


# Run the form
if __name__ == "__main__":
    AboutForm()
