import cv2
import numpy as np
import matplotlib.pyplot as plt

# -----------------------------
# VIDEO PATH
# -----------------------------
vid_path = r"D:\Lie Detection Data HTI\Lie_detection_ex2\Thermal_lie_detection_ex2\grey_manual\rahul_grey_manual.wmv"
# vid_path = r"D:\Lie Detection Data HTI\Lie_detection_ex2\Thermal_lie_detection_ex2\aditi_grey_manual.wmv"
# vid_path = r"D:\Lie Detection Data HTI\Lie_detection_ex2\Thermal_lie_detection_ex2\grey_manual\krishna_grey_manual1.wmv"
# vid_path = r"D:\Lie Detection Data HTI\Lie_detection_ex2\Thermal_lie_detection_ex2\grey_manual\aditi_grey_manual.wmv"
# vid_path = r"D:\Lie Detection Data HTI\Lie_detection_ex2\Thermal_lie_detection_ex2\grey_manual\priyank_grey_manual.wmv"

cap = cv2.VideoCapture(vid_path)

ret, frame = cap.read()
if not ret:
    print("Error reading video")
    exit()

# -----------------------------
# VIDEO INFO
# -----------------------------
fps = cap.get(cv2.CAP_PROP_FPS)
total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
duration_sec = total_frames / fps

print(f"Video Duration: {int(duration_sec//60)}:{int(duration_sec%60):02d}")

# -----------------------------
# SELECT ROIss
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
# REFERENCE
# -----------------------------
reference = [None] * len(trackers)
threshold = 3

# -----------------------------
# PLOTTING (2 GRAPHS)
# -----------------------------
plt.ion()
fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(10, 8))

ax1.set_title("Live Scrolling Graph")
ax2.set_title("Full Signal Graph")

ax1.set_ylabel("Mean Intensity")
ax2.set_ylabel("Mean Intensity")

ax2.set_xlabel("Time (mm:ss)")

# scrolling window (seconds)
window_sec = 10

frame_count = 0

# -----------------------------
# LOOP
# -----------------------------
while True:
    ret, frame = cap.read()
    if not ret:
        break

    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

    current_time = frame_count / fps

    for i, tracker in enumerate(trackers):
        success, bbox = tracker.update(frame)

        if success:
            x, y, w, h = [int(v) for v in bbox]
            roi = gray[y:y+h, x:x+w]

            if roi.size != 0:
                mean_val = np.mean(roi)
                signals[i].append(mean_val)

                if reference[i] is None:
                    reference[i] = mean_val

                if len(signals[i]) > 1:
                    t1 = (frame_count - 1) / fps
                    t2 = frame_count / fps

                    y_vals = [signals[i][-2], signals[i][-1]]

                    # COLOR RULE
                    if (mean_val - reference[i]) > threshold:
                        color = 'red'
                    else:
                        color = 'blue'

                    # -----------------------------
                    # FULL GRAPH (ax2)
                    # -----------------------------
                    ax2.plot([t1, t2], y_vals, color=color)

                    # -----------------------------
                    # LIVE SCROLLING GRAPH (ax1)
                    # -----------------------------
                    ax1.plot([t1, t2], y_vals, color=color)

            cv2.rectangle(frame, (x, y), (x+w, y+h), (0,255,0), 2)

    # -----------------------------
    # SCROLLING WINDOW LOGIC
    # -----------------------------
    ax1.set_xlim(max(0, current_time - window_sec), current_time)

    # Auto scale both
    ax1.relim()
    ax1.autoscale_view()

    ax2.relim()
    ax2.autoscale_view()

    # -----------------------------
    # FORMAT TIME AXIS
    # -----------------------------
    def format_time(x, pos=None):
        m = int(x // 60)
        s = int(x % 60)
        return f"{m}:{s:02d}"

    ax1.xaxis.set_major_formatter(plt.FuncFormatter(format_time))
    ax2.xaxis.set_major_formatter(plt.FuncFormatter(format_time))

    plt.pause(0.001)

    cv2.imshow("Tracking", frame)

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