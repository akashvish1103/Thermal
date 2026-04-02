# import cv2
# import numpy as np
# import matplotlib.pyplot as plt
# from matplotlib.ticker import FuncFormatter

# # -----------------------------
# # VIDEO PATH
# # -----------------------------
# vid_path = r"D:\Lie Detection Data HTI\Lie_detection_ex2\Thermal_lie_detection_ex2\grey_manual\krishna_grey_manual1.wmv"

# # -----------------------------
# # CREATE TRACKER (CSRT is robust)
# # -----------------------------
# def create_tracker():
#     try:
#         return cv2.TrackerCSRT_create()
#     except:
#         return cv2.legacy.TrackerCSRT_create()

# # -----------------------------
# # FUNCTION: Convert time (sec) → mm:ss
# # -----------------------------
# def time_formatter(x, pos):
#     minutes = int(x // 60)
#     seconds = int(x % 60)
#     return f"{minutes:02d}:{seconds:02d}"

# # -----------------------------
# # LOAD VIDEO
# # -----------------------------
# cap = cv2.VideoCapture(vid_path)

# if not cap.isOpened():
#     print("Error opening video")
#     exit()

# # -----------------------------
# # READ FIRST FRAME (for ROI selection)
# # -----------------------------
# ret, frame = cap.read()
# if not ret:
#     print("Error reading first frame")
#     exit()

# # -----------------------------
# # USER SELECTS ROI (nose region)
# # -----------------------------
# bbox = cv2.selectROI("Select ROI (Nose Region)", frame, False)
# cv2.destroyWindow("Select ROI (Nose Region)")

# # -----------------------------
# # INITIALIZE TRACKER
# # -----------------------------
# tracker = create_tracker()
# tracker.init(frame, bbox)

# # -----------------------------
# # SETUP LIVE PLOT
# # -----------------------------
# plt.ion()  # interactive mode ON
# fig, ax = plt.subplots()

# x_vals = []   # time values (in seconds)
# y_vals = []   # mean intensity values

# line, = ax.plot([], [])

# ax.set_title("Breathing Signal (Mean Intensity vs Time)")
# ax.set_xlabel("Time (mm:ss)")
# ax.set_ylabel("Mean Intensity")

# # format x-axis to mm:ss
# ax.xaxis.set_major_formatter(FuncFormatter(time_formatter))

# # -----------------------------
# # MAIN LOOP
# # -----------------------------
# while True:
#     ret, frame = cap.read()
#     if not ret:
#         break

#     # -----------------------------
#     # GET CURRENT VIDEO TIME (ms → sec)
#     # -----------------------------
#     t_ms = cap.get(cv2.CAP_PROP_POS_MSEC)   # time in milliseconds
#     t_sec = t_ms / 1000.0                   # convert to seconds

#     # -----------------------------
#     # TRACK ROI
#     # -----------------------------
#     success, bbox = tracker.update(frame)

#     if success:
#         x, y, w, h = [int(v) for v in bbox]

#         # Extract ROI
#         roi = frame[y:y+h, x:x+w]

#         # Convert to grayscale if needed
#         if len(roi.shape) == 3:
#             roi_gray = cv2.cvtColor(roi, cv2.COLOR_BGR2GRAY)
#         else:
#             roi_gray = roi

#         # -----------------------------
#         # COMPUTE MEAN INTENSITY
#         # -----------------------------
#         mean_val = np.mean(roi_gray)

#         # Store values
#         x_vals.append(t_sec)
#         y_vals.append(mean_val)

#         # -----------------------------
#         # DRAW BOUNDING BOX
#         # -----------------------------
#         cv2.rectangle(frame, (x, y), (x+w, y+h), (0, 255, 0), 2)

#         # -----------------------------
#         # UPDATE LIVE PLOT
#         # -----------------------------
#         line.set_xdata(x_vals)
#         line.set_ydata(y_vals)

#         ax.relim()               # recompute limits
#         ax.autoscale_view()     # rescale axes

#         plt.draw()
#         plt.pause(0.001)

#     else:
#         # If tracking fails
#         cv2.putText(frame, "Tracking Failed", (50, 50),
#                     cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)

#     # -----------------------------
#     # DISPLAY FRAME
#     # -----------------------------
#     cv2.imshow("Tracking", frame)

#     # Small delay for window refresh + key press
#     if cv2.waitKey(1) & 0xFF == ord('q'):
#         break

# # -----------------------------
# # CLEANUP
# # -----------------------------
# cap.release()
# cv2.destroyAllWindows()

# plt.ioff()
# plt.show()

#######################################################################

import cv2
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.ticker import FuncFormatter

# -----------------------------
# VIDEO PATH
# -----------------------------
vid_path = r"D:\Lie Detection Data HTI\Lie_detection_ex2\Thermal_lie_detection_ex2\grey_manual\krishna_grey_manual1.wmv"

# -----------------------------
# CREATE TRACKER
# -----------------------------
def create_tracker():
    try:
        return cv2.TrackerCSRT_create()
    except:
        return cv2.legacy.TrackerCSRT_create()

# -----------------------------
# TIME FORMATTER (mm:ss)
# -----------------------------
def time_formatter(x, pos):
    minutes = int(x // 60)
    seconds = int(x % 60)
    return f"{minutes:02d}:{seconds:02d}"

# -----------------------------
# LOAD VIDEO
# -----------------------------
cap = cv2.VideoCapture(vid_path)

if not cap.isOpened():
    print("Error opening video")
    exit()

# -----------------------------
# READ FIRST FRAME
# -----------------------------
ret, frame = cap.read()
if not ret:
    print("Error reading first frame")
    exit()

# -----------------------------
# SELECT ROI
# -----------------------------
bbox = cv2.selectROI("Select ROI", frame, False)
cv2.destroyWindow("Select ROI")

# -----------------------------
# INIT TRACKER
# -----------------------------
tracker = create_tracker()
tracker.init(frame, bbox)

# -----------------------------
# SETUP PLOTS (2 GRAPHS)
# -----------------------------
plt.ion()

fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(10, 6))

# Data storage
x_vals = []
y_vals = []

# Lines
line_scroll, = ax1.plot([], [])
line_full, = ax2.plot([], [])

# Titles
ax1.set_title("Scrolling Signal (Last 20 sec)")
ax2.set_title("Full Signal")

# Labels
ax1.set_ylabel("Intensity")
ax2.set_ylabel("Intensity")
ax2.set_xlabel("Time (mm:ss)")

# Time formatter
ax1.xaxis.set_major_formatter(FuncFormatter(time_formatter))
ax2.xaxis.set_major_formatter(FuncFormatter(time_formatter))

# Scrolling window size (seconds)
WINDOW_SIZE = 20

# -----------------------------
# MAIN LOOP
# -----------------------------
while True:
    ret, frame = cap.read()
    if not ret:
        break

    # Get time
    t_ms = cap.get(cv2.CAP_PROP_POS_MSEC)
    t_sec = t_ms / 1000.0

    # Track ROI
    success, bbox = tracker.update(frame)

    if success:
        x, y, w, h = [int(v) for v in bbox]
        roi = frame[y:y+h, x:x+w]

        # Convert to grayscale
        if len(roi.shape) == 3:
            roi_gray = cv2.cvtColor(roi, cv2.COLOR_BGR2GRAY)
        else:
            roi_gray = roi

        # Mean intensity
        mean_val = np.mean(roi_gray)

        # Store data
        x_vals.append(t_sec)
        y_vals.append(mean_val)

        # Draw bbox
        cv2.rectangle(frame, (x, y), (x+w, y+h), (0,255,0), 2)

        # -----------------------------
        # GRAPH 1: SCROLLING WINDOW
        # -----------------------------
        x_scroll = []
        y_scroll = []

        for xt, yt in zip(x_vals, y_vals):
            if xt >= t_sec - WINDOW_SIZE:
                x_scroll.append(xt)
                y_scroll.append(yt)

        line_scroll.set_xdata(x_scroll)
        line_scroll.set_ydata(y_scroll)

        ax1.set_xlim(max(0, t_sec - WINDOW_SIZE), t_sec)

        if len(y_scroll) > 0:
            ax1.set_ylim(min(y_scroll) - 1, max(y_scroll) + 1)

        # -----------------------------
        # GRAPH 2: FULL SIGNAL
        # -----------------------------
        line_full.set_xdata(x_vals)
        line_full.set_ydata(y_vals)

        ax2.relim()
        ax2.autoscale_view()

        # -----------------------------
        # UPDATE PLOTS
        # -----------------------------
        plt.draw()
        plt.pause(0.001)

    else:
        cv2.putText(frame, "Tracking Failed", (50,50),
                    cv2.FONT_HERSHEY_SIMPLEX, 1, (0,0,255), 2)

    # Show frame
    cv2.imshow("Tracking", frame)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# -----------------------------
# CLEANUP
# -----------------------------
cap.release()
cv2.destroyAllWindows()

plt.ioff()
plt.show()