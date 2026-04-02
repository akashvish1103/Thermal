# import cv2
# import numpy as np
# import matplotlib.pyplot as plt
# from matplotlib.collections import LineCollection

# # ---------------------------
# # Temperature conversion
# # ---------------------------
# def get_temp_from_pixel(pixel_value):
#     m = 0.05891454 
#     b = 30.07676744
#     return m * pixel_value + b

# # ---------------------------
# # Moving average (no edge distortion)
# # ---------------------------
# def moving_average(signal, k=5):
#     if len(signal) < k:
#         return signal

#     smooth = np.convolve(signal, np.ones(k)/k, mode='valid')

#     pad_left = [smooth[0]] * (k//2)
#     pad_right = [smooth[-1]] * (k//2)

#     return np.concatenate([pad_left, smooth, pad_right])

# # ---------------------------
# # VIDEO
# # ---------------------------
# vid_path = r"C:\Users\Akash Vishwakarma\Downloads\krishna_grey_manual1.mp4"
# cap = cv2.VideoCapture(vid_path)

# ret, frame = cap.read()
# if not ret:
#     print("Error reading video")
#     exit()

# # ---------------------------
# # SELECT 2 ROIs
# # ---------------------------
# print("Select NOSE ROI (breathing)")
# bbox_nose = cv2.selectROI("Nose ROI", frame, False)
# cv2.destroyWindow("Nose ROI")

# print("Select FOREHEAD ROI (stress)")
# bbox_head = cv2.selectROI("Forehead ROI", frame, False)
# cv2.destroyWindow("Forehead ROI")

# # ---------------------------
# # TRACKERS
# # ---------------------------
# tracker_nose = cv2.TrackerCSRT_create()
# tracker_head = cv2.TrackerCSRT_create()

# tracker_nose.init(frame, bbox_nose)
# tracker_head.init(frame, bbox_head)

# # ---------------------------
# # GRAPH SETUP
# # ---------------------------
# plt.ion()

# fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(8,6))

# # Breathing graph
# line_breath, = ax1.plot([], [])
# ax1.set_title("Breathing Signal (Nose)")
# ax1.set_ylabel("Temp (°C)")

# # Forehead graph (color-coded)
# ax2.set_title("Stress Signal (Forehead)")
# ax2.set_xlabel("Frame")
# ax2.set_ylabel("Temp (°C)")

# # ---------------------------
# # DATA STORAGE
# # ---------------------------
# x_data = []
# y_breath = []
# y_head = []

# frame_count = 0
# MAX_POINTS = 200

# # Threshold for stress (tune this)
# THRESHOLD = 35.0

# # ---------------------------
# # MAIN LOOP
# # ---------------------------
# while True:
#     ret, frame = cap.read()
#     if not ret:
#         break

#     gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

#     # Update trackers
#     success_nose, bbox_nose = tracker_nose.update(frame)
#     success_head, bbox_head = tracker_head.update(frame)

#     if success_nose and success_head:

#         # ---------------------------
#         # NOSE (BREATHING)
#         # ---------------------------
#         x1, y1, w1, h1 = [int(v) for v in bbox_nose]
#         roi_nose = gray[y1:y1+h1, x1:x1+w1]

#         mean_nose = np.mean(roi_nose)
#         temp_nose = get_temp_from_pixel(mean_nose)

#         # ---------------------------
#         # FOREHEAD (STRESS)
#         # ---------------------------
#         x2, y2, w2, h2 = [int(v) for v in bbox_head]
#         roi_head = gray[y2:y2+h2, x2:x2+w2]

#         mean_head = np.mean(roi_head)
#         temp_head = get_temp_from_pixel(mean_head)

#         # ---------------------------
#         # STORE DATA
#         # ---------------------------
#         x_data.append(frame_count)
#         y_breath.append(temp_nose)
#         y_head.append(temp_head)

#         # Smooth breathing signal
#         y_breath_smooth = moving_average(y_breath, k=5)

#         # Limit window
#         if len(x_data) > MAX_POINTS:
#             x_data = x_data[-MAX_POINTS:]
#             y_breath = y_breath[-MAX_POINTS:]
#             y_head = y_head[-MAX_POINTS:]
#             y_breath_smooth = y_breath_smooth[-MAX_POINTS:]

#         # ---------------------------
#         # UPDATE BREATH GRAPH
#         # ---------------------------
#         line_breath.set_xdata(x_data)
#         line_breath.set_ydata(y_breath_smooth)

#         ax1.relim()
#         ax1.autoscale_view()

#         # ---------------------------
#         # UPDATE FOREHEAD GRAPH (COLOR CODED)
#         # ---------------------------
#         ax2.clear()
#         ax2.set_title("Stress Signal (Forehead)")
#         ax2.set_xlabel("Frame")
#         ax2.set_ylabel("Temp (°C)")

#         # Create colored segments
#         points = np.array([x_data, y_head]).T.reshape(-1,1,2)
#         segments = np.concatenate([points[:-1], points[1:]], axis=1)

#         colors = []
#         for val in y_head[:-1]:
#             if val > THRESHOLD:
#                 colors.append('red')
#             else:
#                 colors.append('blue')

#         lc = LineCollection(segments, colors=colors, linewidths=2)
#         ax2.add_collection(lc)

#         ax2.set_xlim(min(x_data), max(x_data))
#         ax2.set_ylim(min(y_head)-0.05, max(y_head)+0.05)

#         # ---------------------------
#         # DRAW BOXES
#         # ---------------------------
#         cv2.rectangle(frame, (x1,y1), (x1+w1,y1+h1), (255,0,0), 2)  # nose
#         cv2.rectangle(frame, (x2,y2), (x2+w2,y2+h2), (0,255,0), 2)  # forehead

#         frame_count += 1

#         plt.draw()
#         plt.pause(0.001)

#     else:
#         cv2.putText(frame, "Tracking Lost", (50,50),
#                     cv2.FONT_HERSHEY_SIMPLEX, 1, (0,0,255), 2)

#     cv2.imshow("Tracking", frame)

#     if cv2.waitKey(1) & 0xFF == 27:
#         break

# # ---------------------------
# # CLEANUP
# # ---------------------------
# cap.release()
# cv2.destroyAllWindows()
# plt.ioff()
# plt.show()
####################################################
# Added 3 graphs - raw breathing, smoothed breathing, and forehead temperature


#########################################################################

import cv2
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.ticker as ticker
from matplotlib.collections import LineCollection

# =========================================================
# 🔴 USER SETTINGS (CHANGE HERE EASILY)
# =========================================================

THRESHOLD_TEMP = 0.1   # 🔥 CHANGE THIS (in °C)
SMOOTH_K = 10           # smoothing strength for breathing

# =========================================================
# Temperature conversion
# =========================================================
def get_temp_from_pixel(pixel_value):
    m = 0.05891454 
    b = 30.07676744
    return m * pixel_value + b

# =========================================================
# Moving average (no edge distortion)
# =========================================================
def moving_average(signal, k=5):
    if len(signal) < k:
        return signal

    smooth = np.convolve(signal, np.ones(k)/k, mode='valid')

    pad_left = [smooth[0]] * (k//2)
    pad_right = [smooth[-1]] * (k//2)

    return np.concatenate([pad_left, smooth, pad_right])

# =========================================================
# Time formatter (mm:ss)
# =========================================================
def format_time(x, pos):
    mins = int(x // 60)
    secs = int(x % 60)
    return f"{mins:02d}:{secs:02d}"

# =========================================================
# VIDEO
# =========================================================
vid_path = r"C:\Users\Akash Vishwakarma\Downloads\krishna_grey_manual1.mp4"
cap = cv2.VideoCapture(vid_path)

if not cap.isOpened():
    print("Error opening video")
    exit()

fps = cap.get(cv2.CAP_PROP_FPS)

ret, frame = cap.read()
if not ret:
    print("Error reading frame")
    exit()

# =========================================================
# SELECT ROIs
# =========================================================
print("Select NOSE ROI")
bbox_nose = cv2.selectROI("Nose ROI", frame, False)
cv2.destroyWindow("Nose ROI")

print("Select FOREHEAD ROI")
bbox_head = cv2.selectROI("Forehead ROI", frame, False)
cv2.destroyWindow("Forehead ROI")

# =========================================================
# TRACKERS
# =========================================================
tracker_nose = cv2.TrackerCSRT_create()
tracker_head = cv2.TrackerCSRT_create()

tracker_nose.init(frame, bbox_nose)
tracker_head.init(frame, bbox_head)

# =========================================================
# GRAPH SETUP (3 graphs)
# =========================================================
plt.ion()

fig, (ax1, ax2, ax3) = plt.subplots(3, 1, figsize=(8,9))

# Nose RAW
line_raw, = ax1.plot([], [])
ax1.set_title("Nose Raw Temperature")

# Nose SMOOTHED
line_smooth, = ax2.plot([], [])
ax2.set_title("Nose Smoothed Temperature")

# Forehead (color-coded)
ax3.set_title("Forehead Stress Signal (Color-coded)")

for ax in [ax1, ax2, ax3]:
    ax.set_ylabel("Temp (°C)")
    ax.xaxis.set_major_formatter(ticker.FuncFormatter(format_time))

ax3.set_xlabel("Time (mm:ss)")

# =========================================================
# DATA STORAGE
# =========================================================
x_data = []
y_nose = []
y_head = []

frame_count = 0
MAX_POINTS = 200

baseline = None  # 🔥 baseline for forehead

# =========================================================
# MAIN LOOP
# =========================================================
while True:
    ret, frame = cap.read()
    if not ret:
        break

    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

    success_nose, bbox_nose = tracker_nose.update(frame)
    success_head, bbox_head = tracker_head.update(frame)

    if success_nose and success_head:

        # ---------------------------
        # 👃 NOSE (Breathing)
        # ---------------------------
        x1, y1, w1, h1 = [int(v) for v in bbox_nose]
        roi_nose = gray[y1:y1+h1, x1:x1+w1]
        temp_nose = get_temp_from_pixel(np.mean(roi_nose))

        # ---------------------------
        # 🧠 FOREHEAD (Stress)
        # ---------------------------
        x2, y2, w2, h2 = [int(v) for v in bbox_head]
        roi_head = gray[y2:y2+h2, x2:x2+w2]
        temp_head = get_temp_from_pixel(np.mean(roi_head))

        # ---------------------------
        # Time (seconds)
        # ---------------------------
        time_sec = frame_count / fps

        # Store data
        x_data.append(time_sec)
        y_nose.append(temp_nose)
        y_head.append(temp_head)

        # Set baseline from FIRST frame
        if baseline is None:
            baseline = temp_head

        # Smooth breathing signal
        y_nose_smooth = moving_average(y_nose, k=SMOOTH_K)

        # Limit window size
        if len(x_data) > MAX_POINTS:
            x_data = x_data[-MAX_POINTS:]
            y_nose = y_nose[-MAX_POINTS:]
            y_head = y_head[-MAX_POINTS:]
            y_nose_smooth = y_nose_smooth[-MAX_POINTS:]

        # =========================================================
        # UPDATE GRAPHS
        # =========================================================

        # ----------- Nose RAW -----------
        line_raw.set_xdata(x_data)
        line_raw.set_ydata(y_nose)

        # ----------- Nose SMOOTHED -----------
        line_smooth.set_xdata(x_data)
        line_smooth.set_ydata(y_nose_smooth)

        # ----------- Forehead (COLOR CODED) -----------
        ax3.clear()
        ax3.set_title("Forehead Stress Signal (Color-coded)")
        ax3.set_xlabel("Time (mm:ss)")
        ax3.set_ylabel("Temp (°C)")
        ax3.xaxis.set_major_formatter(ticker.FuncFormatter(format_time))

        if len(x_data) > 1:
            points = np.array([x_data, y_head]).T.reshape(-1,1,2)
            segments = np.concatenate([points[:-1], points[1:]], axis=1)

            colors = []
            for val in y_head[:-1]:
                # 🔥 THRESHOLD LOGIC
                if val >= baseline + THRESHOLD_TEMP:
                    colors.append('red')   # stress
                else:
                    colors.append('blue')  # normal

            lc = LineCollection(segments, colors=colors, linewidths=2)
            ax3.add_collection(lc)

            ax3.set_xlim(min(x_data), max(x_data))

            ymin = min(y_head)
            ymax = max(y_head)
            pad = (ymax - ymin) * 0.4 if ymax != ymin else 0.01
            ax3.set_ylim(ymin - pad, ymax + pad)

        # ----------- Auto scaling for nose graphs -----------
        for ax, y in zip([ax1, ax2], [y_nose, y_nose_smooth]):
            if len(y) > 0:
                ymin, ymax = min(y), max(y)
                pad = (ymax - ymin) * 0.4 if ymax != ymin else 0.01
                ax.set_ylim(ymin - pad, ymax + pad)
                ax.set_xlim(min(x_data), max(x_data))

        plt.draw()
        plt.pause(0.001)

        frame_count += 1

        # Draw bounding boxes
        cv2.rectangle(frame, (x1,y1), (x1+w1,y1+h1), (255,0,0), 2)
        cv2.rectangle(frame, (x2,y2), (x2+w2,y2+h2), (0,255,0), 2)

        # Optional: display status
        status = "STRESS" if temp_head >= baseline + THRESHOLD_TEMP else "NORMAL"
        cv2.putText(frame, status, (50,100),
                    cv2.FONT_HERSHEY_SIMPLEX, 1,
                    (0,0,255) if status=="STRESS" else (255,0,0), 2)

    else:
        cv2.putText(frame, "Tracking Lost", (50,50),
                    cv2.FONT_HERSHEY_SIMPLEX, 1, (0,0,255), 2)

    cv2.imshow("Tracking", frame)

    if cv2.waitKey(1) & 0xFF == 27:
        break

# =========================================================
# CLEANUP
# =========================================================
cap.release()
cv2.destroyAllWindows()
plt.ioff()
plt.show()