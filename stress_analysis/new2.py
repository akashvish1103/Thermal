# import cv2
# import numpy as np
# import matplotlib.pyplot as plt

# # -----------------------------
# # VIDEO PATH
# # -----------------------------
# vid_path = r"D:\Lie Detection Data HTI\Lie_detection_ex2\Thermal_lie_detection_ex2\aditi_grey_manual.wmv"

# cap = cv2.VideoCapture(vid_path)

# ret, frame = cap.read()
# if not ret:
#     print("Error reading video")
#     exit()

# # -----------------------------
# # SELECT MULTIPLE ROIs
# # -----------------------------
# bboxes = cv2.selectROIs("Select Objects", frame, False)
# cv2.destroyWindow("Select Objects")

# trackers = []
# signals = []

# for bbox in bboxes:
#     tracker = cv2.TrackerCSRT_create()
#     tracker.init(frame, bbox)
#     trackers.append(tracker)
#     signals.append([])

# # -----------------------------
# # REFERENCE + LATCH
# # -----------------------------
# reference = [None] * len(trackers)
# latched = [False] * len(trackers)

# threshold = 2   # 🔴 tune this (very important)

# # -----------------------------
# # LIVE PLOTTING
# # -----------------------------
# plt.ion()
# fig, ax = plt.subplots()

# lines = []
# for i in range(len(trackers)):
#     line, = ax.plot([], [], label=f'ROI {i}', color='blue')
#     lines.append(line)

# ax.set_title("Live Multi-ROI Signals with Threshold Detection")
# ax.set_xlabel("Frame")
# ax.set_ylabel("Mean Intensity")
# ax.legend()

# frame_count = 0

# # -----------------------------
# # LOOP
# # -----------------------------
# while True:
#     ret, frame = cap.read()
#     if not ret:
#         break

#     gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

#     for i, tracker in enumerate(trackers):
#         success, bbox = tracker.update(frame)

#         if success:
#             x, y, w, h = [int(v) for v in bbox]
#             roi = gray[y:y+h, x:x+w]

#             if roi.size != 0:
#                 mean_val = np.mean(roi)
#                 signals[i].append(mean_val)

#                 # -----------------------------
#                 # SET REFERENCE (FIRST FRAME)
#                 # -----------------------------
#                 if reference[i] is None:
#                     reference[i] = mean_val

#                 # -----------------------------
#                 # THRESHOLD CHECK (LATCH)
#                 # -----------------------------
#                 if abs(mean_val - reference[i]) > threshold:
#                     latched[i] = True

#                 # OPTIONAL RESET (for breathing cycles)
#                 if abs(mean_val - reference[i]) < threshold / 2:
#                     latched[i] = False

#                 # -----------------------------
#                 # CHANGE GRAPH COLOR
#                 # -----------------------------
#                 if latched[i]:
#                     lines[i].set_color('red')
#                 else:
#                     lines[i].set_color('blue')

#                 # Update graph
#                 lines[i].set_data(range(len(signals[i])), signals[i])

#             # Draw bounding box
#             cv2.rectangle(frame, (x, y), (x+w, y+h), (0, 255, 0), 2)

#     # -----------------------------
#     # AUTO SCALE GRAPH
#     # -----------------------------
#     ax.relim()
#     ax.autoscale_view()

#     plt.pause(0.001)

#     # Show video
#     cv2.imshow("Multi Tracking", frame)

#     if cv2.waitKey(1) & 0xFF == 27:
#         break

# # -----------------------------
# # CLEANUP
# # -----------------------------
# cap.release()
# cv2.destroyAllWindows()
# plt.ioff()
# plt.show()

########################################

import cv2
import numpy as np
import matplotlib.pyplot as plt

# -----------------------------
# VIDEO PATH
# -----------------------------
vid_path = r"D:\Lie Detection Data HTI\Lie_detection_ex2\Thermal_lie_detection_ex2\aditi_grey_manual.wmv"

cap = cv2.VideoCapture(vid_path)

ret, frame = cap.read()
if not ret:
    print("Error reading video")
    exit()

# -----------------------------
# SELECT ROIs
# -----------------------------
bboxes = cv2.selectROIs("Select Objects", frame, False)
cv2.destroyWindow("Select Objects")

trackers = []
signals = []

for bbox in bboxes:
    tracker = cv2.TrackerCSRT_create()
    tracker.init(frame, bbox)
    trackers.append(tracker)
    signals.append([])

# -----------------------------
# REFERENCE + THRESHOLD
# -----------------------------
reference = [None] * len(trackers)
threshold = 2   # tune this

# -----------------------------
# PLOTTING
# -----------------------------
plt.ion()
fig, ax = plt.subplots()

ax.set_title("Segment-wise Threshold Detection")
ax.set_xlabel("Frame")
ax.set_ylabel("Mean Intensity")

# -----------------------------
# LOOP
# -----------------------------
while True:
    ret, frame = cap.read()
    if not ret:
        break

    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

    for i, tracker in enumerate(trackers):
        success, bbox = tracker.update(frame)

        if success:
            x, y, w, h = [int(v) for v in bbox]
            roi = gray[y:y+h, x:x+w]

            if roi.size != 0:
                mean_val = np.mean(roi)
                signals[i].append(mean_val)

                # Set reference (first frame)
                if reference[i] is None:
                    reference[i] = mean_val

                # -----------------------------
                # DRAW SEGMENT (key logic)
                # -----------------------------
                if len(signals[i]) > 1:
                    x_vals = [len(signals[i])-2, len(signals[i])-1]
                    y_vals = [signals[i][-2], signals[i][-1]]

                    # Condition
                    if abs(mean_val - reference[i]) > threshold:
                        color = 'red'
                    else:
                        color = 'blue'

                    ax.plot(x_vals, y_vals, color=color)

            # Draw bounding box
            cv2.rectangle(frame, (x, y), (x+w, y+h), (0, 255, 0), 2)

    # Auto scale
    ax.relim()
    ax.autoscale_view()

    plt.pause(0.001)

    cv2.imshow("Tracking", frame)

    if cv2.waitKey(1) & 0xFF == 27:
        break

# -----------------------------
# CLEANUP
# -----------------------------
cap.release()
cv2.destroyAllWindows()
plt.ioff()
plt.show()