import cv2
import numpy as np
import matplotlib.pyplot as plt

# vid_path = r"D:\Lie Detection Data HTI\Lie_detection_ex2\Thermal_lie_detection_ex2\grey_manual\krishna_grey_manual1.wmv"
# vid_path = r"D:\Lie Detection Data HTI\Lie_detection_ex2\Thermal_lie_detection_ex2\grey_manual\sneha_grey_manual.wmv"
# vid_path = r"D:\Lie Detection Data HTI\Lie_detection_ex2\Thermal_lie_detection_ex2\grey_manual\purva_grey_manual.wmv"
vid_path = r"D:\Lie Detection Data HTI\Lie_detection_ex2\Thermal_lie_detection_ex2\aditi_grey_manual.wmv"
# vid_path = r"D:\Lie Detection Data HTI\Lie_detection_ex2\Thermal_lie_detection_ex2\krishna_grey_20-40.mpg"
# vid_path = r"D:\Lie Detection Data HTI\Lie_detection_ex2\Thermal_lie_detection_ex2\purva_grey_manual.wmv"
# vid_path = r"D:\Lie Detection Data HTI\Lie_detection_ex2\Thermal_lie_detection_ex2\purva_iron_exported.wmv"
# vid_path = r"D:\Lie Detection Data HTI\Lie_detection_ex2\Thermal_lie_detection_ex2\grey_manual\shivam_grey_manual.wmv"
# vid_path = r"D:\Lie Detection Data HTI\Lie_detection_ex2\Thermal_lie_detection_ex2\grey_manual\priyank_grey_manual.wmv"
cap = cv2.VideoCapture(vid_path)

ret, frame = cap.read()

# Select multiple ROIs
bboxes = cv2.selectROIs("Select Objects", frame, False)
cv2.destroyWindow("Select Objects")

trackers = []
signals = []   # list of lists (one per ROI)

# Create tracker + signal list for each ROI
for bbox in bboxes:
    tracker = cv2.TrackerCSRT_create()
    tracker.init(frame, bbox)
    trackers.append(tracker)
    signals.append([])

# ---------------------------
# Setup LIVE plotting
# ---------------------------
plt.ion()
fig, ax = plt.subplots()

lines = []
for i in range(len(trackers)):
    line, = ax.plot([], [], label=f'ROI {i}')
    lines.append(line)

ax.set_title("Live Multi-ROI Signals")
ax.set_xlabel("Frame")
ax.set_ylabel("Mean Intensity")
ax.legend()

frame_count = 0

# ---------------------------
# Loop
# ---------------------------
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

                # Update graph line
                lines[i].set_data(range(len(signals[i])), signals[i])

            # Draw box
            cv2.rectangle(frame, (x,y), (x+w, y+h), (0,255,0), 2)

    # Adjust graph dynamically
    ax.relim()
    ax.autoscale_view()

    plt.pause(0.001)

    cv2.imshow("Multi Tracking", frame)

    if cv2.waitKey(1) & 0xFF == 27:
        break

cap.release()
cv2.destroyAllWindows()
plt.ioff()
plt.show()