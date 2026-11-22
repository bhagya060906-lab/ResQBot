
import cv2
import numpy as np


def detect_objects(frame_rgb):
    """
    Detects the robot, obstacles and rescue target
    from an RGB simulation image using OpenCV.
    """

    # Convert RGB image into HSV
    hsv = cv2.cvtColor(frame_rgb, cv2.COLOR_RGB2HSV)

    # Define colour ranges
    colour_ranges = {
        "obstacle": [
            (np.array([0, 100, 80]), np.array([10, 255, 255])),
            (np.array([170, 100, 80]), np.array([180, 255, 255]))
        ],
        "target": [
            (np.array([35, 80, 70]), np.array([85, 255, 255]))
        ],
        "robot": [
            (np.array([90, 80, 70]), np.array([130, 255, 255]))
        ]
    }

    detections = {
        "obstacle": [],
        "target": [],
        "robot": []
    }

    # Process each object category
    for label, ranges in colour_ranges.items():

        # Create a binary mask
        mask = np.zeros(hsv.shape[:2], dtype=np.uint8)

        for lower, upper in ranges:
            colour_mask = cv2.inRange(hsv, lower, upper)
            mask = cv2.bitwise_or(mask, colour_mask)

        # Remove small noise
        kernel = np.ones((3, 3), np.uint8)
        mask = cv2.morphologyEx(
            mask,
            cv2.MORPH_OPEN,
            kernel
        )

        # Find connected object regions
        count, labels, stats, centroids = (
            cv2.connectedComponentsWithStats(mask, 8)
        )

        for i in range(1, count):

            x, y, width, height, area = stats[i]

            if area > 100:
                detections[label].append({
                    "bbox": (
                        int(x),
                        int(y),
                        int(width),
                        int(height)
                    ),
                    "center": (
                        int(centroids[i][0]),
                        int(centroids[i][1])
                    ),
                    "area": int(area)
                })

    return detections
