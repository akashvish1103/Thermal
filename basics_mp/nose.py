# import cv2
# import mediapipe as mp

# # Initialize MediaPipe
# mp_face_mesh = mp.solutions.face_mesh
# face_mesh = mp_face_mesh.FaceMesh(
#     static_image_mode=False,
#     max_num_faces=1,
#     refine_landmarks=True
# )

# # Nose landmark indices
# NOSE_LANDMARKS = [
#     193, 168, 417, 122, 351, 196, 419, 3, 248, 236,
#     456, 198, 420, 131, 360, 49, 279, 48,
#     278, 219, 439, 59, 289, 218, 438, 237,
#     457, 44, 19, 274
# ]

# # Open webcam (or replace with video path)
# cap = cv2.VideoCapture(0)

# while cap.isOpened():
#     ret, frame = cap.read()
#     if not ret:
#         break

#     # Flip for mirror view (optional but helpful)
#     frame = cv2.flip(frame, 1)

#     # Convert to RGB
#     rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

#     # Process with MediaPipe
#     results = face_mesh.process(rgb)

#     if results.multi_face_landmarks:
#         for face_landmarks in results.multi_face_landmarks:

#             h, w, _ = frame.shape

#             for idx in NOSE_LANDMARKS:
#                 lm = face_landmarks.landmark[idx]

#                 x = int(lm.x * w)
#                 y = int(lm.y * h)

#                 # Draw point
#                 cv2.circle(frame, (x, y), 2, (0, 255, 0), -1)

#                 # Decide label position based on x location
#                 if x < w // 3:  # LEFT side
#                     text_x = x - 60
#                     text_y = y
#                 elif x > 2 * w // 3:  # RIGHT side
#                     text_x = x + 20
#                     text_y = y
#                 else:  # CENTER (nose bridge)
#                     text_x = x
#                     text_y = y - 30

#                 # Draw simple line (no arrow)
#                 cv2.line(frame, (text_x, text_y), (x, y), (255, 0, 0), 1)

#                 # Draw index
#                 cv2.putText(
#                     frame,
#                     str(idx),
#                     (text_x, text_y),
#                     cv2.FONT_HERSHEY_SIMPLEX,
#                     0.2,
#                     (0, 0, 255),
#                     1,
#                     cv2.LINE_AA
#                 )

#     # Show output
#     cv2.imshow("Nose Landmarks with Index", frame)

#     # Press ESC to exit
#     if cv2.waitKey(100) & 0xFF == 27:
#         break

# cap.release()
# cv2.destroyAllWindows()





# import cv2
# import mediapipe as mp
# import math

# # Initialize MediaPipe
# mp_face_mesh = mp.solutions.face_mesh
# face_mesh = mp_face_mesh.FaceMesh(
#     static_image_mode=False,
#     max_num_faces=1,
#     refine_landmarks=True
# )

# # Nose landmark indices
# NOSE_LANDMARKS = [
#     193, 168, 417, 122, 351, 196, 419, 3, 248, 236,
#     456, 198, 420, 131, 360, 49, 279, 48,
#     278, 219, 439, 59, 289, 218, 438, 237,
#     457, 44, 19, 274
# ]

# cap = cv2.VideoCapture(0)

# while cap.isOpened():
#     ret, frame = cap.read()
#     if not ret:
#         break

#     frame = cv2.flip(frame, 1)
#     rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
#     results = face_mesh.process(rgb)

#     if results.multi_face_landmarks:
#         for face_landmarks in results.multi_face_landmarks:

#             h, w, _ = frame.shape

#             # 🔥 Step 1: Get center of nose region
#             xs, ys = [], []
#             for idx in NOSE_LANDMARKS:
#                 lm = face_landmarks.landmark[idx]
#                 xs.append(int(lm.x * w))
#                 ys.append(int(lm.y * h))

#             cx = int(sum(xs) / len(xs))
#             cy = int(sum(ys) / len(ys))

#             # 🔥 Step 2: Draw points + circular labels
#             radius = 100  # adjust for spacing

#             for i, idx in enumerate(NOSE_LANDMARKS):
#                 lm = face_landmarks.landmark[idx]

#                 x = int(lm.x * w)
#                 y = int(lm.y * h)

#                 # Draw landmark point
#                 cv2.circle(frame, (x, y), 3, (0, 255, 0), -1)

#                 # Compute circular label position
#                 angle = (i / len(NOSE_LANDMARKS)) * 2 * math.pi
#                 text_x = int(cx + radius * math.cos(angle))
#                 text_y = int(cy + radius * math.sin(angle))

#                 # Draw connecting line
#                 cv2.line(frame, (text_x, text_y), (x, y), (255, 0, 0), 1)

#                 # Draw label
#                 cv2.putText(
#                     frame,
#                     str(idx),
#                     (text_x, text_y),
#                     cv2.FONT_HERSHEY_SIMPLEX,
#                     0.,
#                     (0, 0, 255),
#                     1,
#                     cv2.LINE_AA
#                 )

#     cv2.imshow("Nose Landmarks (Circular Labels)", frame)

#     if cv2.waitKey(1) & 0xFF == 27:
#         break

# cap.release()
# cv2.destroyAllWindows()

import cv2
import mediapipe as mp
import math

# Initialize MediaPipe
mp_face_mesh = mp.solutions.face_mesh
face_mesh = mp_face_mesh.FaceMesh(
    static_image_mode=False,
    max_num_faces=1,
    refine_landmarks=True
)

# Nose landmark indices
NOSE_LANDMARKS = [
    193, 168, 417, 122, 351, 196, 419, 3, 248, 236,
    456, 198, 420, 131, 360, 49, 279, 48,
    278, 219, 439, 59, 289, 218, 438, 237,
    457, 44, 19, 274
]
new_landmarks = [98, 60, 20, 94, 326,290,327, 2]

NOSE_LANDMARKS = NOSE_LANDMARKS + new_landmarks
# Color palette for alternating lines
COLORS = [
    (255, 0, 0),    # Blue
    (0, 255, 0),    # Green
    (0, 0, 255),    # Red
    (255, 255, 0),  # Cyan
    (255, 0, 255),  # Magenta
    (0, 255, 255)   # Yellow
]

cap = cv2.VideoCapture(0)

while cap.isOpened():
    ret, frame = cap.read()
    if not ret:
        break

    frame = cv2.flip(frame, 1)
    rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    results = face_mesh.process(rgb)

    if results.multi_face_landmarks:
        for face_landmarks in results.multi_face_landmarks:

            h, w, _ = frame.shape

            # 🔥 Step 1: Compute center of nose region
            xs, ys = [], []
            for idx in NOSE_LANDMARKS:
                lm = face_landmarks.landmark[idx]
                xs.append(int(lm.x * w))
                ys.append(int(lm.y * h))

            cx = int(sum(xs) / len(xs))
            cy = int(sum(ys) / len(ys))

            # 🔥 Step 2: Draw circular labels
            radius = 110  # adjust spacing if needed

            for i, idx in enumerate(NOSE_LANDMARKS):
                lm = face_landmarks.landmark[idx]

                x = int(lm.x * w)
                y = int(lm.y * h)

                # Draw landmark point
                cv2.circle(frame, (x, y), 1, (0, 255, 0), -1)

                # Circular placement
                angle = (i / len(NOSE_LANDMARKS)) * 2 * math.pi
                text_x = int(cx + radius * math.cos(angle))
                text_y = int(cy + radius * math.sin(angle))

                # Select alternating color
                color = COLORS[i % len(COLORS)]

                # Draw connecting line
                cv2.line(frame, (text_x, text_y), (x, y), color, 1)

                # Draw label
                cv2.putText(
                    frame,
                    str(idx),
                    (text_x, text_y),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    0.3,
                    color,
                    1,
                    cv2.LINE_AA
                )

    cv2.imshow("Nose Landmarks (Clean Circular View)", frame)

    if cv2.waitKey(1) & 0xFF == 27:
        break

cap.release()
cv2.destroyAllWindows()