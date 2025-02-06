# -*- coding: utf-8 -*-
__title__ = "Run AI Analysis"
__doc__ = """Unified script to export, analyze, and import AI-detected features from point clouds."""

import json
import subprocess
import os
from pyrevit import revit, DB, forms, script

# Step 1: Export Point Cloud Data
doc = revit.doc
point_clouds = (
    DB.FilteredElementCollector(doc).OfClass(DB.PointCloudInstance).ToElements()
)
if not point_clouds:
    forms.alert("No point cloud found in the project.", exitscript=True)

exported_data = []
for cloud in point_clouds:
    # Correcting the access to the point cloud's origin point
    cloud_location = cloud.Location
    if isinstance(cloud_location, DB.LocationPoint):
        cloud_origin = cloud_location.Point
        cloud_data = {
            "name": cloud.Name,
            "origin": [cloud_origin.X, cloud_origin.Y, cloud_origin.Z],
        }
        exported_data.append(cloud_data)
    else:
        logger.warning(
            "Skipping point cloud with missing location data: {}".format(cloud.Id)
        )

export_file = "C:\\temp\\point_cloud_data.json"
with open(export_file, "w") as file:
    json.dump(exported_data, file, indent=4)

forms.alert("Point cloud data exported successfully.")

# Step 2: Run External Open3D Processing Script
external_script_path = "C:\\path_to_scripts\\analyze_point_cloud.py"
if not os.path.exists(external_script_path):
    forms.alert(
        "External script not found. Ensure the file path is correct.", exitscript=True
    )

subprocess.run(["python", external_script_path], check=True)

# Step 3: Import Detected Features Back into Revit
input_file = "C:\\temp\\detected_features.json"
if not os.path.exists(input_file):
    forms.alert(
        "No detected features found. Ensure the external script ran successfully."
    )
    exit()

with open(input_file, "r") as file:
    detected_data = json.load(file)

# Step 4: Process and create elements in Revit
for feature in detected_data["detected_features"]:
    if feature["type"] == "Plane":
        plane_equation = feature["equation"]
        num_points = feature["num_points"]
        equation_text = "{:.2f}x + {:.2f}y + {:.2f}z + {:.2f} = 0".format(
            *plane_equation
        )
        message = "Detected Plane: {} with {} points".format(equation_text, num_points)
        forms.alert(message)
