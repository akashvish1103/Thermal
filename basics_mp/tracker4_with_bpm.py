# import cv2
# import numpy as np
# import matplotlib.pyplot as plt
# import pandas as pd
# import datetime
# import os

# # -----------------------------
# # SETTINGS
# # -----------------------------
# video_path = r"D:\Lie Detection Data HTI\Lie_detection_ex2\Thermal_lie_detection_ex2\grey_manual\krishna_grey_manual1.wmv"
# save_folder = r"basics_mp\output_files"
# window_size = 200

# os.makedirs(save_folder, exist_ok=True)

# # -----------------------------
# # INIT
# # -----------------------------
# cap = cv2.VideoCapture(video_path)

# def create_tracker():
#     try:
#         return cv2.TrackerCSRT_create()
#     except:
#         return cv2.legacy.TrackerCSRT_create()

# tracker = create_tracker()
# tracker_initialized = False

# intensity_values = []
# frame_ids = []
# all_pixel_data = []

# # -----------------------------
# # FUNCTIONS
# # -----------------------------
# def moving_average(signal, k=7):
#     return np.convolve(signal, np.ones(k)/k, mode='same')

# def detect_breathing(signal):
#     inhale_idx = []
#     exhale_idx = []

#     for i in range(1, len(signal)-1):
#         if signal[i] > signal[i-1] and signal[i] > signal[i+1]:
#             exhale_idx.append(i)

#         if signal[i] < signal[i-1] and signal[i] < signal[i+1]:
#             inhale_idx.append(i)

#     return inhale_idx, exhale_idx

# # -----------------------------
# # SELECT ROI
# # -----------------------------
# ret, frame = cap.read()
# if not ret:
#     print("Error reading video")
#     exit()

# bbox = cv2.selectROI("Select ROI", frame, False)
# cv2.destroyWindow("Select ROI")

# tracker.init(frame, bbox)
# tracker_initialized = True

# # -----------------------------
# # GRAPH SETUP
# # -----------------------------
# plt.ion()
# fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(8, 6))

# line_raw, = ax1.plot([], [])
# line_smooth, = ax2.plot([], [])

# ax1.set_title("Raw Signal")
# ax2.set_title("Smoothed Signal")

# plt.show(block=False)

# # -----------------------------
# # LOOP
# # -----------------------------
# frame_count = 0
# fps = 10  # because waitKey(100)

# while True:
#     ret, frame = cap.read()
#     if not ret:
#         break

#     success = False

#     if tracker_initialized:
#         success, bbox = tracker.update(frame)

#     if success:
#         x, y, w, h = map(int, bbox)
#         x = max(0, x)
#         y = max(0, y)

#         cv2.rectangle(frame, (x, y), (x+w, y+h), (0,255,0), 2)

#         roi = frame[y:y+h, x:x+w]

#         if roi.size != 0:
#             gray = cv2.cvtColor(roi, cv2.COLOR_BGR2GRAY)

#             mean_intensity = np.mean(gray)
#             intensity_values.append(mean_intensity)
#             frame_ids.append(frame_count)

#             all_pixel_data.append(gray.flatten())

#             # Inhale / Exhale (simple)
#             if len(intensity_values) > 5:
#                 if intensity_values[-1] > intensity_values[-2]:
#                     phase = "Exhale"
#                 else:
#                     phase = "Inhale"

#                 cv2.putText(frame, phase,
#                             (x, y+h+25),
#                             cv2.FONT_HERSHEY_SIMPLEX,
#                             0.7, (255,255,0), 2)

#             cv2.putText(frame, f"{mean_intensity:.2f}",
#                         (x, y-10),
#                         cv2.FONT_HERSHEY_SIMPLEX,
#                         0.6, (0,255,0), 2)

#     else:
#         cv2.putText(frame, "Tracking Lost - Press R",
#                     (30,50),
#                     cv2.FONT_HERSHEY_SIMPLEX,
#                     0.7, (0,0,255), 2)

#     # -----------------------------
#     # LIVE GRAPH + BPM
#     # -----------------------------
#     if len(intensity_values) > 20:

#         data = intensity_values[-window_size:]
#         x_vals = np.arange(len(data))

#         # RAW
#         line_raw.set_xdata(x_vals)
#         line_raw.set_ydata(data)
#         ax1.set_xlim(0, window_size)
#         ax1.set_ylim(np.min(data)-1, np.max(data)+1)

#         # SMOOTH
#         smooth_data = moving_average(data)
#         inhale_idx, exhale_idx = detect_breathing(smooth_data)

#         ax2.clear()
#         ax2.plot(x_vals, smooth_data)

#         ax2.scatter(exhale_idx,
#                     [smooth_data[i] for i in exhale_idx],
#                     marker='o')

#         ax2.scatter(inhale_idx,
#                     [smooth_data[i] for i in inhale_idx],
#                     marker='x')

#         ax2.set_xlim(0, window_size)
#         ax2.set_ylim(np.min(smooth_data)-1, np.max(smooth_data)+1)

#         # -----------------------------
#         # BPM CALCULATION (BEST METHOD)
#         # -----------------------------
#         bpm = 0

#         if len(exhale_idx) > 1:
#             intervals = np.diff(exhale_idx)  # frames between breaths
#             avg_interval = np.mean(intervals)

#             breathing_rate_hz = fps / avg_interval
#             bpm = breathing_rate_hz * 60

#         # DISPLAY BPM
#         cv2.putText(frame, f"BPM: {bpm:.2f}",
#                     (30, 80),
#                     cv2.FONT_HERSHEY_SIMPLEX,
#                     0.8, (0,255,255), 2)

#         print(f"BPM: {bpm:.2f}")

#         plt.tight_layout()
#         plt.draw()
#         plt.pause(0.01)

#     # -----------------------------
#     # DISPLAY
#     # -----------------------------
#     cv2.imshow("Tracking ROI", frame)

#     key = cv2.waitKey(100) & 0xFF

#     if key == ord('r'):
#         bbox = cv2.selectROI("Reselect ROI", frame, False)
#         cv2.destroyWindow("Reselect ROI")

#         tracker = create_tracker()
#         tracker.init(frame, bbox)

#     elif key == 27:
#         break

#     frame_count += 1

# # -----------------------------
# # CLEANUP
# # -----------------------------
# cap.release()
# cv2.destroyAllWindows()
# plt.ioff()
# plt.show()

# # -----------------------------
# # SAVE DATA
# # -----------------------------
# timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")

# df = pd.DataFrame({
#     "Frame": frame_ids,
#     "Intensity": intensity_values
# })

# df.to_csv(os.path.join(save_folder, f"signal_{timestamp}.csv"), index=False)

# print("✅ Done & Saved")

#############################################################################

# import cv2
# import numpy as np
# import matplotlib.pyplot as plt
# import pandas as pd
# import datetime
# import os

# # -----------------------------
# # SETTINGS
# # -----------------------------
# video_path = r"D:\Lie Detection Data HTI\Lie_detection_ex2\Thermal_lie_detection_ex2\grey_manual\krishna_grey_manual1.wmv"
# save_folder = r"basics_mp\output_files"
# window_size = 200

# os.makedirs(save_folder, exist_ok=True)

# # -----------------------------
# # INIT
# # -----------------------------
# cap = cv2.VideoCapture(video_path)

# def create_tracker():
#     try:
#         return cv2.TrackerCSRT_create()
#     except:
#         return cv2.legacy.TrackerCSRT_create()

# tracker = create_tracker()

# intensity_values = []
# frame_ids = []

# # -----------------------------
# # FUNCTIONS
# # -----------------------------
# def moving_average(signal, k=15):  # stronger smoothing
#     return np.convolve(signal, np.ones(k)/k, mode='same')


# def detect_breathing(signal, fps):
#     inhale_idx = []
#     exhale_idx = []

#     min_distance = int(1.5 * fps)   # minimum gap (physiological)
#     threshold = np.std(signal) * 0.5  # amplitude filter

#     last_peak = -min_distance

#     for i in range(1, len(signal)-1):

#         # EXHALE (PEAK)
#         if signal[i] > signal[i-1] and signal[i] > signal[i+1]:

#             # amplitude check
#             if (signal[i] - np.mean(signal)) > threshold:

#                 # distance check
#                 if (i - last_peak) > min_distance:
#                     exhale_idx.append(i)
#                     last_peak = i

#         # INHALE (VALLEY)
#         if signal[i] < signal[i-1] and signal[i] < signal[i+1]:
#             inhale_idx.append(i)

#     return inhale_idx, exhale_idx


# def calculate_bpm(exhale_idx, fps):
#     if len(exhale_idx) > 1:
#         intervals = np.diff(exhale_idx)
#         avg_interval = np.mean(intervals)

#         breathing_rate_hz = fps / avg_interval
#         return breathing_rate_hz * 60

#     return 0


# # -----------------------------
# # SELECT ROI
# # -----------------------------
# ret, frame = cap.read()
# if not ret:
#     print("Error reading video")
#     exit()

# bbox = cv2.selectROI("Select ROI", frame, False)
# cv2.destroyWindow("Select ROI")

# tracker.init(frame, bbox)

# # -----------------------------
# # GRAPH SETUP
# # -----------------------------
# plt.ion()
# fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(8, 6))

# # -----------------------------
# # FPS (IMPORTANT)
# # -----------------------------
# fps = cap.get(cv2.CAP_PROP_FPS)
# if fps == 0:
#     fps = 10  # fallback

# print("Using FPS:", fps)

# # -----------------------------
# # LOOP
# # -----------------------------
# frame_count = 0

# while True:
#     ret, frame = cap.read()
#     if not ret:
#         break

#     success, bbox = tracker.update(frame)

#     if success:
#         x, y, w, h = map(int, bbox)
#         x, y = max(0, x), max(0, y)

#         cv2.rectangle(frame, (x, y), (x+w, y+h), (0,255,0), 2)

#         roi = frame[y:y+h, x:x+w]

#         if roi.size != 0:
#             gray = cv2.cvtColor(roi, cv2.COLOR_BGR2GRAY)

#             mean_intensity = np.mean(gray)
#             intensity_values.append(mean_intensity)
#             frame_ids.append(frame_count)

#             cv2.putText(frame, f"{mean_intensity:.2f}",
#                         (x, y-10),
#                         cv2.FONT_HERSHEY_SIMPLEX,
#                         0.6, (0,255,0), 2)

#     else:
#         cv2.putText(frame, "Tracking Lost",
#                     (30,50),
#                     cv2.FONT_HERSHEY_SIMPLEX,
#                     0.7, (0,0,255), 2)

#     # -----------------------------
#     # SIGNAL PROCESSING
#     # -----------------------------
#     if len(intensity_values) > 30:

#         data = intensity_values[-window_size:]
#         x_vals = np.arange(len(data))

#         smooth_data = moving_average(data)

#         inhale_idx, exhale_idx = detect_breathing(smooth_data, fps)

#         bpm = calculate_bpm(exhale_idx, fps)

#         # -----------------------------
#         # DISPLAY BPM
#         # -----------------------------
#         cv2.putText(frame, f"BPM: {bpm:.2f}",
#                     (30, 80),
#                     cv2.FONT_HERSHEY_SIMPLEX,
#                     0.9, (0,255,255), 2)

#         # -----------------------------
#         # GRAPH
#         # -----------------------------
#         ax1.clear()
#         ax2.clear()

#         ax1.plot(x_vals, data)
#         ax1.set_title("Raw Signal")

#         ax2.plot(x_vals, smooth_data)
#         ax2.scatter(exhale_idx,
#                     [smooth_data[i] for i in exhale_idx],
#                     marker='o')
#         ax2.scatter(inhale_idx,
#                     [smooth_data[i] for i in inhale_idx],
#                     marker='x')

#         ax2.set_title("Filtered Breathing Signal")

#         plt.tight_layout()
#         plt.draw()
#         plt.pause(0.01)

#     # -----------------------------
#     # SHOW VIDEO
#     # -----------------------------
#     cv2.imshow("Breathing Tracker", frame)

#     key = cv2.waitKey(1) & 0xFF
#     if key == 27:
#         break

#     frame_count += 1

# # -----------------------------
# # CLEANUP
# # -----------------------------
# cap.release()
# cv2.destroyAllWindows()
# plt.ioff()
# plt.show()

# # -----------------------------
# # SAVE DATA
# # -----------------------------
# timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")

# df = pd.DataFrame({
#     "Frame": frame_ids,
#     "Intensity": intensity_values
# })

# df.to_csv(os.path.join(save_folder, f"breathing_signal_{timestamp}.csv"), index=False)

# print("✅ DONE — BPM is now accurate & stable")

#################################################################################################

import cv2
import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
import datetime
import os

# -----------------------------
# SETTINGS
# -----------------------------
# video_path = r"D:\Lie Detection Data HTI\Lie_detection_ex2\Thermal_lie_detection_ex2\grey_manual\krishna_grey_manual1.wmv"
video_path = r"C:\Users\Akash Vishwakarma\Downloads\kriahna_grey_clip.mp4"
save_folder = r"basics_mp\output_files"
window_size = 200

os.makedirs(save_folder, exist_ok=True)

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

intensity_values = []
frame_ids = []

# -----------------------------
# FUNCTIONS
# -----------------------------
def moving_average(signal, k=15):
    return np.convolve(signal, np.ones(k)/k, mode='same')


def detect_breathing(signal, fps):
    inhale_idx = []
    exhale_idx = []

    min_distance = int(1.5 * fps)

    mean_val = np.mean(signal)
    std_val = np.std(signal)

    amplitude_threshold = std_val * 0.3  # 🔥 key filter

    last_peak = -min_distance
    last_valley = None

    for i in range(1, len(signal)-1):

        # -----------------------------
        # VALLEY (INHALE)
        # -----------------------------
        if signal[i] < signal[i-1] and signal[i] < signal[i+1]:
            last_valley = i
            inhale_idx.append(i)

        # -----------------------------
        # PEAK (EXHALE)
        # -----------------------------
        if signal[i] > signal[i-1] and signal[i] > signal[i+1]:

            if last_valley is not None:

                amplitude = signal[i] - signal[last_valley]

                # ✅ ONLY COUNT REAL BREATH
                if amplitude > amplitude_threshold:
                    if (i - last_peak) > min_distance:
                        exhale_idx.append(i)
                        last_peak = i

    return inhale_idx, exhale_idx


def calculate_bpm(exhale_idx, fps):
    if len(exhale_idx) > 1:
        intervals = np.diff(exhale_idx)
        avg_interval = np.mean(intervals)

        breathing_rate_hz = fps / avg_interval
        return breathing_rate_hz * 60

    return 0


# -----------------------------
# SELECT ROI
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

# -----------------------------
# FPS
# -----------------------------
fps = cap.get(cv2.CAP_PROP_FPS)
if fps == 0:
    fps = 10

print("FPS:", fps)

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
        x, y = max(0, x), max(0, y)

        cv2.rectangle(frame, (x, y), (x+w, y+h), (0,255,0), 2)

        roi = frame[y:y+h, x:x+w]

        if roi.size != 0:
            gray = cv2.cvtColor(roi, cv2.COLOR_BGR2GRAY)

            mean_intensity = np.mean(gray)
            intensity_values.append(mean_intensity)
            frame_ids.append(frame_count)

            cv2.putText(frame, f"{mean_intensity:.2f}",
                        (x, y-10),
                        cv2.FONT_HERSHEY_SIMPLEX,
                        0.6, (0,255,0), 2)

    else:
        cv2.putText(frame, "Tracking Lost",
                    (30,50),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    0.7, (0,0,255), 2)

    # -----------------------------
    # SIGNAL PROCESSING
    # -----------------------------
    if len(intensity_values) > 30:

        data = intensity_values[-window_size:]
        x_vals = np.arange(len(data))

        smooth_data = moving_average(data)

        inhale_idx, exhale_idx = detect_breathing(smooth_data, fps)

        bpm = calculate_bpm(exhale_idx, fps)

        # -----------------------------
        # DISPLAY BPM
        # -----------------------------
        cv2.putText(frame, f"BPM: {bpm:.2f}",
                    (30, 80),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    0.9, (0,255,255), 2)

        # -----------------------------
        # GRAPH
        # -----------------------------
        ax1.clear()
        ax2.clear()

        ax1.plot(x_vals, data)
        ax1.set_title("Raw Signal")

        ax2.plot(x_vals, smooth_data)

        # Exhale (valid breaths)
        ax2.scatter(exhale_idx,
                    [smooth_data[i] for i in exhale_idx],
                    marker='o')

        # Inhale
        ax2.scatter(inhale_idx,
                    [smooth_data[i] for i in inhale_idx],
                    marker='x')

        ax2.set_title("Breathing Signal (Amplitude Filtered)")

        plt.tight_layout()
        plt.draw()
        plt.pause(0.01)

    # -----------------------------
    # DISPLAY
    # -----------------------------
    cv2.imshow("Breathing Tracker", frame)

    key = cv2.waitKey(1) & 0xFF
    if key == 27:
        break

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

df.to_csv(os.path.join(save_folder, f"breathing_signal_{timestamp}.csv"), index=False)

print("✅ DONE — Only real breaths are counted now")