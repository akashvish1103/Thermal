# To check whether the video is truly grayscale (R=G=B) or not, we can read each frame and verify that all three
#  channels are identical.
# Results: All the grey scaled videos exported from IrSoft are NOT TRUE GRAYSCALE (R != G != B). This is important
# to know for our processing pipeline, as we may need to convert to grayscale first.

import cv2
import numpy as np

# -----------------------------
# VIDEO PATH
# -----------------------------
vid_path = r"D:\Lie Detection Data HTI\Lie_detection_ex2\Thermal_lie_detection_ex2\grey_manual\krishna_grey_manual1.wmv"

cap = cv2.VideoCapture(vid_path)

frame_count = 0
is_grayscale = True

while True:
    ret, frame = cap.read()
    if not ret:
        break

    frame_count += 1

    # Check if all channels are equal
    if not (np.array_equal(frame[:, :, 0], frame[:, :, 1]) and
            np.array_equal(frame[:, :, 1], frame[:, :, 2])):

        print(f"❌ NOT grayscale at frame {frame_count}")
        is_grayscale = False
        break

cap.release()

# -----------------------------
# FINAL RESULT
# -----------------------------
if is_grayscale:
    print("✅ VIDEO is TRUE GRAYSCALE (R = G = B)")
else:
    print("❌ VIDEO is NOT TRUE GRAYSCALE")