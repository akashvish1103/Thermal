import cv2
import numpy as np
import matplotlib.pyplot as plt
import pandas as pd

# -----------------------------
# SETTINGS
# -----------------------------
video_path = r"D:\Lie Detection Data HTI\Lie_detection_ex2\Thermal_lie_detection_ex2\grey_manual\sneha_grey_manual.wmv"
window_size = 200

# -----------------------------
# INIT
# -----------------------------
cap = cv2.VideoCapture(video_path)

def create_tracker():
    try:
        return cv2.TrackerCSRT_create()
    except:
        return cv2.legacy.TrackerCSRT_create()

tracker = create_tracker()
tracker_initialized = False

intensity_values = []
frame_ids = []

# -----------------------------
# FIRST FRAME → SELECT ROI
# -----------------------------
ret, frame = cap.read()
if not ret:
    print("Error reading video")
    exit()

bbox = cv2.selectROI("Select ROI", frame, False)
cv2.destroyWindow("Select ROI")

tracker.init(frame, bbox)
tracker_initialized = True

# -----------------------------
# GRAPH SETUP
# -----------------------------
plt.ion()
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

    success = False

    # -----------------------------
    # TRY TRACKING
    # -----------------------------
    if tracker_initialized:
        success, bbox = tracker.update(frame)

    # -----------------------------
    # IF TRACK LOST → HANDLE
    # -----------------------------
    if not success:
        cv2.putText(frame, "Tracking Lost - Press R to reselect ROI",
                    (30,50), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0,0,255), 2)

    else:
        x, y, w, h = map(int, bbox)

        x = max(0, x)
        y = max(0, y)

        cv2.rectangle(frame, (x, y), (x+w, y+h), (0,255,0), 2)

        roi = frame[y:y+h, x:x+w]

        if roi.size != 0:
            gray = cv2.cvtColor(roi, cv2.COLOR_BGR2GRAY)
            mean_intensity = np.mean(gray)

            intensity_values.append(mean_intensity)
            frame_ids.append(frame_count)

            cv2.putText(frame, f"{mean_intensity:.2f}",
                        (x, y-10), cv2.FONT_HERSHEY_SIMPLEX,
                        0.6, (0,255,0), 2)

    # -----------------------------
    # SHOW FRAME
    # -----------------------------
    cv2.imshow("Tracking ROI", frame)

    key = cv2.waitKey(30) & 0xFF

    # -----------------------------
    # PRESS R → RESELECT ROI
    # -----------------------------
    if key == ord('r'):
        bbox = cv2.selectROI("Reselect ROI", frame, False)
        cv2.destroyWindow("Reselect ROI")

        tracker = create_tracker()
        tracker.init(frame, bbox)
        tracker_initialized = True

    elif key == 27:
        break

    # -----------------------------
    # LIVE GRAPH (SCROLLING + ZOOM)
    # -----------------------------
    if len(intensity_values) > 5:
        data = intensity_values[-window_size:]

        line.set_xdata(np.arange(len(data)))
        line.set_ydata(data)

        ax.set_xlim(0, window_size)

        y_min = np.min(data)
        y_max = np.max(data)
        ax.set_ylim(y_min - 1, y_max + 1)

        plt.draw()
        plt.pause(0.01)

    frame_count += 1

# -----------------------------
# CLEANUP
# -----------------------------
cap.release()
cv2.destroyAllWindows()
plt.ioff()
plt.show()

# -----------------------------
# SAVE DATA
# -----------------------------
df = pd.DataFrame({
    "Frame": frame_ids,
    "Intensity": intensity_values
})

df.to_csv("breathing_signal.csv", index=False)
df.to_excel("breathing_signal.xlsx", index=False)

print("✅ Data saved!")