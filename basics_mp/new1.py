import cv2
import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
import datetime
import os

# -----------------------------
# SETTINGS
# -----------------------------
video_path = r"D:\Lie Detection Data HTI\Lie_detection_ex2\Thermal_lie_detection_ex2\grey_manual\krishna_grey_manual1.wmv"

save_folder = r"C:\Users\Akash Vishwakarma\Desktop\Thermal_Analysis\basics_mp\output_files"
window_size = 200

os.makedirs(save_folder, exist_ok=True)

# -----------------------------
# INIT
# -----------------------------
cap = cv2.VideoCapture(video_path)
fps = cap.get(cv2.CAP_PROP_FPS)
print("FPS:", fps)

def create_tracker():
    try:
        return cv2.TrackerCSRT_create()
    except:
        return cv2.legacy.TrackerCSRT_create()

tracker = create_tracker()

intensity_values = []
frame_ids = []
all_pixel_data = []

# -----------------------------
# FUNCTIONS
# -----------------------------
def moving_average(signal, k=7):
    return np.convolve(signal, np.ones(k)/k, mode='same')

def detect_breathing(signal):
    inhale_idx = []
    exhale_idx = []

    for i in range(1, len(signal)-1):
        if signal[i] > signal[i-1] and signal[i] > signal[i+1]:
            exhale_idx.append(i)

        if signal[i] < signal[i-1] and signal[i] < signal[i+1]:
            inhale_idx.append(i)

    return inhale_idx, exhale_idx

# 🔥 NEW: classify peaks (stress vs normal)
def classify_peaks(exhale_idx, fps, threshold=1.5):
    normal_peaks = []
    stress_peaks = []

    if len(exhale_idx) < 2:
        return normal_peaks, stress_peaks

    intervals = np.diff(exhale_idx) / fps

    for i, interval in enumerate(intervals):
        if interval < threshold:
            stress_peaks.append(exhale_idx[i+1])
        else:
            normal_peaks.append(exhale_idx[i+1])

    return normal_peaks, stress_peaks

# -----------------------------
# ROI SELECTION
# -----------------------------
ret, frame = cap.read()
if not ret:
    print("Error reading video")
    exit()

bbox = cv2.selectROI("Select ROI", frame, False)
cv2.destroyWindow("Select ROI")

tracker.init(frame, bbox)

# -----------------------------
# GRAPH SETUP
# -----------------------------
plt.ion()
fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(8, 6))

line_raw, = ax1.plot([], [])
ax1.set_title("Raw Intensity Signal")

ax2.set_title("Smoothed Signal (Breathing + Stress)")

plt.show(block=False)

# -----------------------------
# LOOP
# -----------------------------
frame_count = 0
bpm = 0

while True:
    ret, frame = cap.read()
    if not ret:
        break

    success, bbox = tracker.update(frame)

    if success:
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

            all_pixel_data.append(gray.flatten())

    cv2.imshow("Tracking ROI", frame)

    if cv2.waitKey(10) & 0xFF == 27:
        break

    # -----------------------------
    # GRAPH + BPM
    # -----------------------------
    if len(intensity_values) > 20:

        data = intensity_values[-window_size:]
        x_vals = np.arange(len(data))

        # RAW GRAPH
        line_raw.set_xdata(x_vals)
        line_raw.set_ydata(data)
        ax1.set_xlim(0, window_size)
        ax1.set_ylim(np.min(data)-1, np.max(data)+1)

        # SMOOTH
        smooth_data = moving_average(data)

        inhale_idx, exhale_idx = detect_breathing(smooth_data)

        # 🔥 classify peaks
        normal_peaks, stress_peaks = classify_peaks(exhale_idx, fps)

        # BPM
        if len(exhale_idx) > 1:
            peak_intervals = np.diff(exhale_idx) / fps
            avg_time = np.mean(peak_intervals)
            if avg_time > 0:
                bpm = 60 / avg_time

        ax2.clear()
        ax2.set_title("Smoothed Signal (Breathing + Stress)")

        ax2.plot(x_vals, smooth_data)

        # NORMAL (green)
        ax2.scatter(normal_peaks,
                    [smooth_data[i] for i in normal_peaks],
                    color='green', marker='o', label='Normal')

        # STRESS (red)
        ax2.scatter(stress_peaks,
                    [smooth_data[i] for i in stress_peaks],
                    color='red', marker='o', label='Stress')

        # INHALE
        ax2.scatter(inhale_idx,
                    [smooth_data[i] for i in inhale_idx],
                    marker='x', label='Inhale')

        ax2.set_xlim(0, window_size)
        ax2.set_ylim(np.min(smooth_data)-1, np.max(smooth_data)+1)

        ax2.legend()

        # BPM text
        ax2.text(0.02, 0.95, f"BPM: {bpm:.2f}",
                 transform=ax2.transAxes,
                 fontsize=12,
                 verticalalignment='top')

        plt.tight_layout()
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
timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")

df = pd.DataFrame({
    "Frame": frame_ids,
    "Intensity": intensity_values
})

csv_name = os.path.join(save_folder, f"breathing_signal_{timestamp}.csv")
df.to_csv(csv_name, index=False)

print("✅ Saved:", csv_name)