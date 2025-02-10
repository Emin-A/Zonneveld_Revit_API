# -*- coding: utf-8 -*-
__title__ = "Export Point\nCloud Data"
__doc__ = """Extract scan paths, transform data, and prepare for external processing."""

import json
import os
from pyrevit import revit, DB, forms, script

# Logger setup
logger = script.get_logger()

# Step 1: Collect Point Cloud Data
doc = revit.doc
point_clouds = (
    DB.FilteredElementCollector(doc).OfClass(DB.PointCloudInstance).ToElements()
)

if not point_clouds:
    forms.alert("No point cloud found in the project.", exitscript=True)

exported_data = []

for cloud in point_clouds:
    try:
        # Extract scan details
        scans = list(cloud.GetScans())  # Get the scan names
        regions = list(cloud.GetRegions())  # May not contain regions always

        # Extract transformation data
        transform = cloud.GetTotalTransform()
        transform_data = {
            "origin": [transform.Origin.X, transform.Origin.Y, transform.Origin.Z],
            "basis_x": [transform.BasisX.X, transform.BasisX.Y, transform.BasisX.Z],
            "basis_y": [transform.BasisY.X, transform.BasisY.Y, transform.BasisY.Z],
            "basis_z": [transform.BasisZ.X, transform.BasisZ.Y, transform.BasisZ.Z],
            "scale": transform.Scale,
        }

        # Export point cloud details
        exported_data.append(
            {
                "name": cloud.Name,
                "scans": scans,
                "regions": regions,
                "color_supported": cloud.HasColor(),
                "transform": transform_data,
            }
        )

        logger.info("Extracted data for point cloud: {}".format(cloud.Name))
    except Exception as ex:
        logger.warning("Failed to access point cloud data: " + str(ex))

# Step 2: Export Data to JSON
output_file = "C:\\Zonneveld\\temp\\point_cloud_data_with_transform.json"
with open(output_file, "w") as file:
    json.dump(exported_data, file, indent=4)

forms.alert("Point cloud data exported with transform information to: " + output_file)
