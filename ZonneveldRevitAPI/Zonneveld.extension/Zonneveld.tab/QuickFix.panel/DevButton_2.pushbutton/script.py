# -*- coding: utf-8 -*-
__title__ = "Auto Params"
__doc__ = """Version = 1.0
Date    = 09.01.2025
________________________________________________________________
Description:

This is the placeholder for a .pushbutton
You can use it to start your pyRevit Add-In

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
from pyrevit import forms

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
rvt_year = int(app.VersionNumber)


# ╔╦╗╔═╗╦╔╗╔
# ║║║╠═╣║║║║
# ╩ ╩╩ ╩╩╝╚╝
# ==================================================

# Accress SharedParameterFiles ( you need to have the shared parameter file path set)
sp_file = app.OpenSharedParameterFile()
if not sp_file:
    forms.alert(
        "Shared parameter File not found. Add the Shared Parameter File in Revit and try again."
    )

# Sort All Parameters from SharedParameterFile
dict_shared_params = {}
for group in sp_file.Groups:
    for p_def in group.Definitions:
        combined_name = "[{}]_{}".format(group.Name, p_def.Name)
        dict_shared_params[combined_name] = p_def

# 1. Use pyRevit Forms to choose SharedParameters
selected_p_names = forms.SelectFromList.show(
    sorted(dict_shared_params.keys()), button_name="Select Parameters", multiselect=True
)
selected_param_defs = [dict_shared_params[p_name] for p_name in selected_p_names]

# Print Selected Parametes
# print(selected_p_names)
# print(selected_param_defs)

# 2. Select Categories and create CategorySet
cat_set = app.Create.NewCategorySet()
cat_view = Category.GetCategory(doc, BuiltInCategory.OST_Views)
cat_wall = Category.GetCategory(doc, BuiltInCategory.OST_Walls)
cat_set.Insert(cat_view)
cat_set.Insert(cat_wall)

# 3. Create Instance or Type Binding
new_instance_binding = app.Create.NewInstanceBinding(cat_set)
# new_type_binding = app.Create.NewTypeBinding(cat_set)

# 4. Select Parameter Group
# parameter_group = (
#     BuiltInParameterGroup.PG_ANALYSIS_RESULTS
# )  # This works find until RVT 2024
# parameter_group = GroupTypeId.AnalysisResults  # works on RVT 2024+
if rvt_year >= 2024:
    parameter_group = GroupTypeId.AnalysisResults  # works on RVT 2024+
else:
    parameter_group = (
        BuiltInParameterGroup.PG_ANALYSIS_RESULTS
    )  # works on lower than RVT 2024

# 5. Add Parameters
t = Transaction(doc, "Add Shared Parameters")
t.Start()  # Start transaction

# Iterate through Parameter Groups and Parameter Definitions
for p_def in selected_param_defs:
    try:
        doc.ParameterBindings.Insert(p_def, new_instance_binding, parameter_group)
        print("✅Added Parameter: {}".format(p_def.Name))
    except:
        print("❌Failed to add {}".format(p_def.Name))

t.Commit()  # Commit transaction
