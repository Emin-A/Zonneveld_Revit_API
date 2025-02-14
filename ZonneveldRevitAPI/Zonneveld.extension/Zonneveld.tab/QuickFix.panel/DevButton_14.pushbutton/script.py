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
mass_family_name = os.path.join(temp_dir, "AI_Generated_Mass.rfa")

# Detect Revit version and set correct Mass Template Path
revit_version = revit.doc.Application.VersionNumber
template_base_path = "C:\\ProgramData\\Autodesk\\RVT {}\\Family Templates\\English\\Conceptual Mass\\Metric Mass.rft"
mass_template_path = template_base_path.format(revit_version)

if not os.path.exists(mass_template_path):
    forms.alert(
        "Mass template file not found for Revit " + revit_version, exitscript=True
    )

# Check if detected clusters file exists
if not os.path.exists(detected_features_path):
    forms.alert(
        "No detected features found. Ensure the AI analysis ran successfully.",
        exitscript=True,
    )

# Read detected features
with open(detected_features_path, "r") as file:
    detected_data = json.load(file)

# Extract clusters
clusters = detected_data.get("detected_features", [])

if not clusters:
    forms.alert("No valid clusters found in the detected features.", exitscript=True)

# Minimum allowable curve length in Revit
min_curve_length = revit.doc.Application.ShortCurveTolerance

# Start a SINGLE Transaction for mass creation
try:
    doc = revit.doc

    # Ensure Mass Category is available
    mass_category = DB.Category.GetCategory(doc, DB.BuiltInCategory.OST_Mass)
    if not mass_category:
        raise Exception("Mass category is missing in the project.")

    # Begin transaction for creating and loading the mass family
    with DB.Transaction(doc, "Create AI-Generated In-Place Mass") as transaction:
        transaction.Start()

        # Check if the mass family file exists, delete if necessary
        if os.path.exists(mass_family_name):
            try:
                os.remove(mass_family_name)
                logger.info("Existing mass file deleted: " + mass_family_name)
            except Exception as delete_error:
                raise Exception(
                    "Failed to delete existing mass file: " + str(delete_error)
                )

        # Create a new Mass Family Document
        mass_family_doc = doc.Application.NewFamilyDocument(mass_template_path)
        if not mass_family_doc:
            raise Exception("Failed to create mass family document.")

        # Start transaction in the mass family document
        family_transaction = DB.Transaction(mass_family_doc, "Create Mass Geometry")
        family_transaction.Start()

        # Iterate through detected clusters and create mass forms
        for cluster in clusters:
            if cluster["type"] == "Cluster":
                min_x, min_y, min_z = cluster["bounding_box"]["min"]
                max_x, max_y, max_z = cluster["bounding_box"]["max"]

                # Calculate dimensions
                width = abs(max_x - min_x)
                depth = abs(max_y - min_y)
                height = abs(max_z - min_z)

                # Skip clusters that are too small for Revit's tolerance
                if (
                    width < min_curve_length
                    or depth < min_curve_length
                    or height < min_curve_length
                ):
                    logger.warning(
                        "Skipped small cluster ID "
                        + str(cluster["cluster_id"])
                        + " due to size below Revit's tolerance."
                    )
                    continue

                # Define base points for extrusion
                base_points = [
                    DB.XYZ(min_x, min_y, min_z),
                    DB.XYZ(max_x, min_y, min_z),
                    DB.XYZ(max_x, max_y, min_z),
                    DB.XYZ(min_x, max_y, min_z),
                ]

                # Create profile curves
                try:
                    profile = DB.CurveLoop.Create(
                        [
                            DB.Line.CreateBound(
                                base_points[i], base_points[(i + 1) % 4]
                            )
                            for i in range(4)
                        ]
                    )
                except Exception as curve_error:
                    logger.warning(
                        "Skipping cluster ID "
                        + str(cluster["cluster_id"])
                        + " due to curve creation error: "
                        + str(curve_error)
                    )
                    continue

                # Extrude the profile upwards to create a solid
                try:
                    solid = DB.GeometryCreationUtilities.CreateExtrusionGeometry(
                        [profile], DB.XYZ(0, 0, 1), height
                    )
                    mass_form = DB.FreeFormElement.Create(mass_family_doc, solid)
                    if not mass_form:
                        raise Exception("Failed to create mass form.")
                except Exception as extrude_error:
                    logger.warning(
                        "Skipping cluster ID "
                        + str(cluster["cluster_id"])
                        + " due to extrusion error: "
                        + str(extrude_error)
                    )
                    continue

        family_transaction.Commit()

        # Save and close mass family
        mass_family_doc.SaveAs(mass_family_name)
        mass_family_doc.Close(False)

        # Load the mass family into the project
        load_success = doc.LoadFamily(mass_family_name)
        if not load_success:
            raise Exception("Failed to load Mass Family into project.")

        # Retrieve the Family and FamilySymbol
        family = next(
            (
                f
                for f in DB.FilteredElementCollector(doc).OfClass(DB.Family)
                if f.Name == "AI_Generated_Mass"
            ),
            None,
        )

        if not family:
            raise Exception("Loaded mass family not found in project.")

        # Retrieve FamilySymbol
        family_symbol = next((s for s in family.GetFamilySymbolIds()), None)

        if not family_symbol:
            raise Exception("No FamilySymbol found in the loaded family.")

        family_symbol = doc.GetElement(family_symbol)

        # Activate FamilySymbol if needed
        if not family_symbol.IsActive:
            family_symbol.Activate()
            doc.Regenerate()

        # Loop through detected clusters and create mass instances
        for cluster in clusters:
            if cluster["type"] == "Cluster":
                min_x, min_y, min_z = cluster["bounding_box"]["min"]
                max_x, max_y, max_z = cluster["bounding_box"]["max"]

                min_corner = DB.XYZ(min_x, min_y, min_z)

                # Create in-place mass instance
                mass_instance = doc.Create.NewFamilyInstance(
                    min_corner, family_symbol, DB.Structure.StructuralType.NonStructural
                )
                if not mass_instance:
                    raise Exception("Failed to create Mass Instance.")

                logger.info("Created mass for cluster ID " + str(cluster["cluster_id"]))

        transaction.Commit()
        forms.alert("Mass creation completed successfully!")

except Exception as e:
    logger.error("Error during mass creation: " + str(e))
    forms.alert("Mass creation failed. Check logs for details.", exitscript=True)
