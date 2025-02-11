import json
import open3d as o3d
import numpy as np
from sklearn.cluster import DBSCAN
import os

# Load point cloud metadata
metadata_file = "C:\\Zonneveld\\temp\\point_cloud_data_with_transform.json"
output_file = "C:\\Zonneveld\\temp\\detected_features.json"

if not os.path.exists(metadata_file):
    print("Metadata file not found. Exiting.")
    exit()

# Read metadata
with open(metadata_file, "r") as file:
    metadata = json.load(file)

detected_features = {"detected_features": []}

# Process each scan from the metadata
for entry in metadata:
    scans = entry.get("scans", [])
    if not scans:
        print("No scans found for entry. Skipping.")
        continue

    scan_file_name = scans[0] + ".pts"
    scan_file_path = os.path.join("C:\\Zonneveld\\Point_Clouds", scan_file_name)

    if not os.path.exists(scan_file_path):
        print("Scan file not found:", scan_file_path)
        continue

    # Read points from the .pts file
    points = []
    colors = []
    try:
        with open(scan_file_path, "r") as file:
            line_count = int(
                file.readline().strip()
            )  # First line is the number of points
            for line in file:
                data = line.split()
                if len(data) >= 6:
                    x, y, z = float(data[0]), float(data[1]), float(data[2])
                    r, g, b = int(data[3]), int(data[4]), int(data[5])
                    points.append([x, y, z])
                    colors.append([r / 255.0, g / 255.0, b / 255.0])

    except Exception as e:
        print("Error reading .pts file:", e)
        continue

    print("Read {} points from {}".format(len(points), scan_file_path))

    # Convert points to Open3D point cloud
    point_cloud = o3d.geometry.PointCloud()
    point_cloud.points = o3d.utility.Vector3dVector(points)
    point_cloud.colors = o3d.utility.Vector3dVector(colors)

    # **Downsample the point cloud**
    voxel_size = 0.1  # Adjust this value as needed
    point_cloud = point_cloud.voxel_down_sample(voxel_size)

    downsampled_points = np.asarray(point_cloud.points)
    print("Downsampled to {} points.".format(len(downsampled_points)))

    if len(downsampled_points) == 0:
        print("Downsampling resulted in an empty point cloud. Skipping.")
        continue

    # Run DBSCAN clustering on downsampled points
    dbscan_labels = np.array(
        DBSCAN(eps=0.5, min_samples=10).fit(downsampled_points).labels_
    )

    # Extract clusters and bounding boxes
    unique_labels = set(dbscan_labels)
    for label in unique_labels:
        if label == -1:  # Noise points
            continue

        cluster_points = downsampled_points[dbscan_labels == label]
        bbox_min = cluster_points.min(axis=0)
        bbox_max = cluster_points.max(axis=0)

        # Save detected feature
        detected_features["detected_features"].append(
            {
                "type": "Cluster",
                "cluster_id": int(label),
                "bounding_box": {"min": bbox_min.tolist(), "max": bbox_max.tolist()},
                "num_points": len(cluster_points),
            }
        )

# Save detected features to output JSON
with open(output_file, "w") as file:
    json.dump(detected_features, file, indent=4)

print("Feature detection completed and saved to", output_file)
