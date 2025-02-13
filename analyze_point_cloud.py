import sys
import json
import numpy as np
import open3d as o3d
import os
from sklearn.cluster import DBSCAN, KMeans

# Define file paths
metadata_file = "C:\\Zonneveld\\temp\\point_cloud_data_with_transform.json"
output_file = "C:\\Zonneveld\\temp\\detected_features.json"
log_file_path = "C:\\Zonneveld\\temp\\ai_debug_log.txt"  # ✅ Fix: Declare the log file path at the start

# Initialize log file
try:
    with open(log_file_path, "w") as log_file:
        log_file.write("AI Analysis Debug Log\n")
        log_file.write("-----------------\n")
except Exception as e:
    print("Failed to create log file: " + str(e))
    exit()

# Ensure metadata file exists
if not os.path.exists(metadata_file):
    with open(log_file_path, "a") as log_file:
        log_file.write("Metadata file not found. Exiting.\n")
    print("Metadata file not found. Exiting.")
    exit()

# Load metadata
try:
    with open(metadata_file, "r") as file:
        metadata = json.load(file)
except Exception as e:
    with open(log_file_path, "a") as log_file:
        log_file.write("Failed to load metadata file: " + str(e) + "\n")
    exit()

# Initialize detected features list
detected_features = {"detected_features": []}

# Process each scan from the metadata
for point_cloud_entry in metadata:
    scans = point_cloud_entry.get("scans", [])
    if not scans:
        with open(log_file_path, "a") as log_file:
            log_file.write("No scans found for entry. Skipping.\n")
        continue

    scan_file_name = scans[0]
    scan_file_path = os.path.join(
        "C:\\Zonneveld\\Point_Clouds", scan_file_name + ".pts"
    )

    if not os.path.exists(scan_file_path):
        with open(log_file_path, "a") as log_file:
            log_file.write("Scan file not found: " + scan_file_path + "\n")
        continue

    with open(log_file_path, "a") as log_file:
        log_file.write("Processing Point Cloud: " + scan_file_path + "\n")

    # Read the PTS file
    try:
        with open(scan_file_path, "r") as file:
            lines = file.readlines()

        with open(log_file_path, "a") as log_file:
            log_file.write("Found " + str(len(lines)) + " lines in the PTS file.\n")

        # Convert point cloud data to numpy array
        points = []
        for line in lines[1:]:  # Skip first line (header)
            parts = line.strip().split()
            if len(parts) >= 3:  # x, y, z
                x, y, z = float(parts[0]), float(parts[1]), float(parts[2])
                points.append([x, y, z])

        points = np.array(points)

        # **Debugging: Print First Few Points**
        with open(log_file_path, "a") as log_file:
            log_file.write("First 10 points: " + str(points[:10]) + "\n")

        # **Downsample large point clouds**
        if len(points) > 10000000:
            with open(log_file_path, "a") as log_file:
                log_file.write("Downsampling large point cloud for clustering...\n")

            points = points[::10]  # Keep every 10th point

            with open(log_file_path, "a") as log_file:
                log_file.write("Downsampled to " + str(len(points)) + " points.\n")

        # **Try DBSCAN Clustering**
        try:
            with open(log_file_path, "a") as log_file:
                log_file.write("Running DBSCAN with eps=0.022 and min_samples=13...\n")

            dbscan_labels = np.array(
                DBSCAN(eps=0.022, min_samples=13).fit(points).labels_
            )
            unique_labels = set(dbscan_labels)
            num_clusters = len(unique_labels) - (1 if -1 in unique_labels else 0)

            with open(log_file_path, "a") as log_file:
                log_file.write("DBSCAN found " + str(num_clusters) + " clusters.\n")

            if num_clusters > 0:
                for cluster_id in range(num_clusters):
                    cluster_points = points[dbscan_labels == cluster_id]
                    if len(cluster_points) == 0:
                        continue

                    min_bound = cluster_points.min(axis=0).tolist()
                    max_bound = cluster_points.max(axis=0).tolist()

                    detected_features["detected_features"].append(
                        {
                            "type": "Cluster",
                            "cluster_id": cluster_id,
                            "bounding_box": {"min": min_bound, "max": max_bound},
                            "num_points": len(cluster_points),
                        }
                    )
            else:
                with open(log_file_path, "a") as log_file:
                    log_file.write("DBSCAN found no clusters. Trying KMeans...\n")

                # **If DBSCAN Fails, Try KMeans**
                kmeans = KMeans(n_clusters=5, random_state=42).fit(points)
                kmeans_labels = kmeans.labels_

                for cluster_id in range(5):  # Since we set n_clusters=5
                    cluster_points = points[kmeans_labels == cluster_id]
                    if len(cluster_points) == 0:
                        continue

                    min_bound = cluster_points.min(axis=0).tolist()
                    max_bound = cluster_points.max(axis=0).tolist()

                    detected_features["detected_features"].append(
                        {
                            "type": "Cluster",
                            "cluster_id": cluster_id,
                            "bounding_box": {"min": min_bound, "max": max_bound},
                            "num_points": len(cluster_points),
                        }
                    )

        except Exception as e:
            with open(log_file_path, "a") as log_file:
                log_file.write("DBSCAN clustering failed: " + str(e) + "\n")

    except Exception as e:
        with open(log_file_path, "a") as log_file:
            log_file.write("Error processing point cloud: " + str(e) + "\n")

# **Save Detected Features**
try:
    with open(output_file, "w") as file:
        json.dump(detected_features, file, indent=4)

    with open(log_file_path, "a") as log_file:
        log_file.write(
            "Feature detection completed. Output saved to " + output_file + "\n"
        )

except Exception as e:
    with open(log_file_path, "a") as log_file:
        log_file.write("Failed to save detected features: " + str(e) + "\n")

print("AI Analysis Completed.")
if "dbscan_labels" in locals():
    print("DBSCAN unique clusters:", np.unique(dbscan_labels))
else:
    print("❌ DBSCAN failed: No clusters detected.")

print("DBSCAN unique clusters:", np.unique(dbscan_labels))
