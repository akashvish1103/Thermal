# import cv2
# import mediapipe as mp
# import numpy as np
# import matplotlib.pyplot as plt

# # -----------------------------
# # SETTINGS
# # -----------------------------
# video_path = r"D:\Lie Detection Data HTI\Lie_detection_ex2\Thermal_lie_detection_ex2\grey_manual\krishna_grey_manual1.wmv"   # 0 for webcam OR give video path
# BOX_SIZE = 40    # size of nose box (adjust if needed)

# # -----------------------------
# # INIT
# # -----------------------------
# cap = cv2.VideoCapture(video_path)

# mp_face = mp.solutions.face_mesh
# face_mesh = mp_face.FaceMesh(static_image_mode=False, max_num_faces=1)

# # Safe tracker creation (works for all versions)
# try:
#     tracker = cv2.TrackerCSRT_create()
# except AttributeError:
#     tracker = cv2.legacy.TrackerCSRT_create()
# tracker_initialized = False

# intensity_values = []

# # Nose landmark index (MediaPipe)
# NOSE_TIP = 1

# # -----------------------------
# # LOOP
# # -----------------------------
# while True:
#     ret, frame = cap.read()
#     if not ret:
#         break

#     h, w, _ = frame.shape
#     rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

#     # -----------------------------
#     # STEP 1: Detect nose (only if tracker not initialized)
#     # -----------------------------
#     if not tracker_initialized:
#         results = face_mesh.process(rgb)

#         if results.multi_face_landmarks:
#             landmarks = results.multi_face_landmarks[0]

#             nose = landmarks.landmark[NOSE_TIP]
#             x = int(nose.x * w)
#             y = int(nose.y * h)

#             # Create bounding box
#             x1 = x - BOX_SIZE // 2
#             y1 = y - BOX_SIZE // 2
#             bbox = (x1, y1, BOX_SIZE, BOX_SIZE)

#             tracker.init(frame, bbox)
#             tracker_initialized = True

#     # -----------------------------
#     # STEP 2: Track nose
#     # -----------------------------
#     if tracker_initialized:
#         success, bbox = tracker.update(frame)

#         if success:
#             x, y, bw, bh = map(int, bbox)

#             # Draw rectangle
#             cv2.rectangle(frame, (x, y), (x+bw, y+bh), (0,255,0), 2)

#             # -----------------------------
#             # STEP 3: Extract intensity
#             # -----------------------------
#             roi = frame[y:y+bh, x:x+bw]

#             if roi.size != 0:
#                 gray = cv2.cvtColor(roi, cv2.COLOR_BGR2GRAY)
#                 mean_intensity = np.mean(gray)

#                 intensity_values.append(mean_intensity)

#                 # Display value
#                 cv2.putText(frame, f"Intensity: {mean_intensity:.2f}",
#                             (x, y-10), cv2.FONT_HERSHEY_SIMPLEX,
#                             0.6, (0,255,0), 2)
#         else:
#             cv2.putText(frame, "Tracking Lost", (50,50),
#                         cv2.FONT_HERSHEY_SIMPLEX, 1, (0,0,255), 2)

#     cv2.imshow("Nose Tracking", frame)

#     if cv2.waitKey(100) & 0xFF == 27:
#         break

# # -----------------------------
# # CLEANUP
# # -----------------------------
# cap.release()
# cv2.destroyAllWindows()

# # -----------------------------
# # STEP 4: Plot breathing signal
# # -----------------------------
# plt.plot(intensity_values)
# plt.title("Breathing Signal (Thermal Intensity)")
# plt.xlabel("Frame")
# plt.ylabel("Mean Intensity")
# plt.show()

#####################

import cv2
import numpy as np
import matplotlib.pyplot as plt

# -----------------------------
# SETTINGS
# -----------------------------
# video_path = r"D:\Lie Detection Data HTI\Lie_detection_ex2\Thermal_lie_detection_ex2\grey_manual\krishna_grey_manual1.wmv"
# video_path = r"d:\Lie Detection Data HTI\Lie_detection_ex2\Thermal_lie_detection_ex2\sneha_grey_manual.wmv"
video_path = "D:\Lie Detection Data HTI\Lie_detection_ex2\Thermal_lie_detection_ex2\grey_manual\sneha_grey_manual.wmv"

# -----------------------------
# INIT
# -----------------------------
cap = cv2.VideoCapture(video_path)

# Safe tracker creation
try:
    tracker = cv2.TrackerCSRT_create()
except AttributeError:
    tracker = cv2.legacy.TrackerCSRT_create()

intensity_values = []

# -----------------------------
# STEP 1: First frame + ROI
# -----------------------------
ret, frame = cap.read()
if not ret:
    print("Error reading video")
    exit()

bbox = cv2.selectROI("Select ROI", frame, False)
cv2.destroyWindow("Select ROI")

tracker.init(frame, bbox)

# -----------------------------
# LIVE GRAPH SETUP
# -----------------------------
plt.ion()   # interactive mode ON
fig, ax = plt.subplots()
line, = ax.plot([], [])

ax.set_title("Live Breathing Signal")
ax.set_xlabel("Frame")
ax.set_ylabel("Intensity")

# -----------------------------
# LOOP
# -----------------------------
frame_count = 0

while True:
    ret, frame = cap.read()
    if not ret:
        break

    success, bbox = tracker.update(frame)

    if success:
        x, y, w, h = map(int, bbox)

        # Safety boundaries
        x = max(0, x)
        y = max(0, y)

        # Draw box
        cv2.rectangle(frame, (x, y), (x+w, y+h), (0,255,0), 2)

        # ROI
        roi = frame[y:y+h, x:x+w]

        if roi.size != 0:
            gray = cv2.cvtColor(roi, cv2.COLOR_BGR2GRAY)
            mean_intensity = np.mean(gray)

            intensity_values.append(mean_intensity)

            # Display value
            cv2.putText(frame, f"{mean_intensity:.2f}",
                        (x, y-10), cv2.FONT_HERSHEY_SIMPLEX,
                        0.6, (0,255,0), 2)

    else:
        cv2.putText(frame, "Tracking Lost", (50,50),
                    cv2.FONT_HERSHEY_SIMPLEX, 1, (0,0,255), 2)

    cv2.imshow("Tracking ROI", frame)

    # -----------------------------
    # UPDATE LIVE GRAPH
    # -----------------------------
    # -----------------------------
# LIVE GRAPH (SCROLLING WINDOW)
# -----------------------------
    window_size = 200   # number of frames visible

    if len(intensity_values) > 5:
        data = intensity_values[-window_size:]   # last N values only

        line.set_xdata(np.arange(len(data)))
        line.set_ydata(data)

        # FIXED AXIS (no shrinking)
        ax.set_xlim(0, window_size)
        # ax.set_ylim(0, 255)   # for grayscale thermal
        y_min = np.min(data)
        y_max = np.max(data)

        margin = 2  # small padding

        ax.set_ylim(y_min - margin, y_max + margin)

        plt.draw()
        plt.pause(0.01)

    # -----------------------------
    # EXIT
    # -----------------------------
    if cv2.waitKey(30) & 0xFF == 27:
        break

    frame_count += 1

# -----------------------------
# CLEANUP
# -----------------------------
cap.release()
cv2.destroyAllWindows()
plt.ioff()
plt.show()