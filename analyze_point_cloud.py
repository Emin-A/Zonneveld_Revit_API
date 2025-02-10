import sys
import json
import open3d as o3d
import os

# Load point cloud metadata
metadata_file = "C:\\Zonneveld\\temp\\point_cloud_data_with_transform.json"
output_file = "C:\\Zonneveld\\temp\\detected_features.json"
point_cloud_dir = "C:\\Zonneveld\\Point_Clouds"

# Check if metadata file exists
if not os.path.exists(metadata_file):
    print("Metadata file not found. Exiting.")
    sys.exit()

# Read point cloud metadata
with open(metadata_file, "r") as file:
    metadata = json.load(file)

# Initialize detected features list
detected_features = {"detected_features": []}

# Process each scan from the metadata
for point_cloud_entry in metadata:
    scans = point_cloud_entry.get("scans", [])
    transform_data = point_cloud_entry.get("transform", {})
    if not scans:
        print("No scans found for entry. Skipping.")
        continue

    scan_file_name = scans[0] + ".pts"
    scan_file_path = os.path.join(point_cloud_dir, scan_file_name)

    if not os.path.exists(scan_file_path):
        print("Scan file not found: " + scan_file_path)
        continue

    # Load point cloud from .pts
    point_cloud = o3d.io.read_point_cloud(scan_file_path, format="pts")

    if point_cloud.is_empty():
        print("Empty point cloud loaded. Skipping.")
        continue

    # Apply transformation if present
    if transform_data:
        origin = transform_data.get("origin", [0.0, 0.0, 0.0])
        basis_x = transform_data.get("basis_x", [1.0, 0.0, 0.0])
        basis_y = transform_data.get("basis_y", [0.0, 1.0, 0.0])
        basis_z = transform_data.get("basis_z", [0.0, 0.0, 1.0])

        transform_matrix = [
            [basis_x[0], basis_y[0], basis_z[0], origin[0]],
            [basis_x[1], basis_y[1], basis_z[1], origin[1]],
            [basis_x[2], basis_y[2], basis_z[2], origin[2]],
            [0, 0, 0, 1],
        ]

        point_cloud.transform(transform_matrix)

    # Detect planes using RANSAC
    plane_model, inliers = point_cloud.segment_plane(
        distance_threshold=0.01, ransac_n=3, num_iterations=1000
    )

    if plane_model:
        plane_equation = {
            "type": "Plane",
            "equation": [
                plane_model[0],
                plane_model[1],
                plane_model[2],
                plane_model[3],
            ],
            "num_points": len(inliers),
        }
        detected_features["detected_features"].append(plane_equation)
        print(
            "Detected plane with equation: {}x + {}y + {}z + {} = 0".format(
                *plane_model
            )
        )

# Save detected features to output JSON
with open(output_file, "w") as file:
    json.dump(detected_features, file, indent=4)

print("Feature detection completed and saved to " + output_file)
print("Python executable:", sys.executable)
print("Python sys.path:", sys.path)
print("Open3D version:", o3d.__version__)
