import cv2
import numpy as np
import matplotlib.pyplot as plt

# -----------------------------
# VIDEO
# -----------------------------
cap = cv2.VideoCapture(r"D:\Lie Detection Data HTI\Lie_detection_ex2\Thermal_lie_detection_ex2\grey_manual\purva_grey_manual.wmv")   # use 0 for webcam OR put your video path

ret, frame = cap.read()
if not ret:
    print("Error reading video")
    exit()

# -----------------------------
# SELECT ROI
# -----------------------------
bbox = cv2.selectROI("Select ROI", frame, False)
cv2.destroyWindow("Select ROI")

tracker = cv2.TrackerCSRT_create()
tracker.init(frame, bbox)

# -----------------------------
# GRAPH SETUP
# -----------------------------
plt.ion()
fig, ax = plt.subplots()

line, = ax.plot([], [], label="Mean Intensity")
ax.set_title("Live ROI Mean Signal")
ax.set_xlabel("Frame")
ax.set_ylabel("Intensity")
ax.legend()

signal = []
frame_count = 0
window_size = 200   # show last N points

# -----------------------------
# LOOP
# -----------------------------
while True:
    ret, frame = cap.read()
    if not ret:
        break

    success, bbox = tracker.update(frame)

    if success:
        x, y, w, h = [int(v) for v in bbox]

        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        roi = gray[y:y+h, x:x+w]

        if roi.size != 0:
            # 🔥 MEAN INTENSITY
            mean_val = np.mean(roi)
            signal.append(mean_val)

            # -----------------------------
            # UPDATE GRAPH
            # -----------------------------
            data = signal[-window_size:]
            x_vals = range(len(data))

            line.set_data(x_vals, data)

            ax.set_xlim(0, window_size)
            ax.set_ylim(min(data)-1, max(data)+1)

            plt.pause(0.001)

        # Draw bounding box
        cv2.rectangle(frame, (x,y), (x+w, y+h), (0,255,0), 2)

        # Show value
        cv2.putText(frame,
                    f"{mean_val:.2f}",
                    (x, y-10),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    0.6, (0,255,0), 2)

    else:
        cv2.putText(frame, "Tracking Lost",
                    (30,50),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    0.7, (0,0,255), 2)

    cv2.imshow("CSRT Tracking", frame)

    if cv2.waitKey(1) & 0xFF == 27:
        break

    frame_count += 1

# -----------------------------
# CLEANUP
# -----------------------------
cap.release()
cv2.destroyAllWindows()
plt.ioff()
plt.show()