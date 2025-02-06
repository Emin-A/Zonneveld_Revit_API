# -*- coding: utf-8 -*-
__title__ = "Run AI Analysis (Debug v4)"
__doc__ = """Script to collect point cloud metadata using supported methods."""

import json
import os
from pyrevit import revit, DB, forms, script

# Set up logger
logger = script.get_logger()

# Step 1: Export Point Cloud Data
doc = revit.doc
point_clouds = (
    DB.FilteredElementCollector(doc).OfClass(DB.PointCloudInstance).ToElements()
)

if not point_clouds:
    forms.alert("No point cloud found in the project.", exitscript=True)

# Create output directory if not exists
output_dir = "C:\\Zonneveld\\temp"
if not os.path.exists(output_dir):
    os.makedirs(output_dir)

exported_data = []

# Collect metadata for each point cloud
for cloud in point_clouds:
    logger.info("Inspecting point cloud: {}".format(cloud.Name))
    cloud_data = {
        "name": cloud.Name,
        "regions": [],
        "scans": [],
        "color_supported": cloud.HasColor(),  # Call HasColor() correctly to get a boolean
    }

    # Fetch regions if available
    try:
        regions = cloud.GetRegions()
        if regions:
            cloud_data["regions"] = list(regions)
    except Exception as e:
        logger.warning(
            "Could not retrieve regions for cloud {}: {}".format(cloud.Name, e)
        )

    # Fetch scans if available
    try:
        scans = cloud.GetScans()
        if scans:
            cloud_data["scans"] = list(scans)
    except Exception as e:
        logger.warning(
            "Could not retrieve scans for cloud {}: {}".format(cloud.Name, e)
        )

    # Export pathname parameter (if found)
    try:
        pathname_param = cloud.LookupParameter("PathName")
        if pathname_param and pathname_param.HasValue:
            cloud_data["path"] = pathname_param.AsString()
    except Exception as e:
        logger.warning(
            "Could not retrieve pathname for cloud {}: {}".format(cloud.Name, e)
        )

    exported_data.append(cloud_data)

# Write data to JSON
export_file = os.path.join(output_dir, "point_cloud_data_debug_v4.json")
with open(export_file, "w") as file:
    json.dump(exported_data, file, indent=4)

# Check export results
if not exported_data:
    forms.alert("No valid point cloud data found. Export failed.", exitscript=True)
else:
    forms.alert("Point cloud metadata exported successfully. Check the debug JSON.")
