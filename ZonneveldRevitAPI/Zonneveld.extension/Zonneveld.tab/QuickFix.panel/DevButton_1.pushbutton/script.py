# -*- coding: utf-8 -*-
__title__ = "Automation"
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
# ╩╩ ╩╩  ╚═╝╩╚═ ╩ ╚═╝
# ==================================================
from Autodesk.Revit.DB import *

# .NET Imports
import clr

clr.AddReference("System")
from System.Collections.Generic import List


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


# 🤖 Automate Your Boring Work Here


# ==================================================
# 🚫 DELETE BELOW
from Snippets._customprint import (
    kit_button_clicked,
)  # Import Reusable Function from 'lib/Snippets/_customprint.py'

kit_button_clicked(btn_name=__title__)  # Display Default Print Message
