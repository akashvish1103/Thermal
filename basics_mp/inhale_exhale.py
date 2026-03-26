import mediapipe as mp
import cv2
import numpy as np
import matplotlib.pyplot as plt

# -----------------------------
# VIDEO PATH
# -----------------------------
# vid_path = r"D:\Lie Detection Data HTI\Lie_detection_ex2\Thermal_lie_detection_ex2\krishna_grey_manual1.wmv"
vid_path = r"d:\Lie Detection Data HTI\Lie_detection_ex2\Thermal_lie_detection_ex2\sneha_grey_manual.wmv"
# vid_path = r"D:\Lie Detection Data HTI\Lie_detection_ex2\Thermal_lie_detection_ex2\purva_grey_manual.wmv"
# vid_path = r"D:\Lie Detection Data HTI\Lie_detection_ex2\Thermal_lie_detection_ex2\grey_manual\jayesh_grey_manual.wmv"
# vid_path = r"D:\Lie Detection Data HTI\Lie_detection_ex2\Thermal_lie_detection_ex2\krishna_iron_exported.wmv"

cap = cv2.VideoCapture(vid_path)

# -----------------------------
# MEDIAPIPE
mp_face_mesh = mp.solutions.face_mesh
face_mesh = mp_face_mesh.FaceMesh(static_image_mode=False)

# -----------------------------
# LANDMARKS (your fixed ones)
# -----------------------------
# -----------------------------
BOX_LANDMARKS = [
    94, 97, 2, 98,          # left nostril
    326, 327, 294, 331, 
        60, 20, 98  
]

# -----------------------------
# GRAPH SETUP (LIVE)
# -----------------------------
plt.ion()   # interactive mode ON
fig, ax = plt.subplots()
x_data, y_data = [], []
line, = ax.plot(x_data, y_data)

ax.set_title("Live Breathing Signal")
ax.set_xlabel("Frame")
ax.set_ylabel("Intensity")

frame_id = 0

# -----------------------------
# LOOP
# -----------------------------
while True:
    ret, frame = cap.read()
    if not ret:
        break

    frame_id += 1

    h, w, _ = frame.shape

    # RGB for mediapipe
    rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    results = face_mesh.process(rgb)

    # GRAYSCALE (IMPORTANT)
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

    if results.multi_face_landmarks:
        for face_landmarks in results.multi_face_landmarks:

            points = []

            # get points
            for idx in BOX_LANDMARKS:
                lm = face_landmarks.landmark[idx]
                x = int(lm.x * w)
                y = int(lm.y * h)
                points.append((x, y))
                cv2.circle(frame, (x, y), 2, (0, 255, 0), -1)

            xs = [p[0] for p in points]
            ys = [p[1] for p in points]

            x_min, x_max = min(xs), max(xs)
            y_min, y_max = min(ys), max(ys)

            # margin
            # margin = 10
            margin = 5
            x_min = max(0, x_min - margin)
            x_max = min(w, x_max + margin)
            y_min = max(0, y_min - margin)
            y_max = min(h, y_max + margin)

            # draw box
            cv2.rectangle(frame, (x_min, y_min), (x_max, y_max), (255, 0, 0), 2)

            # -----------------------------
            # EXTRACT INTENSITY
            # -----------------------------
            roi = gray[y_min:y_max, x_min:x_max]

            if roi.size != 0:
                mean_intensity = np.mean(roi)

                # update graph data
                x_data.append(frame_id)
                y_data.append(mean_intensity)

                # limit size (last 200 frames)
                x_data = x_data[-200:]
                y_data = y_data[-200:]

                # update plot
                line.set_xdata(x_data)
                line.set_ydata(y_data)

                ax.relim()
                ax.autoscale_view()

                plt.draw()
                plt.pause(0.001)

    cv2.imshow("Breathing ROI", frame)

    if cv2.waitKey(100) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()