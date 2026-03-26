import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

# -----------------------------
# SETTINGS
# -----------------------------
csv_path = r"C:\Users\Akash Vishwakarma\Desktop\Thermal_Analysis\basics_mp\output_files\breathing_signal_20260323_141933.csv"   # 👈 change this
fps = 30                    # 👈 put your video FPS
smooth_k = 7

FAST_INTERVAL = 1.5         # sec
HIGH_BPM = 50               # threshold
WINDOW_SEC = 10             # for peak density

# -----------------------------
# LOAD DATA
# -----------------------------
df = pd.read_csv(csv_path)

signal = df["Intensity"].values
frames = df["Frame"].values

# -----------------------------
# SMOOTHING
# -----------------------------
def moving_average(signal, k=7):
    return np.convolve(signal, np.ones(k)/k, mode='same')

smooth_signal = moving_average(signal, smooth_k)

# -----------------------------
# PEAK DETECTION
# -----------------------------
def detect_breathing(signal):
    inhale_idx = []
    exhale_idx = []

    for i in range(1, len(signal)-1):
        if signal[i] > signal[i-1] and signal[i] > signal[i+1]:
            exhale_idx.append(i)
        if signal[i] < signal[i-1] and signal[i] < signal[i+1]:
            inhale_idx.append(i)

    return inhale_idx, exhale_idx

inhale_idx, exhale_idx = detect_breathing(smooth_signal)

# -----------------------------
# ANALYSIS
# -----------------------------
peak_intervals = np.diff(exhale_idx) / fps   # seconds

fast_events = []
irregular_flag = False
local_bpm_list = []
density_flags = []

for i in range(len(peak_intervals)):

    interval = peak_intervals[i]

    # -----------------------------
    # 1. FAST INTERVAL
    # -----------------------------
    if interval < FAST_INTERVAL:
        fast_events.append(exhale_idx[i])

# -----------------------------
# 2. LOCAL BPM (sliding)
# -----------------------------
window_size = 5

for i in range(len(exhale_idx)):
    window_peaks = exhale_idx[max(0, i-window_size):i+1]

    if len(window_peaks) > 1:
        intervals = np.diff(window_peaks) / fps
        local_bpm = 60 / np.mean(intervals)
        local_bpm_list.append((exhale_idx[i], local_bpm))

# -----------------------------
# 3. PEAK DENSITY
# -----------------------------
for i in range(len(signal)):
    window_start = i - int(WINDOW_SEC * fps)
    window_start = max(0, window_start)

    peaks_in_window = [p for p in exhale_idx if window_start <= p <= i]

    if len(peaks_in_window) > 1:
        duration = (i - window_start) / fps
        rate = len(peaks_in_window) / duration
        bpm_local = rate * 60

        if bpm_local > HIGH_BPM:
            density_flags.append(i)

# -----------------------------
# 4. IRREGULARITY
# -----------------------------
if len(peak_intervals) > 2:
    std_interval = np.std(peak_intervals)
    if std_interval > 0.5:
        irregular_flag = True

# -----------------------------
# GLOBAL BPM
# -----------------------------
if len(peak_intervals) > 0:
    avg_interval = np.mean(peak_intervals)
    global_bpm = 60 / avg_interval
else:
    global_bpm = 0

# -----------------------------
# FINAL STATE
# -----------------------------
state = "NORMAL"

if global_bpm > HIGH_BPM:
    state = "FAST BREATHING"

if len(fast_events) > 3:
    state += " + RAPID SPIKES"

if irregular_flag:
    state += " + IRREGULAR"

# -----------------------------
# PRINT RESULTS
# -----------------------------
print("Global BPM:", round(global_bpm, 2))
print("State:", state)

# -----------------------------
# PLOT
# -----------------------------
plt.figure(figsize=(12,6))

# Signal
plt.plot(smooth_signal, label="Smoothed Signal")

# Peaks
plt.scatter(exhale_idx,
            smooth_signal[exhale_idx],
            label="Exhale Peaks")

# Fast events
plt.scatter(fast_events,
            smooth_signal[fast_events],
            color='red',
            s=60,
            label="Fast Breathing")

# Density flags
plt.scatter(density_flags,
            smooth_signal[density_flags],
            color='orange',
            s=20,
            label="High Density")

plt.title(f"Breathing Analysis | BPM: {global_bpm:.2f} | {state}")
plt.legend()
plt.show()