import sys
import json
import numpy as np
import open3d as o3d
import os
from sklearn.linear_model import RANSACRegressor

# from sklearn.cluster import DBSCAN, KMeans
# from scipy.spatial import ConvexHull

# Define file paths
temp_dir = "C:\\Zonneveld\\temp"
point_cloud_path = "C:\\Zonneveld\\Point_Clouds\\Aerial scan farmhouse.pts"
detected_surfaces_path = os.path.join(temp_dir, "detected_surfaces.json")
log_file_path = os.path.join(temp_dir, "ai_debug_log.txt")


# Logging function
def write_log(message):
    with open(log_file_path, "a") as log_file:
        log_file.write(message + "\n")
    print(message)


# Load Point Cloud Data
write_log("Processing Point Cloud: " + point_cloud_path)

if not os.path.exists(point_cloud_path):
    write_log("Error: PTS file not found.")
    exit()

# Read PTS file
with open(point_cloud_path, "r") as file:
    lines = file.readlines()

num_points = int(lines[0].strip())  # First line contains number of points
write_log("Found " + str(num_points) + " lines in the PTS file.")

# Parse points
points = []
colors = []
for line in lines[1:]:  # Skip first line
    values = line.split()
    if len(values) < 6:
        continue
    x, y, z, r, g, b = map(float, values[:6])
    points.append([x, y, z])
    colors.append([r / 255, g / 255, b / 255])

points = np.array(points)
write_log("Loaded " + str(len(points)) + " points.")

# Downsample for performance
if len(points) > 5_000_000:
    sample_indices = np.random.choice(len(points), 5_000_000, replace=False)
    points = points[sample_indices]
    write_log("Downsampled to 5 million points.")

# Convert to Open3D Point Cloud
pcd = o3d.geometry.PointCloud()
pcd.points = o3d.utility.Vector3dVector(points)

# Estimate Normals
pcd.estimate_normals(
    search_param=o3d.geometry.KDTreeSearchParamHybrid(radius=0.5, max_nn=30)
)

# Convert Open3D points to numpy
normals = np.asarray(pcd.normals)

# RANSAC Plane Detection
detected_surfaces = []
plane_count = 0
write_log("Running RANSAC plane detection...")

while len(points) > 1000:  # Stop if too few points remain
    plane_model, inliers = pcd.segment_plane(
        distance_threshold=0.05, ransac_n=3, num_iterations=1000
    )

    if len(inliers) < 5000:  # Ignore small planes
        write_log("Skipped small plane with " + str(len(inliers)) + " points.")
        break

    # Extract the plane points
    plane_points = points[inliers]
    plane_normals = normals[inliers]

    # Determine plane type (Wall, Roof, Ground)
    normal = np.mean(plane_normals, axis=0)
    plane_type = "Unknown"

    if abs(normal[2]) > 0.9:  # Z-axis normal → Ground
        plane_type = "Ground"
    elif abs(normal[2]) < 0.2:  # Mostly vertical → Wall
        plane_type = "Wall"
    else:  # Slanted surface → Roof
        plane_type = "Roof"

    # Compute bounding box
    min_corner = plane_points.min(axis=0).tolist()
    max_corner = plane_points.max(axis=0).tolist()

    detected_surfaces.append(
        {
            "type": plane_type,
            "plane_id": plane_count,
            "bounding_box": {"min": min_corner, "max": max_corner},
            "num_points": len(plane_points),
        }
    )

    write_log(
        "Detected "
        + plane_type
        + " plane with ID "
        + str(plane_count)
        + " | Points: "
        + str(len(plane_points))
    )

    plane_count += 1

    # Remove inliers and continue
    pcd = pcd.select_by_index(inliers, invert=True)
    points = np.asarray(pcd.points)
    normals = np.asarray(pcd.normals)

# Save detected surfaces
with open(detected_surfaces_path, "w") as file:
    json.dump({"detected_surfaces": detected_surfaces}, file, indent=4)

write_log("Feature detection completed. Output saved to " + detected_surfaces_path)
print("AI Analysis Completed.")
