# import mediapipe as mp
# import cv2
# import numpy as np

# vid_path = r"D:\Lie Detection Data HTI\Lie_detection_ex2\Thermal_lie_detection_ex2\krishna_grey_manual1.wmv"

# cap = cv2.VideoCapture(vid_path)

# fps = cap.get(cv2.CAP_PROP_FPS)
# print("FPS:", fps)

# while True:
#     ret, frame = cap.read()

#     if not ret:
#         break

#     cv2.imshow("My Video Window", frame)

#     if cv2.waitKey(100) & 0xFF == ord('q'):
#         break

# cap.release()
##############################################################################################################

# import mediapipe as mp
# import cv2
# import numpy as np

# # vid_path = r"D:\Lie Detection Data HTI\Lie_detection_ex2\Thermal_lie_detection_ex2\krishna_grey_manual1.wmv"
# vid_path = r"d:\Lie Detection Data HTI\Lie_detection_ex2\Thermal_lie_detection_ex2\sneha_grey_manual.wmv"

# cap = cv2.VideoCapture(vid_path)

# mp_face_mesh = mp.solutions.face_mesh
# face_mesh = mp_face_mesh.FaceMesh(static_image_mode=False)

# # 🔥 Placeholder landmark indices (replace later)
# BOX_LANDMARKS = [49, 98, 279, 327]   #219, 98, 360, 327

# fps = cap.get(cv2.CAP_PROP_FPS)
# print("FPS:", fps)

# while True:
#     ret, frame = cap.read()
#     if not ret:
#         break

#     h, w, _ = frame.shape

#     # Convert to RGB
#     rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
#     results = face_mesh.process(rgb)

#     if results.multi_face_landmarks:
#         for face_landmarks in results.multi_face_landmarks:

#             points = []

#             # 🔥 Get coordinates of placeholder landmarks
#             for idx in BOX_LANDMARKS:
#                 lm = face_landmarks.landmark[idx]
#                 x = int(lm.x * w)
#                 y = int(lm.y * h)
#                 points.append((x, y))

#                 # draw the points
#                 cv2.circle(frame, (x, y), 3, (0, 255, 0), -1)

#             # 🔥 Create bounding box from these points
#             xs = [p[0] for p in points]
#             ys = [p[1] for p in points]

#             x_min, x_max = min(xs), max(xs)
#             y_min, y_max = min(ys), max(ys)

#             # Draw bounding box
#             cv2.rectangle(frame, (x_min, y_min), (x_max, y_max), (255, 0, 0), 2)

#     cv2.imshow("Bounding Box (Landmark-based)", frame)

#     if cv2.waitKey(30) & 0xFF == ord('q'):
#         break

# cap.release()
# cv2.destroyAllWindows()


###############################################

import mediapipe as mp
import cv2
import numpy as np

# -----------------------------
# VIDEO PATH
# -----------------------------
# vid_path = r"d:\Lie Detection Data HTI\Lie_detection_ex2\Thermal_lie_detection_ex2\sneha_grey_manual.wmv"
vid_path = r"D:\Lie Detection Data HTI\Lie_detection_ex2\Thermal_lie_detection_ex2\krishna_grey_manual1.wmv"

cap = cv2.VideoCapture(vid_path)

# -----------------------------
# MEDIAPIPE SETUP
# -----------------------------
mp_face_mesh = mp.solutions.face_mesh
face_mesh = mp_face_mesh.FaceMesh(static_image_mode=False)

# -----------------------------
# STABLE LANDMARKS (NOSTRILS + BELOW NOSE)
# -----------------------------
BOX_LANDMARKS = [
    94, 97, 2, 98,          # left nostril
    326, 327, 294, 331, 
        60, 20, 98    # right nostril                  # below nose (important)
]

fps = cap.get(cv2.CAP_PROP_FPS)
print("FPS:", fps)

# -----------------------------
# LOOP
# -----------------------------
while True:
    ret, frame = cap.read()
    if not ret:
        break

    h, w, _ = frame.shape

    # Convert to RGB
    rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    results = face_mesh.process(rgb)

    if results.multi_face_landmarks:
        for face_landmarks in results.multi_face_landmarks:

            points = []

            # -----------------------------
            # GET LANDMARK POINTS
            # -----------------------------
            for idx in BOX_LANDMARKS:
                lm = face_landmarks.landmark[idx]
                x = int(lm.x * w)
                y = int(lm.y * h)
                points.append((x, y))

                # draw landmarks
                cv2.circle(frame, (x, y), 2, (0, 255, 0), -1)

            # -----------------------------
            # CREATE BOUNDING BOX
            # -----------------------------
            xs = [p[0] for p in points]
            ys = [p[1] for p in points]

            x_min, x_max = min(xs), max(xs)
            y_min, y_max = min(ys), max(ys)

            # -----------------------------
            # ADD MARGIN (VERY IMPORTANT)
            # -----------------------------
            margin_x = 8
            margin_y = 8

            x_min = max(0, x_min - margin_x)
            x_max = min(w, x_max + margin_x)
            y_min = max(0, y_min - margin_y)
            y_max = min(h, y_max + margin_y)

            # -----------------------------
            # OPTIONAL: FALLBACK USING NOSE TIP
            # (if box becomes weird)
            # -----------------------------
            if (y_max - y_min) < 10:
                nose_tip = face_landmarks.landmark[1]
                x_center = int(nose_tip.x * w)
                y_center = int(nose_tip.y * h)

                box_w = 60
                box_h = 40

                x_min = max(0, x_center - box_w // 2)
                x_max = min(w, x_center + box_w // 2)
                y_min = min(h, y_center + 5)
                y_max = min(h, y_center + box_h)

            # -----------------------------
            # DRAW FINAL BOX
            # -----------------------------
            cv2.rectangle(frame, (x_min, y_min), (x_max, y_max), (255, 0, 0), 2)

    cv2.imshow("Stable Nose ROI", frame)

    if cv2.waitKey(100) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()