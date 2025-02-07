# -*- coding: utf-8 -*-
__title__ = "AI \n Analysis"
__doc__ = """Pipeline to export, analyze, and import AI-detected features from point clouds."""

import json
import subprocess
import os
from pyrevit import revit, DB, forms, script

# Define paths
python_executable = "C:\\Zonneveld\\Zonneveld_Revit_API\\.venv\\Scripts\\python.exe"
external_script_path = "C:\\Zonneveld\\Zonneveld_Revit_API\\analyze_point_cloud.py"

# Logger
logger = script.get_logger()

# Step 1: Export Point Cloud Metadata
doc = revit.doc
point_clouds = (
    DB.FilteredElementCollector(doc).OfClass(DB.PointCloudInstance).ToElements()
)

exported_data = []
for cloud in point_clouds:
    try:
        scans = cloud.GetScans()
        regions = cloud.GetRegions()
        exported_data.append(
            {
                "name": cloud.Name,
                "scans": list(scans),
                "regions": list(regions),
                "color_supported": bool(cloud.HasColor()),
            }
        )
    except Exception as ex:
        logger.warning("Failed to access point cloud metadata: " + str(ex))

if not exported_data:
    forms.alert("No valid point cloud data found. Export failed.", exitscript=True)

# Save metadata to file
metadata_file = "C:\\Zonneveld\\temp\\point_cloud_data_debug.json"
with open(metadata_file, "w") as file:
    json.dump(exported_data, file, indent=4)

forms.alert("Point cloud metadata exported successfully.")

# Step 2: Run External Feature Detection Script
try:
    process = subprocess.Popen(
        [python_executable, external_script_path],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )
    stdout, stderr = process.communicate()

    # Log the output and errors from the external script
    logger.info("External script STDOUT: " + stdout.decode("utf-8"))
    logger.error("External script STDERR: " + stderr.decode("utf-8"))

    if process.returncode != 0:
        forms.alert(
            "External script execution failed. Check the logs for details.",
            exitscript=True,
        )
except Exception as e:
    logger.error("Failed to run external script: " + str(e))
    forms.alert("Failed to run external feature detection script.", exitscript=True)

# Step 3: Import Detected Features into Revit
input_file = "C:\\Zonneveld\\temp\\detected_features.json"
if not os.path.exists(input_file):
    forms.alert(
        "No detected features found. Ensure the external script ran successfully.",
        exitscript=True,
    )

with open(input_file, "r") as file:
    detected_data = json.load(file)

# Step 4: Process Detected Features
for feature in detected_data.get("detected_features", []):
    if feature["type"] == "Plane":
        plane_equation = feature["equation"]
        num_points = feature["num_points"]

        # Provide simple feedback for detected planes
        forms.alert(
            "Detected Plane: {}x + {}y + {}z + {} = 0 with {} points".format(
                plane_equation[0],
                plane_equation[1],
                plane_equation[2],
                plane_equation[3],
                num_points,
            )
        )

forms.alert("AI feature import completed.")
