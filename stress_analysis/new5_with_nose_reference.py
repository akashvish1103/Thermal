import cv2
import numpy as np
import matplotlib.pyplot as plt
import mediapipe as mp

# -----------------------------
# VIDEO PATH
# -----------------------------
vid_path = r"D:\Lie Detection Data HTI\Lie_detection_ex2\Thermal_lie_detection_ex2\grey_manual\rahul_grey_manual.wmv"


cap = cv2.VideoCapture(vid_path)

ret, frame = cap.read()
if not ret:
    print("Error reading video")
    exit()

# -----------------------------
# MEDIAPIPE SETUP (Face Mesh)
# -----------------------------
mp_face_mesh = mp.solutions.face_mesh
face_mesh = mp_face_mesh.FaceMesh(refine_landmarks=True)

# Nose tip landmark index (MediaPipe)
NOSE_TIP = 1

# -----------------------------
# SELECT ROI
# -----------------------------
bbox = cv2.selectROI("Select ROI", frame, False)
cv2.destroyWindow("Select ROI")

x, y, w, h = [int(v) for v in bbox]

# -----------------------------
# DETECT NOSE IN FIRST FRAME
# -----------------------------
rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
results = face_mesh.process(rgb)

if not results.multi_face_landmarks:
    print("Face not detected")
    exit()

landmarks = results.multi_face_landmarks[0]

h_frame, w_frame, _ = frame.shape

nose_x = int(landmarks.landmark[NOSE_TIP].x * w_frame)
nose_y = int(landmarks.landmark[NOSE_TIP].y * h_frame)

# -----------------------------
# STORE RELATION (VERY IMPORTANT)
# distance from nose → bottom of box
# -----------------------------
distance_nose_to_bottom = (y + h) - nose_y

# also store width and height
box_w, box_h = w, h

# -----------------------------
# TRACKER INIT
# -----------------------------
tracker = cv2.TrackerCSRT_create()
tracker.init(frame, bbox)

# -----------------------------
# SIGNAL STORAGE
# -----------------------------
signals = []
reference = None
threshold = 2

# -----------------------------
# PLOTTING
# -----------------------------
plt.ion()
fig, ax = plt.subplots()

ax.set_title("Signal with Nose-based Recovery")
ax.set_xlabel("Frame")
ax.set_ylabel("Mean Intensity")

frame_count = 0

# -----------------------------
# LOOP
# -----------------------------
while True:
    ret, frame = cap.read()
    if not ret:
        break

    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

    # -----------------------------
    # DETECT NOSE EVERY FRAME
    # -----------------------------
    rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    results = face_mesh.process(rgb)

    nose_detected = False

    if results.multi_face_landmarks:
        landmarks = results.multi_face_landmarks[0]

        nose_x = int(landmarks.landmark[NOSE_TIP].x * w_frame)
        nose_y = int(landmarks.landmark[NOSE_TIP].y * h_frame)

        nose_detected = True

        # draw nose point
        cv2.circle(frame, (nose_x, nose_y), 3, (0, 0, 255), -1)

    # -----------------------------
    # TRACKER UPDATE
    # -----------------------------
    success, bbox = tracker.update(frame)

    # -----------------------------
    # IF TRACKING FAILS → RECONSTRUCT BOX
    # -----------------------------
    if not success and nose_detected:

        # reconstruct bottom of box
        bottom_y = nose_y + distance_nose_to_bottom

        # compute top-left y
        new_y = int(bottom_y - box_h)

        # keep x centered around nose
        new_x = int(nose_x - box_w // 2)

        bbox = (new_x, new_y, box_w, box_h)

        # reinitialize tracker
        tracker = cv2.TrackerCSRT_create()
        tracker.init(frame, bbox)

        print("Tracker recovered using nose")

    x, y, w, h = [int(v) for v in bbox]

    # -----------------------------
    # BOUNDARY CHECK
    # -----------------------------
    x = max(0, min(x, w_frame-1))
    y = max(0, min(y, h_frame-1))
    w = max(1, min(w, w_frame-x))
    h = max(1, min(h, h_frame-y))

    roi = gray[y:y+h, x:x+w]

    if roi.size != 0:
        mean_val = np.mean(roi)
        signals.append(mean_val)

        if reference is None:
            reference = mean_val

        if len(signals) > 1:
            x_vals = [len(signals)-2, len(signals)-1]
            y_vals = [signals[-2], signals[-1]]

            if (mean_val - reference) > threshold:
                color = 'red'
            else:
                color = 'blue'

            ax.plot(x_vals, y_vals, color=color)

    # draw bounding box
    cv2.rectangle(frame, (x, y), (x+w, y+h), (0,255,0), 2)

    # -----------------------------
    # GRAPH UPDATE
    # -----------------------------
    ax.relim()
    ax.autoscale_view()

    plt.pause(0.001)

    cv2.imshow("Tracking with Nose Recovery", frame)

    frame_count += 1

    if cv2.waitKey(1) & 0xFF == 27:
        break

# -----------------------------
# CLEANUP
# -----------------------------
cap.release()
cv2.destroyAllWindows()
plt.ioff()
plt.show()

########################################################################################

# import cv2
# import numpy as np
# import matplotlib.pyplot as plt
# import mediapipe as mp

# # -----------------------------
# # VIDEO PATH
# # -----------------------------
# # vid_path = r"D:\Lie Detection Data HTI\Lie_detection_ex2\Thermal_lie_detection_ex2\grey_manual\rahul_grey_manual.wmv"
# # vid_path = r"D:\Lie Detection Data HTI\Lie_detection_ex2\Thermal_lie_detection_ex2\grey_manual\shivam_grey_manual.wmv"
# vid_path = r"D:\Lie Detection Data HTI\Lie_detection_ex2\Thermal_lie_detection_ex2\grey_manual\sneha_grey_manual.wmv"

# cap = cv2.VideoCapture(vid_path)

# ret, frame = cap.read()
# if not ret:
#     print("Error reading video")
#     exit()

# # -----------------------------
# # MEDIAPIPE SETUP
# # -----------------------------
# mp_face_mesh = mp.solutions.face_mesh
# face_mesh = mp_face_mesh.FaceMesh(refine_landmarks=True)

# NOSE_TIP = 1  # MediaPipe nose tip index

# h_frame, w_frame, _ = frame.shape

# # -----------------------------
# # SELECT ROI
# # -----------------------------
# bbox = cv2.selectROI("Select ROI", frame, False)
# cv2.destroyWindow("Select ROI")

# x, y, w, h = [int(v) for v in bbox]

# # -----------------------------
# # DETECT NOSE IN FIRST FRAME
# # -----------------------------
# rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
# results = face_mesh.process(rgb)

# if not results.multi_face_landmarks:
#     print("Face not detected")
#     exit()

# landmarks = results.multi_face_landmarks[0]

# nose_x = int(landmarks.landmark[NOSE_TIP].x * w_frame)
# nose_y = int(landmarks.landmark[NOSE_TIP].y * h_frame)

# # -----------------------------
# # STORE RELATIVE OFFSET (KEY FIX)
# # -----------------------------
# dx = x - nose_x
# dy = y - nose_y

# box_w, box_h = w, h

# # -----------------------------
# # TRACKER INIT
# # -----------------------------
# tracker = cv2.TrackerCSRT_create()
# tracker.init(frame, bbox)

# # -----------------------------
# # SIGNAL + REFERENCE
# # -----------------------------
# signals = []
# reference = None
# threshold = 2

# # -----------------------------
# # PLOTTING
# # -----------------------------
# plt.ion()
# fig, ax = plt.subplots()

# ax.set_title("Signal with Nose-Based Recovery (Corrected)")
# ax.set_xlabel("Frame")
# ax.set_ylabel("Mean Intensity")

# # -----------------------------
# # LOOP
# # -----------------------------
# while True:
#     ret, frame = cap.read()
#     if not ret:
#         break

#     gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

#     # -----------------------------
#     # DETECT NOSE EVERY FRAME
#     # -----------------------------
#     rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
#     results = face_mesh.process(rgb)

#     nose_detected = False

#     if results.multi_face_landmarks:
#         landmarks = results.multi_face_landmarks[0]

#         nose_x = int(landmarks.landmark[NOSE_TIP].x * w_frame)
#         nose_y = int(landmarks.landmark[NOSE_TIP].y * h_frame)

#         nose_detected = True

#         # Draw nose point
#         cv2.circle(frame, (nose_x, nose_y), 3, (0, 0, 255), -1)

#     # -----------------------------
#     # TRACKER UPDATE
#     # -----------------------------
#     success, bbox = tracker.update(frame)

#     # -----------------------------
#     # IF TRACKING FAILS → RECOVER
#     # -----------------------------
#     if not success and nose_detected:

#         new_x = int(nose_x + dx)
#         new_y = int(nose_y + dy)

#         bbox = (new_x, new_y, box_w, box_h)

#         # Reinitialize tracker
#         tracker = cv2.TrackerCSRT_create()
#         tracker.init(frame, bbox)

#         print("Tracker recovered using nose (dx, dy)")

#     x, y, w, h = [int(v) for v in bbox]

#     # -----------------------------
#     # BOUNDARY CHECK (VERY IMPORTANT)
#     # -----------------------------
#     x = max(0, min(x, w_frame - 1))
#     y = max(0, min(y, h_frame - 1))
#     w = max(1, min(w, w_frame - x))
#     h = max(1, min(h, h_frame - y))

#     roi = gray[y:y+h, x:x+w]

#     if roi.size != 0:
#         mean_val = np.mean(roi)
#         signals.append(mean_val)

#         # Reference = first frame
#         if reference is None:
#             reference = mean_val

#         # -----------------------------
#         # SEGMENT COLORING
#         # -----------------------------
#         if len(signals) > 1:
#             x_vals = [len(signals)-2, len(signals)-1]
#             y_vals = [signals[-2], signals[-1]]

#             if (mean_val - reference) > threshold:
#                 color = 'red'
#             else:
#                 color = 'blue'

#             ax.plot(x_vals, y_vals, color=color)

#     # Draw bounding box
#     cv2.rectangle(frame, (x, y), (x+w, y+h), (0,255,0), 2)

#     # -----------------------------
#     # GRAPH UPDATE
#     # -----------------------------
#     ax.relim()
#     ax.autoscale_view()

#     plt.pause(0.001)

#     cv2.imshow("Tracking (Nose Recovery Fixed)", frame)

#     if cv2.waitKey(1) & 0xFF == 27:
#         break

# # -----------------------------
# # CLEANUP
# # -----------------------------
# cap.release()
# cv2.destroyAllWindows()
# plt.ioff()
# plt.show()