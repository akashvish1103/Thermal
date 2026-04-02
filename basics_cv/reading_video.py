# import cv2

# # vid_path = r"D:\akashvProfile-TESTO-recorded-InCDAC-Lab\thermal-data\girish-demo.wmv"
# vid_path = r"D:\Lie Detection Data HTI\Lie_detection_ex2\Thermal_lie_detection_ex2\grey_manual\krishna_grey_manual1.wmv"

# cap = cv2.VideoCapture(vid_path)

# fps = cap.get(cv2.CAP_PROP_FPS)
# print("FPS:", fps)

# while True:
#     ret, frame = cap.read()

#     if not ret:
#         break

#     cv2.imshow("My Video Window", frame)

#     if cv2.waitKey(100) & 0xFF == ord('q'):
#         break

# cap.release()
# cv2.destroyAllWindows()

##################################################################################################
import cv2
import numpy as np

# -----------------------------
# VIDEO PATH
# -----------------------------
vid_path = r"D:\Lie Detection Data HTI\Lie_detection_ex2\Thermal_lie_detection_ex2\grey_manual\krishna_grey_manual1.wmv"

# -----------------------------
# LOAD VIDEO
# -----------------------------
cap = cv2.VideoCapture(vid_path)

if not cap.isOpened():
    print("Error: Cannot open video")
    exit()

# -----------------------------
# GET METADATA FPS (UNRELIABLE)
# -----------------------------
fps_meta = cap.get(cv2.CAP_PROP_FPS)
print("Metadata FPS:", fps_meta)

# -----------------------------
# COMPUTE ACTUAL FPS USING TIMESTAMPS
# -----------------------------
timestamps = []

while True:
    ret, frame = cap.read()
    if not ret:
        break
    
    t = cap.get(cv2.CAP_PROP_POS_MSEC)  # time in milliseconds
    timestamps.append(t)

# Convert to numpy
timestamps = np.array(timestamps)

# Compute intervals between frames
intervals = np.diff(timestamps)

# Remove zeros (sometimes occurs)
intervals = intervals[intervals > 0]

# Compute FPS
fps_actual = 1000 / np.mean(intervals)

print("Actual FPS (computed):", fps_actual)

# -----------------------------
# RESET VIDEO TO START
# -----------------------------
cap.set(cv2.CAP_PROP_POS_FRAMES, 0)

# -----------------------------
# PLAY VIDEO AT CORRECT SPEED
# -----------------------------
delay = int(1000 / fps_actual)

print("Playback delay (ms):", delay)

while True:
    ret, frame = cap.read()
    if not ret:
        break

    cv2.imshow("Thermal Video", frame)

    if cv2.waitKey(delay) & 0xFF == ord('q'):
        break

# -----------------------------
# CLEANUP
# -----------------------------
cap.release()
cv2.destroyAllWindows()