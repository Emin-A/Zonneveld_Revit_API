# -*- coding: utf-8 -*-
__title__ = "AI \n Massing"
__doc__ = """Pipeline to export, analyze, and import AI-detected features from point clouds."""

import json
import os
import subprocess
from pyrevit import revit, DB, forms, script

# Logger
logger = script.get_logger()

# Paths
detected_features_file = "C:\\Zonneveld\\temp\\detected_features.json"

if not os.path.exists(detected_features_file):
    forms.alert(
        "No detected features found. Ensure the AI analysis ran successfully.",
        exitscript=True,
    )

# Load detected clusters
with open(detected_features_file, "r") as file:
    detected_data = json.load(file)

clusters = detected_data.get("detected_features", [])

if not clusters:
    forms.alert("No valid clusters found in the detected features.", exitscript=True)

doc = revit.doc

# Ensure Massing Mode is Enabled
try:
    doc.Settings.MassMode = True
except Exception as e:
    logger.error("Failed to enable mass mode: " + str(e))
    forms.alert(
        "Mass creation failed. Ensure Massing Mode is enabled in Revit.",
        exitscript=True,
    )

# Start Revit Transaction
with revit.Transaction("Create Mass from AI Clusters"):
    try:
        mass_category = DB.BuiltInCategory.OST_Masses
        mass_family = DB.Family.Create(doc, mass_category)

        if not mass_family:
            raise Exception("Failed to create mass family.")

        for cluster in clusters:
            bbox_min = DB.XYZ(*cluster["bounding_box"]["min"])
            bbox_max = DB.XYZ(*cluster["bounding_box"]["max"])

            # Define Mass Volume
            solid_options = DB.SolidOptions(None, None)
            solid = DB.GeometryCreationUtilities.CreateExtrusionGeometry(
                [bbox_min, bbox_max], DB.XYZ.BasisZ, 10.0
            )

            # Create Mass Instance
            new_mass = DB.DirectShape.CreateElement(doc, DB.ElementId(mass_family.Id))
            new_mass.SetShape([solid])

            logger.info("Created mass for Cluster ID: " + str(cluster["cluster_id"]))

        forms.alert("Mass creation completed successfully.")
    except Exception as e:
        logger.error("Error during mass creation: " + str(e))
        forms.alert("Mass creation failed. Check logs for details.", exitscript=True)
