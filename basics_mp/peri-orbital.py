# import cv2
# import mediapipe as mp
# import numpy as np
# import matplotlib.pyplot as plt

# mp_face_mesh = mp.solutions.face_mesh
# face_mesh = mp_face_mesh.FaceMesh(refine_landmarks=True)

# LEFT_EYE = [
#     33, 7, 163, 144, 145, 153, 154, 155,
#     133, 173, 157, 158, 159, 160, 161, 246
# ]
# vid_path = r"D:\Lie Detection Data HTI\Lie_detection_ex2\Thermal_lie_detection_ex2\krishna_grey_manual1.wmv"
# cap = cv2.VideoCapture(vid_path)

# signal = []

# while True:
#     ret, frame = cap.read()
#     if not ret:
#         break

#     h, w, _ = frame.shape
#     rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
#     results = face_mesh.process(rgb)

#     if results.multi_face_landmarks:
#         for face_landmarks in results.multi_face_landmarks:

#             # -----------------------------
#             # Get eye points
#             # -----------------------------
#             eye_points = []
#             for idx in LEFT_EYE:
#                 x = int(face_landmarks.landmark[idx].x * w)
#                 y = int(face_landmarks.landmark[idx].y * h)
#                 eye_points.append((x, y))

#             eye_points = np.array(eye_points)

#             # -----------------------------
#             # RECTANGLE around eye (OUTER)
#             # -----------------------------
#             x_min = np.min(eye_points[:, 0]) - 10
#             x_max = np.max(eye_points[:, 0]) + 10
#             y_min = np.min(eye_points[:, 1]) - 10
#             y_max = np.max(eye_points[:, 1]) + 10

#             # Clamp values (avoid out of bounds)
#             x_min = max(0, x_min)
#             y_min = max(0, y_min)
#             x_max = min(w, x_max)
#             y_max = min(h, y_max)

#             # -----------------------------
#             # Create OUTER mask (rectangle)
#             # -----------------------------
#             mask_outer = np.zeros((h, w), dtype=np.uint8)
#             cv2.rectangle(mask_outer, (x_min, y_min), (x_max, y_max), 255, -1)

#             # -----------------------------
#             # Create INNER mask (eye shape)
#             # -----------------------------
#             mask_inner = np.zeros((h, w), dtype=np.uint8)
#             cv2.fillPoly(mask_inner, [eye_points], 255)

#             # -----------------------------
#             # Subtract → peri-orbital
#             # -----------------------------
#             peri_mask = cv2.subtract(mask_outer, mask_inner)

#             # -----------------------------
#             # Convert to grayscale
#             # -----------------------------
#             gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

#             # Extract pixels
#             roi_pixels = gray[peri_mask == 255]

#             if len(roi_pixels) > 0:
#                 mean_val = np.mean(roi_pixels)
#                 signal.append(mean_val)

#             # -----------------------------
#             # Visualization
#             # -----------------------------
#             frame[peri_mask == 255] = [0, 255, 255]  # highlight peri region
#             cv2.rectangle(frame, (x_min, y_min), (x_max, y_max), (255, 0, 0), 1)

#     cv2.imshow("Peri-Orbital (Rectangle - Eye)", frame)

#     if cv2.waitKey(1) & 0xFF == 27:
#         break

# cap.release()
# cv2.destroyAllWindows()

# # -----------------------------
# # Plot graph
# # -----------------------------
# plt.plot(signal)
# plt.title("Peri-Orbital Intensity (Rectangle - Eye)")
# plt.xlabel("Frame")
# plt.ylabel("Mean Intensity")
# plt.show()
#############################################################

import cv2
import mediapipe as mp
import numpy as np
import matplotlib.pyplot as plt

# -----------------------------
# Setup
# -----------------------------
mp_face_mesh = mp.solutions.face_mesh
face_mesh = mp_face_mesh.FaceMesh(refine_landmarks=True)

LEFT_EYE = [
    33, 7, 163, 144, 145, 153, 154, 155,
    133, 173, 157, 158, 159, 160, 161, 246
]
vid_path = r"D:\Lie Detection Data HTI\Lie_detection_ex2\Thermal_lie_detection_ex2\krishna_iron_exported.wmv"
# vid_path = r"d:\Lie Detection Data HTI\Lie_detection_ex2\Thermal_lie_detection_ex2\sneha_grey_manual.wmv"
# vid_path = r"D:\Lie Detection Data HTI\Lie_detection_ex2\Thermal_lie_detection_ex2\sneha_iron_exported.wmv"
cap = cv2.VideoCapture(vid_path)

signal = []

# -----------------------------
# Live Graph Setup
# -----------------------------
plt.ion()  # interactive mode ON
fig, ax = plt.subplots()
line, = ax.plot([], [], lw=2)

ax.set_title("Live Peri-Orbital Signal")
ax.set_xlabel("Frame")
ax.set_ylabel("Intensity")

# -----------------------------
# Main Loop
# -----------------------------
while True:
    ret, frame = cap.read()
    if not ret:
        break

    h, w, _ = frame.shape
    rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    results = face_mesh.process(rgb)

    if results.multi_face_landmarks:
        for face_landmarks in results.multi_face_landmarks:

            # Get eye points
            eye_points = []
            for idx in LEFT_EYE:
                x = int(face_landmarks.landmark[idx].x * w)
                y = int(face_landmarks.landmark[idx].y * h)
                eye_points.append((x, y))

            eye_points = np.array(eye_points)

            # Rectangle (outer)
            padding = 10
            x_min = max(0, np.min(eye_points[:, 0]) - padding)
            x_max = min(w, np.max(eye_points[:, 0]) + padding)
            y_min = max(0, np.min(eye_points[:, 1]) - padding)
            y_max = min(h, np.max(eye_points[:, 1]) + padding)

            # Masks
            mask_outer = np.zeros((h, w), dtype=np.uint8)
            cv2.rectangle(mask_outer, (x_min, y_min), (x_max, y_max), 255, -1)

            mask_inner = np.zeros((h, w), dtype=np.uint8)
            cv2.fillPoly(mask_inner, [eye_points], 255)

            peri_mask = cv2.subtract(mask_outer, mask_inner)

            # Grayscale
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            roi_pixels = gray[peri_mask == 255]

            if len(roi_pixels) > 0:
                mean_val = np.mean(roi_pixels)
                signal.append(mean_val)

                # -----------------------------
                # LIVE GRAPH UPDATE
                # -----------------------------
                line.set_xdata(range(len(signal)))
                line.set_ydata(signal)

                # Auto scale for peaks & lows
                ax.set_xlim(0, len(signal))
                ax.set_ylim(min(signal) - 5, max(signal) + 5)

                plt.draw()
                plt.pause(0.001)

            # Visualization
            frame[peri_mask == 255] = [0, 255, 255]
            cv2.rectangle(frame, (x_min, y_min), (x_max, y_max), (255, 0, 0), 1)

    cv2.imshow("Peri-Orbital Tracking", frame)

    if cv2.waitKey(1) & 0xFF == 27:
        break

cap.release()
cv2.destroyAllWindows()

# -----------------------------
# FINAL GRAPH
# -----------------------------
plt.ioff()
plt.figure()
plt.plot(signal, linewidth=2)
plt.title("Final Peri-Orbital Signal")
plt.xlabel("Frame")
plt.ylabel("Intensity")
plt.grid()
plt.show()