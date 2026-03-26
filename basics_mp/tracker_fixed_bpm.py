import cv2
import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
import datetime
import os
from scipy.signal import find_peaks   # 🔥 NEW

# -----------------------------
# SETTINGS
# -----------------------------
# video_path = r"D:\Lie Detection Data HTI\Lie_detection_ex2\Thermal_lie_detection_ex2\grey_manual\krishna_grey_manual1.wmv"
vid_path = r"D:\Lie Detection Data HTI\Lie_detection_ex2\Thermal_lie_detection_ex2\grey_manual\shivam_grey_manual.wmv"

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
def moving_average(signal, k=11):   # 🔥 increased smoothing
    return np.convolve(signal, np.ones(k)/k, mode='same')

def detect_breathing(signal, fps):
    # Minimum distance between breaths (frames)
    min_distance = int(fps * 1.5)

    # Detect exhale peaks
    peaks, _ = find_peaks(signal,
                          distance=min_distance,
                          prominence=0.5)

    # Detect inhale valleys
    valleys, _ = find_peaks(-signal,
                            distance=min_distance,
                            prominence=0.5)

    return valleys, peaks

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

ax2.set_title("Smoothed Signal")

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

            # Simple inhale/exhale label
            if len(intensity_values) > 5:
                if intensity_values[-1] > intensity_values[-2]:
                    phase = "Exhale"
                else:
                    phase = "Inhale"

                cv2.putText(frame, phase,
                            (x, y+h+25),
                            cv2.FONT_HERSHEY_SIMPLEX,
                            0.7, (255,255,0), 2)

            cv2.putText(frame, f"{mean_intensity:.2f}",
                        (x, y-10),
                        cv2.FONT_HERSHEY_SIMPLEX,
                        0.6, (0,255,0), 2)

    else:
        cv2.putText(frame, "Tracking Lost - Press R",
                    (30,50),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    0.7, (0,0,255), 2)

    cv2.imshow("Tracking ROI", frame)

    key = cv2.waitKey(30) & 0xFF

    if key == ord('r'):
        bbox = cv2.selectROI("Reselect ROI", frame, False)
        cv2.destroyWindow("Reselect ROI")
        tracker = create_tracker()
        tracker.init(frame, bbox)

    elif key == 27:
        break

    # -----------------------------
    # LIVE GRAPH
    # -----------------------------
    if len(intensity_values) > 20:

        data = intensity_values[-window_size:]
        x_vals = np.arange(len(data))

        # RAW
        line_raw.set_xdata(x_vals)
        line_raw.set_ydata(data)
        ax1.set_xlim(0, window_size)
        ax1.set_ylim(np.min(data)-1, np.max(data)+1)

        # SMOOTH
        smooth_data = moving_average(data)

        inhale_idx, exhale_idx = detect_breathing(smooth_data, fps)

        ax2.clear()
        ax2.set_title("Smoothed Signal")

        ax2.plot(x_vals, smooth_data)

        # Peaks (Exhale)
        ax2.scatter(exhale_idx,
                    [smooth_data[i] for i in exhale_idx],
                    color='red', marker='o')

        # Valleys (Inhale)
        ax2.scatter(inhale_idx,
                    [smooth_data[i] for i in inhale_idx],
                    color='blue', marker='x')

        ax2.set_xlim(0, window_size)
        ax2.set_ylim(np.min(smooth_data)-1, np.max(smooth_data)+1)

        plt.tight_layout()
        plt.draw()
        plt.pause(0.01)

    frame_count += 1

# -----------------------------
# FINAL BPM CALCULATION
# -----------------------------
final_bpm = 0

if len(intensity_values) > 20:
    full_signal = moving_average(intensity_values)

    inhale_idx, exhale_idx = detect_breathing(full_signal, fps)

    print("Detected breaths:", len(exhale_idx))  # debug

    if len(exhale_idx) > 1:
        peak_intervals = np.diff(exhale_idx) / fps
        avg_time = np.mean(peak_intervals)

        if avg_time > 0:
            final_bpm = 60 / avg_time

print(f"\n✅ Final Breathing Rate: {final_bpm:.2f} BPM")

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
    "Intensity": intensity_values,
    "Final_BPM": final_bpm
})

csv_name = os.path.join(save_folder, f"breathing_signal_{timestamp}.csv")
excel_name = os.path.join(save_folder, f"breathing_signal_{timestamp}.xlsx")

df.to_csv(csv_name, index=False)
df.to_excel(excel_name, index=False)

pixel_df = pd.DataFrame(all_pixel_data)
pixel_csv_name = os.path.join(save_folder, f"roi_pixels_{timestamp}.csv")
pixel_df.to_csv(pixel_csv_name, index=False)

print("\n✅ Files saved successfully!")
print(csv_name)
print(excel_name)
print(pixel_csv_name)