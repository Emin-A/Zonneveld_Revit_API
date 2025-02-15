# -*- coding: utf-8 -*-
__title__ = "AI \n Massing"
__doc__ = """Pipeline to process AI-detected clusters and generate in-place massing in Revit."""

import json
import os
import subprocess
from pyrevit import revit, DB, forms, script

# Logger
logger = script.get_logger()

# File paths
temp_dir = "C:\\Zonneveld\\temp"
detected_features_path = os.path.join(temp_dir, "detected_features.json")
mass_family_name = "AI_Generated_Mass"

# Check detected features file
if not os.path.exists(detected_features_path):
    forms.alert(
        "No detected features found. Ensure AI analysis ran successfully.",
        exitscript=True,
    )

# Read detected features
with open(detected_features_path, "r") as file:
    detected_data = json.load(file)

clusters = detected_data.get("detected_features", [])

if not clusters:
    forms.alert("No valid clusters found.", exitscript=True)

# Start a transaction
doc = revit.doc
with DB.Transaction(doc, "Create AI-Generated In-Place Mass") as transaction:
    transaction.Start()

    mass_category = DB.Category.GetCategory(doc, DB.BuiltInCategory.OST_Mass)
    if not mass_category:
        raise Exception("Mass category is missing in the project.")

    # **Loop Through Clusters to Create Mass Geometry**
    for cluster in clusters:
        min_x, min_y, min_z = cluster["bounding_box"]["min"]
        max_x, max_y, max_z = cluster["bounding_box"]["max"]

        width = max_x - min_x
        depth = max_y - min_y
        height = max_z - min_z

        if width < 0.5 or depth < 0.5 or height < 0.5:
            logger.warning(
                "Skipped small cluster ID "
                + str(cluster["cluster_id"])
                + " due to size below Revit tolerance."
            )
            continue

        # Create the base rectangle
        base_curve_loop = DB.CurveLoop()
        base_curve_loop.Append(
            DB.Line.CreateBound(
                DB.XYZ(min_x, min_y, min_z), DB.XYZ(max_x, min_y, min_z)
            )
        )
        base_curve_loop.Append(
            DB.Line.CreateBound(
                DB.XYZ(max_x, min_y, min_z), DB.XYZ(max_x, max_y, min_z)
            )
        )
        base_curve_loop.Append(
            DB.Line.CreateBound(
                DB.XYZ(max_x, max_y, min_z), DB.XYZ(min_x, max_y, min_z)
            )
        )
        base_curve_loop.Append(
            DB.Line.CreateBound(
                DB.XYZ(min_x, max_y, min_z), DB.XYZ(min_x, min_y, min_z)
            )
        )

        # Create a mass form
        try:
            mass_form = DB.FreeFormElement.Create(doc, base_curve_loop)
            logger.info("Created mass for cluster ID " + str(cluster["cluster_id"]))
        except Exception as e:
            logger.warning(
                "Skipped cluster ID "
                + str(cluster["cluster_id"])
                + " due to error: "
                + str(e)
            )

    transaction.Commit()

forms.alert("Mass creation completed successfully!")
