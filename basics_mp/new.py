import cv2
import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
import datetime
import os
from scipy.signal import find_peaks

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

# -----------------------------
# TRACKER
# -----------------------------
def create_tracker():
    try:
        return cv2.TrackerCSRT_create()
    except:
        return cv2.legacy.TrackerCSRT_create()

tracker = create_tracker()

# -----------------------------
# DATA STORAGE
# -----------------------------
intensity_values = []
frame_ids = []
all_pixel_data = []

# -----------------------------
# FUNCTIONS
# -----------------------------
def moving_average(signal, k=7):
    return np.convolve(signal, np.ones(k)/k, mode='same')

def strong_smoothing(signal):
    return moving_average(moving_average(signal, 11), 11)

def detect_breathing(signal, fps):
    min_distance = int(fps * 1.5)

    peaks, _ = find_peaks(signal,
                          distance=min_distance,
                          prominence=0.5)

    valleys, _ = find_peaks(-signal,
                            distance=min_distance,
                            prominence=0.5)

    return valleys, peaks

# 🔥 Stress detection (fast breathing)
def detect_stress_regions(exhale_idx, fps, threshold=2.5):
    stress_points = []

    if len(exhale_idx) > 1:
        intervals = np.diff(exhale_idx) / fps

        for i, interval in enumerate(intervals):
            if interval < threshold:
                stress_points.append(exhale_idx[i+1])

    return stress_points

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
fig, (ax1, ax2, ax3) = plt.subplots(3, 1, figsize=(10, 10))

line_raw, = ax1.plot([], [])
ax1.set_title("Raw Signal")

ax2.set_title("Smoothed Signal (Code-2 Style)")
ax3.set_title("Final Signal (Used for BPM + Stress Detection)")

plt.show(block=False)

# -----------------------------
# LOOP
# -----------------------------
frame_count = 0

while True:
    ret, frame = cap.read()
    if not ret:
        break

    success, bbox = tracker.update(frame)

    if success:
        x, y, w, h = map(int, bbox)
        roi = frame[y:y+h, x:x+w]

        if roi.size != 0:
            gray = cv2.cvtColor(roi, cv2.COLOR_BGR2GRAY)

            mean_intensity = np.mean(gray)
            intensity_values.append(mean_intensity)
            frame_ids.append(frame_count)

            all_pixel_data.append(gray.flatten())

    cv2.imshow("Tracking ROI", frame)

    if cv2.waitKey(30) & 0xFF == 27:
        break

    # -----------------------------
    # GRAPH UPDATE
    # -----------------------------
    if len(intensity_values) > 20:

        data = intensity_values[-window_size:]
        frame_vals = np.arange(len(data))
        time_vals = frame_vals / fps

        # -----------------------------
        # GRAPH 1 → RAW
        # -----------------------------
        line_raw.set_xdata(time_vals)
        line_raw.set_ydata(data)

        ax1.set_xlim(time_vals[0], time_vals[-1])
        ax1.set_ylim(np.min(data)-1, np.max(data)+1)
        ax1.set_xlabel("Time (seconds)")

        # -----------------------------
        # GRAPH 2 → CODE-2 STYLE
        # -----------------------------
        smooth_data_1 = moving_average(data, 7)

        inhale_1, exhale_1 = detect_breathing(smooth_data_1, fps)

        ax2.clear()
        ax2.set_title("Smoothed Signal (Code-2 Style)")
        ax2.plot(time_vals, smooth_data_1)

        ax2.scatter(time_vals[exhale_1],
                    [smooth_data_1[i] for i in exhale_1],
                    marker='o')

        ax2.scatter(time_vals[inhale_1],
                    [smooth_data_1[i] for i in inhale_1],
                    marker='x')

        ax2.set_xlim(time_vals[0], time_vals[-1])
        ax2.set_ylim(np.min(smooth_data_1)-1, np.max(smooth_data_1)+1)
        ax2.set_xlabel("Time (seconds)")

        # -----------------------------
        # GRAPH 3 → FINAL + STRESS
        # -----------------------------
        smooth_data_2 = strong_smoothing(data)

        inhale_2, exhale_2 = detect_breathing(smooth_data_2, fps)

        stress_idx = detect_stress_regions(exhale_2, fps)

        ax3.clear()
        ax3.set_title("Final Signal (BPM + Stress)")

        ax3.plot(time_vals, smooth_data_2)

        # Normal breathing
        normal_idx = [i for i in exhale_2 if i not in stress_idx]

        ax3.scatter(time_vals[normal_idx],
                    [smooth_data_2[i] for i in normal_idx],
                    color='green', marker='o', label='Normal')

        # Stress breathing
        ax3.scatter(time_vals[stress_idx],
                    [smooth_data_2[i] for i in stress_idx],
                    color='red', marker='o', label='Stress')

        ax3.set_xlim(time_vals[0], time_vals[-1])
        ax3.set_ylim(np.min(smooth_data_2)-1, np.max(smooth_data_2)+1)

        ax3.set_xlabel("Time (seconds)")
        ax3.legend()

        plt.tight_layout()
        plt.draw()
        plt.pause(0.01)

    frame_count += 1

# -----------------------------
# FINAL BPM
# -----------------------------
final_bpm = 0

if len(intensity_values) > 20:
    full_signal = strong_smoothing(intensity_values)

    _, exhale_idx = detect_breathing(full_signal, fps)

    if len(exhale_idx) > 1:
        intervals = np.diff(exhale_idx) / fps
        avg_time = np.mean(intervals)

        if avg_time > 0:
            final_bpm = 60 / avg_time

print(f"\n✅ Final Breathing Rate: {final_bpm:.2f} BPM")

# -----------------------------
# SAVE FILES
# -----------------------------
timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")

time_values = np.arange(len(intensity_values)) / fps

df = pd.DataFrame({
    "Frame": frame_ids,
    "Time_sec": time_values,
    "Intensity": intensity_values,
    "Final_BPM": final_bpm
})

csv_name = os.path.join(save_folder, f"breathing_signal_{timestamp}.csv")
df.to_csv(csv_name, index=False)

print("✅ Saved:", csv_name)