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

# # 👉 PUT YOUR FOLDER PATH HERE
# save_folder = r"basics_mp\output_files"

# window_size = 200

# # -----------------------------
# # CREATE SAVE FOLDER
# # -----------------------------
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
# # SMOOTHING FUNCTION
# # -----------------------------
# def moving_average(signal, k=7):
#     return np.convolve(signal, np.ones(k)/k, mode='same')

# # -----------------------------
# # PEAK / VALLEY DETECTION
# # -----------------------------
# def detect_breathing(signal):
#     inhale_idx = []
#     exhale_idx = []

#     for i in range(1, len(signal)-1):
#         # Peak → Exhale
#         if signal[i] > signal[i-1] and signal[i] > signal[i+1]:
#             exhale_idx.append(i)

#         # Valley → Inhale
#         if signal[i] < signal[i-1] and signal[i] < signal[i+1]:
#             inhale_idx.append(i)

#     return inhale_idx, exhale_idx

# # -----------------------------
# # FIRST FRAME → SELECT ROI
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
# # -----------------------------
# # GRAPH SETUP (2 GRAPHS)
# # -----------------------------
# plt.ion()
# fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(8, 6))

# # Raw signal
# line_raw, = ax1.plot([], [])
# ax1.set_title("Raw Intensity Signal")
# ax1.set_xlabel("Frame")
# ax1.set_ylabel("Intensity")

# # Smoothed signal
# line_smooth, = ax2.plot([], [])
# ax2.set_title("Smoothed Breathing Signal (Inhale/Exhale)")
# ax2.set_xlabel("Frame")
# ax2.set_ylabel("Intensity")
# # -----------------------------
# # LOOP
# # -----------------------------
# frame_count = 0

# while True:
#     ret, frame = cap.read()
#     if not ret:
#         break

#     success = False

#     # -----------------------------
#     # TRACKING
#     # -----------------------------
#     if tracker_initialized:
#         success, bbox = tracker.update(frame)

#     # -----------------------------
#     # TRACK LOST
#     # -----------------------------
#     if not success:
#         cv2.putText(frame, "Tracking Lost - Press R",
#                     (30,50), cv2.FONT_HERSHEY_SIMPLEX,
#                     0.7, (0,0,255), 2)

#     else:
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

#             pixels = gray.flatten()
#             all_pixel_data.append(pixels)

#             # -----------------------------
#             # INHALE / EXHALE LABEL (LIVE)
#             # -----------------------------
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
#                         (x, y-10), cv2.FONT_HERSHEY_SIMPLEX,
#                         0.6, (0,255,0), 2)

#     # -----------------------------
#     # DISPLAY
#     # -----------------------------
#     cv2.imshow("Tracking ROI", frame)

#     key = cv2.waitKey(100) & 0xFF

#     # -----------------------------
#     # RESELECT ROI
#     # -----------------------------
#     if key == ord('r'):
#         bbox = cv2.selectROI("Reselect ROI", frame, False)
#         cv2.destroyWindow("Reselect ROI")

#         tracker = create_tracker()
#         tracker.init(frame, bbox)
#         tracker_initialized = True

#     elif key == 27:
#         break

#     # -----------------------------
#     # LIVE GRAPH
#     # -----------------------------
#    # -----------------------------
# # LIVE GRAPH (2 PLOTS)
# # -----------------------------
# if len(intensity_values) > 20:

#     data = intensity_values[-window_size:]
#     x_vals = np.arange(len(data))

#     # -----------------------------
#     # GRAPH 1 → RAW SIGNAL
#     # -----------------------------
#     line_raw.set_xdata(x_vals)
#     line_raw.set_ydata(data)

#     ax1.set_xlim(0, window_size)

#     y_min = np.min(data)
#     y_max = np.max(data)
#     ax1.set_ylim(y_min - 1, y_max + 1)

#     # -----------------------------
#     # GRAPH 2 → SMOOTHED SIGNAL
#     # -----------------------------
#     smooth_data = moving_average(data)

#     inhale_idx, exhale_idx = detect_breathing(smooth_data)

#     line_smooth.set_xdata(x_vals)
#     line_smooth.set_ydata(smooth_data)

#     ax2.set_xlim(0, window_size)

#     y_min2 = np.min(smooth_data)
#     y_max2 = np.max(smooth_data)
#     ax2.set_ylim(y_min2 - 1, y_max2 + 1)

#     # 🔴 Exhale (peaks)
#     ax2.scatter(exhale_idx,
#                 [smooth_data[i] for i in exhale_idx],
#                 marker='o')

#     # 🔵 Inhale (valleys)
#     ax2.scatter(inhale_idx,
#                 [smooth_data[i] for i in inhale_idx],
#                 marker='x')

#     plt.tight_layout()
#     plt.draw()
#     plt.pause(0.01)

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

# csv_name = os.path.join(save_folder, f"breathing_signal_{timestamp}.csv")
# excel_name = os.path.join(save_folder, f"breathing_signal_{timestamp}.xlsx")

# df.to_csv(csv_name, index=False)
# df.to_excel(excel_name, index=False)

# pixel_array = np.array(all_pixel_data)
# pixel_df = pd.DataFrame(pixel_array)

# pixel_csv_name = os.path.join(save_folder, f"roi_pixels_{timestamp}.csv")
# pixel_df.to_csv(pixel_csv_name, index=False)

# print("✅ Files saved:")
# print(csv_name)
# print(excel_name)
# print(pixel_csv_name)




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

# 👉 PUT YOUR OUTPUT FOLDER HERE
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
tracker_initialized = False

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
tracker_initialized = True

# -----------------------------
# GRAPH SETUP
# -----------------------------
plt.ion()
fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(8, 6))

line_raw, = ax1.plot([], [])
line_smooth, = ax2.plot([], [])

ax1.set_title("Raw Intensity Signal")
ax2.set_title("Smoothed Signal (Inhale/Exhale)")

plt.show(block=False)

# -----------------------------
# LOOP
# -----------------------------
frame_count = 0

while True:
    ret, frame = cap.read()
    if not ret:
        break

    success = False

    # TRACKING
    if tracker_initialized:
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

            pixels = gray.flatten()
            all_pixel_data.append(pixels)

            # -----------------------------
            # INHALE / EXHALE LABEL
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

            cv2.putText(frame, f"{mean_intensity:.2f}",
                        (x, y-10),
                        cv2.FONT_HERSHEY_SIMPLEX,
                        0.6, (0,255,0), 2)

    else:
        cv2.putText(frame, "Tracking Lost - Press R",
                    (30,50),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    0.7, (0,0,255), 2)

    # DISPLAY VIDEO
    cv2.imshow("Tracking ROI", frame)

    key = cv2.waitKey(100) & 0xFF

    if key == ord('r'):
        bbox = cv2.selectROI("Reselect ROI", frame, False)
        cv2.destroyWindow("Reselect ROI")

        tracker = create_tracker()
        tracker.init(frame, bbox)

    elif key == 27:
        break

    # -----------------------------
    # LIVE GRAPH (FIXED ✅)
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

        ax2.clear()
        ax2.set_title("Smoothed Signal (Inhale/Exhale)")
        ax2.set_xlabel("Frame")
        ax2.set_ylabel("Intensity")

        ax2.plot(x_vals, smooth_data)

        ax2.scatter(exhale_idx,
                    [smooth_data[i] for i in exhale_idx],
                    marker='o')

        ax2.scatter(inhale_idx,
                    [smooth_data[i] for i in inhale_idx],
                    marker='x')

        ax2.set_xlim(0, window_size)
        ax2.set_ylim(np.min(smooth_data)-1, np.max(smooth_data)+1)

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
# -----------------------------qqqqqqq
timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")

df = pd.DataFrame({
    "Frame": frame_ids,
    "Intensity": intensity_values
})

csv_name = os.path.join(save_folder, f"breathing_signal_{timestamp}.csv")
excel_name = os.path.join(save_folder, f"breathing_signal_{timestamp}.xlsx")

df.to_csv(csv_name, index=False)
df.to_excel(excel_name, index=False)

pixel_array = np.array(all_pixel_data)
pixel_df = pd.DataFrame(pixel_array)

pixel_csv_name = os.path.join(save_folder, f"roi_pixels_{timestamp}.csv")
pixel_df.to_csv(pixel_csv_name, index=False)

print("✅ Files saved:")
print(csv_name)
print(excel_name)
print(pixel_csv_name)