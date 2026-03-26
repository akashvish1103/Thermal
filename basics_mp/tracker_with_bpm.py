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
# video_path = r"D:\Lie Detection Data HTI\Lie_detection_ex2\Thermal_lie_detection_ex2\aditi_grey_manual.wmv"
# video_path = r"D:\akashvProfile-TESTO-recorded-InCDAC-Lab\thermal-data\girish-TESTO-gray.wmv"
# video_path = r"D:\Lie Detection Data HTI\Lie_detection_ex2\Thermal_lie_detection_ex2\krishna_grey_20-40.mpg"
video_path = r"D:\Lie Detection Data HTI\Lie_detection_ex2\Thermal_lie_detection_ex2\grey_manual\shivam_grey_manual.wmv"
# 👉 PUT YOUR FULL PATH HERE
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

# -----------------------------
# FIRST FRAME → ROI
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

ax2.set_title("Smoothed Signal (Inhale/Exhale)")

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

            # FIXED pixel saving
            all_pixel_data.append(gray.flatten())

            # -----------------------------
            # INHALE / EXHALE
            # -----------------------------
            if len(intensity_values) > 5:
                if intensity_values[-1] > intensity_values[-2]:
                    phase = "Exhale"
                else:
                    phase = "Inhale"

                cv2.putText(frame, phase,
                            (x, y+h+25),
                            cv2.FONT_HERSHEY_SIMPLEX,
                            0.7, (255,255,0), 2)

            # -----------------------------
            # BPM DISPLAY
            # -----------------------------
            cv2.putText(frame, f"BPM: {bpm:.2f}",
                        (x, y+h+50),
                        cv2.FONT_HERSHEY_SIMPLEX,
                        0.7, (0,255,255), 2)

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

    key = cv2.waitKey(10) & 0xFF

    if key == ord('r'):
        bbox = cv2.selectROI("Reselect ROI", frame, False)
        cv2.destroyWindow("Reselect ROI")
        tracker = create_tracker()
        tracker.init(frame, bbox)

    elif key == 27:
        break

    # -----------------------------
    # LIVE GRAPH + BPM
    # -----------------------------
    if len(intensity_values) > 20:

        data = intensity_values[-window_size:]
        x_vals = np.arange(len(data))

        # RAW GRAPH
        line_raw.set_xdata(x_vals)
        line_raw.set_ydata(data)
        ax1.set_xlim(0, window_size)
        ax1.set_ylim(np.min(data)-1, np.max(data)+1)

        # SMOOTH GRAPH
        smooth_data = moving_average(data)
        inhale_idx, exhale_idx = detect_breathing(smooth_data)

        # BPM calculation
        if len(exhale_idx) > 1:
            peak_intervals = np.diff(exhale_idx) / fps
            avg_time = np.mean(peak_intervals)
            if avg_time > 0:
                bpm = 60 / avg_time

        ax2.clear()
        ax2.set_title("Smoothed Signal (Inhale/Exhale)")
        ax2.plot(x_vals, smooth_data)

        ax2.scatter(exhale_idx,
                    [smooth_data[i] for i in exhale_idx],
                    marker='o')

        ax2.scatter(inhale_idx,
                    [smooth_data[i] for i in inhale_idx],
                    marker='x')

        ax2.set_xlim(0, window_size)
        ax2.set_ylim(np.min(smooth_data)-1, np.max(smooth_data)+1)

        # BPM text on graph
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
# SAVE DATA (FIXED ✅)
# -----------------------------
timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")

df = pd.DataFrame({
    "Frame": frame_ids,
    "Intensity": intensity_values
})

csv_name = os.path.join(save_folder, f"breathing_signal_{timestamp}.csv")
excel_name = os.path.join(save_folder, f"breathing_signal_{timestamp}.xlsx")

df.to_csv(csv_name, index=False)
df.to_excel(excel_name, index=False)

# FIXED pixel saving
pixel_df = pd.DataFrame(all_pixel_data)
pixel_csv_name = os.path.join(save_folder, f"roi_pixels_{timestamp}.csv")
pixel_df.to_csv(pixel_csv_name, index=False)

print("✅ Files saved successfully!")
print(csv_name)
print(excel_name)
print(pixel_csv_name)

#########################################################

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
# # video_path = r"C:\Users\Akash Vishwakarma\Downloads\kriahna_grey_clip.mp4"
# # video_path = r"D:\Lie Detection Data HTI\Lie_detection_ex2\Thermal_lie_detection_ex2\grey_manual\sneha_grey_manual.wmv"
# # video_path = r"D:\Lie Detection Data HTI\Lie_detection_ex2\Thermal_lie_detection_ex2\grey_manual\purva_grey_manual.wmv"
# # video_path = r"D:\Lie Detection Data HTI\Lie_detection_ex2\Thermal_lie_detection_ex2\grey_manual\pratham_iron_auto.wmv"

# save_folder = r"C:\Users\Akash Vishwakarma\Desktop\Thermal_Analysis\basics_mp\output_files"
# window_size = 200

# os.makedirs(save_folder, exist_ok=True)

# # -----------------------------
# # INIT
# # -----------------------------
# cap = cv2.VideoCapture(video_path)
# fps = cap.get(cv2.CAP_PROP_FPS)
# print("FPS:", fps)

# def create_tracker():
#     try:
#         return cv2.TrackerCSRT_create()
#     except:
#         return cv2.legacy.TrackerCSRT_create()

# tracker = create_tracker()

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
# # ROI SELECTION
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

# line_raw, = ax1.plot([], [])  
# ax1.set_title("Raw Intensity Signal")

# ax2.set_title("Smoothed Signal")

# plt.show(block=False)

# # -----------------------------
# # LOOP
# # -----------------------------
# frame_count = 0

# while True:
#     ret, frame = cap.read()
#     # print("FRAME shape", frame.shape)
#     # frame = cv2.resize(frame, (480, 800,3))
#     if not ret:
#         break

#     success, bbox = tracker.update(frame)

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

#             # Inhale / Exhale only
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

#     cv2.imshow("Tracking ROI", frame)

#     key = cv2.waitKey(30) & 0xFF

#     if key == ord('r'):
#         bbox = cv2.selectROI("Reselect ROI", frame, False)
#         cv2.destroyWindow("Reselect ROI")
#         tracker = create_tracker()
#         tracker.init(frame, bbox)

#     elif key == 27:
#         break

#     # -----------------------------
#     # LIVE GRAPH (NO BPM)
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
#         ax2.set_title("Smoothed Signal")

#         ax2.plot(x_vals, smooth_data)

#         ax2.scatter(exhale_idx,
#                     [smooth_data[i] for i in exhale_idx],
#                     marker='o')

#         ax2.scatter(inhale_idx,
#                     [smooth_data[i] for i in inhale_idx],
#                     marker='x')

#         ax2.set_xlim(0, window_size)
#         ax2.set_ylim(np.min(smooth_data)-1, np.max(smooth_data)+1)

#         plt.tight_layout()
#         plt.draw()
#         plt.pause(0.01)

#     frame_count += 1

# # -----------------------------
# # FINAL BPM CALCULATION
# # -----------------------------
# final_bpm = 0

# if len(intensity_values) > 20:
#     full_signal = moving_average(intensity_values)

#     inhale_idx, exhale_idx = detect_breathing(full_signal)

#     if len(exhale_idx) > 1:
#         peak_intervals = np.diff(exhale_idx) / fps
#         avg_time = np.mean(peak_intervals)

#         if avg_time > 0:
#             final_bpm = 60 / avg_time

# print(f"\n✅ Final Breathing Rate: {final_bpm:.2f} BPM")

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
#     "Intensity": intensity_values,
#     "Final_BPM": final_bpm
# })

# csv_name = os.path.join(save_folder, f"breathing_signal_{timestamp}.csv")
# excel_name = os.path.join(save_folder, f"breathing_signal_{timestamp}.xlsx")

# df.to_csv(csv_name, index=False)
# df.to_excel(excel_name, index=False)

# pixel_df = pd.DataFrame(all_pixel_data)
# pixel_csv_name = os.path.join(save_folder, f"roi_pixels_{timestamp}.csv")
# pixel_df.to_csv(pixel_csv_name, index=False)

# print("\n✅ Files saved successfully!")
# print(csv_name)
# print(excel_name)
# print(pixel_csv_name)

#########################################################################

# import cv2
# import numpy as np
# import matplotlib.pyplot as plt
# import pandas as pd
# import datetime
# import os
# from scipy.signal import find_peaks   # 🔥 NEW

# # -----------------------------
# # SETTINGS
# # -----------------------------
# video_path = r"D:\Lie Detection Data HTI\Lie_detection_ex2\Thermal_lie_detection_ex2\grey_manual\krishna_grey_manual1.wmv"

# save_folder = r"C:\Users\Akash Vishwakarma\Desktop\Thermal_Analysis\basics_mp\output_files"
# window_size = 200

# os.makedirs(save_folder, exist_ok=True)

# # -----------------------------
# # INIT
# # -----------------------------
# cap = cv2.VideoCapture(video_path)
# fps = cap.get(cv2.CAP_PROP_FPS)
# print("FPS:", fps)

# def create_tracker():
#     try:
#         return cv2.TrackerCSRT_create()
#     except:
#         return cv2.legacy.TrackerCSRT_create()

# tracker = create_tracker()

# intensity_values = []
# frame_ids = []
# all_pixel_data = []

# # -----------------------------
# # FUNCTIONS
# # -----------------------------
# def moving_average(signal, k=11):   # 🔥 increased smoothing
#     return np.convolve(signal, np.ones(k)/k, mode='same')

# def detect_breathing(signal, fps):
#     # Minimum distance between breaths (frames)
#     min_distance = int(fps * 1.5)

#     # Detect exhale peaks
#     peaks, _ = find_peaks(signal,
#                           distance=min_distance,
#                           prominence=0.5)

#     # Detect inhale valleys
#     valleys, _ = find_peaks(-signal,
#                             distance=min_distance,
#                             prominence=0.5)

#     return valleys, peaks

# # -----------------------------
# # ROI SELECTION
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
# fig, (ax1, ax2, ax3) = plt.subplots(3, 1, figsize=(8, 9))

# # Raw
# line_raw, = ax1.plot([], [])
# ax1.set_title("Raw Intensity Signal")

# # Moving Average ONLY
# line_smooth_only, = ax2.plot([], [])
# ax2.set_title("Moving Average (Smoothed Signal)")

# # Final with Peaks
# ax3.set_title("Smoothed + Breathing Peaks")

# plt.show(block=False)

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

#             # Simple inhale/exhale label
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

#     cv2.imshow("Tracking ROI", frame)

#     key = cv2.waitKey(30) & 0xFF

#     if key == ord('r'):
#         bbox = cv2.selectROI("Reselect ROI", frame, False)
#         cv2.destroyWindow("Reselect ROI")
#         tracker = create_tracker()
#         tracker.init(frame, bbox)

#     elif key == 27:
#         break

#     # -----------------------------
#     # LIVE GRAPH
#     # -----------------------------
#     if len(intensity_values) > 20:

#         data = intensity_values[-window_size:]
#         x_vals = np.arange(len(data))

#         # -----------------------------
#         # GRAPH 1 → RAW
#         # -----------------------------
#         line_raw.set_xdata(x_vals)
#         line_raw.set_ydata(data)

#         ax1.set_xlim(0, window_size)
#         ax1.set_ylim(np.min(data)-1, np.max(data)+1)

#         # -----------------------------
#         # GRAPH 2 → MOVING AVERAGE ONLY
#         # -----------------------------
#         smooth_data = moving_average(data)

#         line_smooth_only.set_xdata(x_vals)
#         line_smooth_only.set_ydata(smooth_data)

#         ax2.set_xlim(0, window_size)
#         ax2.set_ylim(np.min(smooth_data)-1, np.max(smooth_data)+1)

#         # -----------------------------
#         # GRAPH 3 → PEAK DETECTION
#         # -----------------------------
#         inhale_idx, exhale_idx = detect_breathing(smooth_data, fps)

#         ax3.clear()
#         ax3.set_title("Smoothed + Breathing Peaks")

#         ax3.plot(x_vals, smooth_data)

#         # Exhale (peaks)
#         ax3.scatter(exhale_idx,
#                     [smooth_data[i] for i in exhale_idx],
#                     color='red', marker='o', label='Exhale')

#         # Inhale (valleys)
#         ax3.scatter(inhale_idx,
#                     [smooth_data[i] for i in inhale_idx],
#                     color='blue', marker='x', label='Inhale')

#         ax3.set_xlim(0, window_size)
#         ax3.set_ylim(np.min(smooth_data)-1, np.max(smooth_data)+1)

#         ax3.legend()

#         plt.tight_layout()
#         plt.draw()
#         plt.pause(0.01)

# # -----------------------------
# # FINAL BPM CALCULATION
# # -----------------------------
# final_bpm = 0

# if len(intensity_values) > 20:
#     full_signal = moving_average(intensity_values)

#     inhale_idx, exhale_idx = detect_breathing(full_signal, fps)

#     print("Detected breaths:", len(exhale_idx))  # debug

#     if len(exhale_idx) > 1:
#         peak_intervals = np.diff(exhale_idx) / fps
#         avg_time = np.mean(peak_intervals)

#         if avg_time > 0:
#             final_bpm = 60 / avg_time

# print(f"\n✅ Final Breathing Rate: {final_bpm:.2f} BPM")

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
#     "Intensity": intensity_values,
#     "Final_BPM": final_bpm
# })

# csv_name = os.path.join(save_folder, f"breathing_signal_{timestamp}.csv")
# excel_name = os.path.join(save_folder, f"breathing_signal_{timestamp}.xlsx")

# df.to_csv(csv_name, index=False)
# df.to_excel(excel_name, index=False)

# pixel_df = pd.DataFrame(all_pixel_data)
# pixel_csv_name = os.path.join(save_folder, f"roi_pixels_{timestamp}.csv")
# pixel_df.to_csv(pixel_csv_name, index=False)

# print("\n✅ Files saved successfully!")
# print(csv_name)
# print(excel_name)
# print(pixel_csv_name)

################################################################

# import cv2
# import numpy as np
# import matplotlib.pyplot as plt
# import pandas as pd
# import datetime
# import os
# from scipy.signal import find_peaks

# # -----------------------------
# # SETTINGS
# # -----------------------------
# video_path = r"D:\Lie Detection Data HTI\Lie_detection_ex2\Thermal_lie_detection_ex2\grey_manual\krishna_grey_manual1.wmv"

# # 👉 CHANGE THIS PATH IF NEEDED
# save_folder = r"C:\Users\Akash Vishwakarma\Desktop\Thermal_Analysis\basics_mp\output_files"

# window_size = 200
# os.makedirs(save_folder, exist_ok=True)

# # -----------------------------
# # VIDEO INIT
# # -----------------------------
# cap = cv2.VideoCapture(video_path)
# fps = cap.get(cv2.CAP_PROP_FPS)
# print("FPS:", fps)

# # -----------------------------
# # TRACKER
# # -----------------------------
# def create_tracker():
#     try:
#         return cv2.TrackerCSRT_create()
#     except:
#         return cv2.legacy.TrackerCSRT_create()

# tracker = create_tracker()

# # -----------------------------
# # DATA STORAGE
# # -----------------------------
# intensity_values = []
# frame_ids = []
# all_pixel_data = []

# # -----------------------------
# # SIGNAL FUNCTIONS
# # -----------------------------
# def moving_average(signal, k=7):
#     return np.convolve(signal, np.ones(k)/k, mode='same')

# def strong_smoothing(signal):
#     # Apply smoothing twice for cleaner signal
#     return moving_average(moving_average(signal, k=11), k=11)

# def detect_breathing(signal, fps):
#     # Minimum distance between breaths (avoid fake peaks)
#     min_distance = int(fps * 1.5)

#     peaks, _ = find_peaks(signal,
#                           distance=min_distance,
#                           prominence=0.5)

#     valleys, _ = find_peaks(-signal,
#                             distance=min_distance,
#                             prominence=0.5)

#     return valleys, peaks

# # -----------------------------
# # ROI SELECTION
# # -----------------------------
# ret, frame = cap.read()
# if not ret:
#     print("Error reading video")
#     exit()

# bbox = cv2.selectROI("Select ROI", frame, False)
# cv2.destroyWindow("Select ROI")

# tracker.init(frame, bbox)

# # -----------------------------
# # GRAPH SETUP (3 GRAPHS)
# # -----------------------------
# plt.ion()
# fig, (ax1, ax2, ax3) = plt.subplots(3, 1, figsize=(8, 9))

# # Graph 1 → Raw
# line_raw, = ax1.plot([], [])
# ax1.set_title("Raw Intensity Signal")

# # Graph 2 → Code-2 style
# ax2.set_title("Smoothed Signal")

# # Graph 3 → Final Clean Signal
# ax3.set_title("Final Signal (Used for BPM)")

# plt.show(block=False)

# # -----------------------------
# # MAIN LOOP
# # -----------------------------
# frame_count = 0

# while True:
#     ret, frame = cap.read()
#     if not ret:
#         break

#     success, bbox = tracker.update(frame)

#     if success:
#         x, y, w, h = map(int, bbox)
#         x = max(0, x)
#         y = max(0, y)

#         cv2.rectangle(frame, (x, y), (x+w, y+h), (0,255,0), 2)

#         roi = frame[y:y+h, x:x+w]

#         if roi.size != 0:
#             gray = cv2.cvtColor(roi, cv2.COLOR_BGR2GRAY)

#             # Mean intensity → breathing signal
#             mean_intensity = np.mean(gray)

#             intensity_values.append(mean_intensity)
#             frame_ids.append(frame_count)

#             all_pixel_data.append(gray.flatten())

#             # Simple inhale/exhale (visual only)
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

#     cv2.imshow("Tracking ROI", frame)

#     key = cv2.waitKey(30) & 0xFF

#     if key == ord('r'):
#         bbox = cv2.selectROI("Reselect ROI", frame, False)
#         cv2.destroyWindow("Reselect ROI")
#         tracker = create_tracker()
#         tracker.init(frame, bbox)

#     elif key == 27:
#         break

#     # -----------------------------
#     # GRAPH UPDATE
#     # -----------------------------
#     if len(intensity_values) > 20:

#         data = intensity_values[-window_size:]
#         x_vals = np.arange(len(data))

#         # -----------------------------
#         # GRAPH 1 → RAW
#         # -----------------------------
#         line_raw.set_xdata(x_vals)
#         line_raw.set_ydata(data)
#         ax1.set_xlim(0, window_size)
#         ax1.set_ylim(np.min(data)-1, np.max(data)+1)

#         # -----------------------------
#         # GRAPH 2 → CODE-2 STYLE
#         # -----------------------------
#         smooth_data_1 = moving_average(data, k=7)

#         inhale_idx_1, exhale_idx_1 = detect_breathing(smooth_data_1, fps)

#         ax2.clear()
#         ax2.set_title("Smoothed Signal (Code-2 Style)")

#         ax2.plot(x_vals, smooth_data_1)

#         ax2.scatter(exhale_idx_1,
#                     [smooth_data_1[i] for i in exhale_idx_1],
#                     marker='o')

#         ax2.scatter(inhale_idx_1,
#                     [smooth_data_1[i] for i in inhale_idx_1],
#                     marker='x')

#         ax2.set_xlim(0, window_size)
#         ax2.set_ylim(np.min(smooth_data_1)-1, np.max(smooth_data_1)+1)

#         # -----------------------------
#         # GRAPH 3 → FINAL CLEAN SIGNAL
#         # -----------------------------
#         smooth_data_2 = strong_smoothing(data)

#         inhale_idx_2, exhale_idx_2 = detect_breathing(smooth_data_2, fps)

#         ax3.clear()
#         ax3.set_title("Final Signal (Used for BPM)")

#         ax3.plot(x_vals, smooth_data_2)

#         ax3.scatter(exhale_idx_2,
#                     [smooth_data_2[i] for i in exhale_idx_2],
#                     color='red', marker='o', label='Exhale')

#         ax3.scatter(inhale_idx_2,
#                     [smooth_data_2[i] for i in inhale_idx_2],
#                     color='blue', marker='x', label='Inhale')

#         ax3.set_xlim(0, window_size)
#         ax3.set_ylim(np.min(smooth_data_2)-1, np.max(smooth_data_2)+1)

#         ax3.legend()

#         plt.tight_layout()
#         plt.draw()
#         plt.pause(0.01)

#     frame_count += 1

# # -----------------------------
# # FINAL BPM CALCULATION
# # -----------------------------
# final_bpm = 0

# if len(intensity_values) > 20:
#     full_signal = strong_smoothing(intensity_values)

#     inhale_idx, exhale_idx = detect_breathing(full_signal, fps)

#     print("Detected breaths:", len(exhale_idx))

#     if len(exhale_idx) > 1:
#         peak_intervals = np.diff(exhale_idx) / fps
#         avg_time = np.mean(peak_intervals)

#         if avg_time > 0:
#             final_bpm = 60 / avg_time

# print(f"\n✅ Final Breathing Rate: {final_bpm:.2f} BPM")

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
#     "Intensity": intensity_values,
#     "Final_BPM": final_bpm
# })

# csv_name = os.path.join(save_folder, f"breathing_signal_{timestamp}.csv")
# excel_name = os.path.join(save_folder, f"breathing_signal_{timestamp}.xlsx")

# df.to_csv(csv_name, index=False)
# df.to_excel(excel_name, index=False)

# pixel_df = pd.DataFrame(all_pixel_data)
# pixel_csv_name = os.path.join(save_folder, f"roi_pixels_{timestamp}.csv")
# pixel_df.to_csv(pixel_csv_name, index=False)

# print("\n✅ Files saved successfully!")
# print(csv_name)
# print(excel_name)
# print(pixel_csv_name)