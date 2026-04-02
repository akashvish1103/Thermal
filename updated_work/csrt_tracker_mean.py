# import cv2
# from matplotlib.pyplot import box
# import numpy as np
# import matplotlib.pyplot as plt

# def get_temp_from_pixel(pixel_value):
#     m = 0.05891454 
#     b = 30.07676744
#     return m*pixel_value + b                        # temperature = 0.05891454*(pixel_value) + 30.07676744

# # ---------------------------
# # 1. Read video
# # ---------------------------
# # vid_path = r"D:\Lie Detection Data HTI\Lie_detection_ex2\Audio_video_lie_detection_ex2\Krishan_lie_detection_ex2.mp4"
# vid_path = r"C:\Users\Akash Vishwakarma\Downloads\krishna_grey_manual1.mp4"

# cap = cv2.VideoCapture(vid_path)  # 0 for webcam

# # ---------------------------
# # 2. Read first frame
# # ---------------------------
# ret, frame = cap.read()

# # ---------------------------
# # 3. Select ROI manually
# # ---------------------------
# bbox = cv2.selectROI("Select Object", frame, False)  # (x, y) = where box starts (top-left corner)
#                                                      #  (w, h) = how big the box is
# cv2.destroyWindow("Select Object")

# # ---------------------------
# # 4. Create CSRT tracker
# # ---------------------------
# tracker = cv2.TrackerCSRT_create()

# # ---------------------------
# # 5. Initialize tracker
# # ---------------------------
# tracker.init(frame, bbox)

# # ---------------------------
# # 6. Tracking loop
# # ---------------------------
# while True:
#     ret, frame = cap.read()
#     grey_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
#     if not ret:
#         break

#     # Update tracker
#     success, bbox = tracker.update(frame)

#     if success:
#         x, y, w, h = [int(v) for v in bbox]

#         bbox_arr = grey_frame[y:y+h, x:x+w]
#         print(type(bbox_arr))        
#         print(bbox_arr.shape)
#         print(bbox_arr)

#         bbox_arr_mean = np.mean(bbox_arr)
#         print("Mean intensity in bbox:", bbox_arr_mean)

#         temp = get_temp_from_pixel(bbox_arr_mean)
#         print("Temperature corresponding to mean pixel value:", temp)


#         # Draw rectangle
#         cv2.rectangle(frame, (x,y), (x+w, y+h), (0,255,0), 2)

#     else:
#         cv2.putText(frame, "Tracking Lost", (50,50),
#                     cv2.FONT_HERSHEY_SIMPLEX, 1, (0,0,255), 2)

#     cv2.imshow("Tracking", frame)

#     if cv2.waitKey(1) & 0xFF == 27:
#         break

# cap.release()
# cv2.destroyAllWindows()

###########################################################################

# Add the live plotting of Temperature

# import cv2
# import numpy as np
# import matplotlib.pyplot as plt

# # ---------------------------
# # Temperature conversion
# # ---------------------------
# def get_temp_from_pixel(pixel_value):
#     m = 0.05891454 
#     b = 30.07676744
#     return m * pixel_value + b

# # ---------------------------
# # 1. Read video
# # ---------------------------
# vid_path = r"C:\Users\Akash Vishwakarma\Downloads\krishna_grey_manual1.mp4"
# cap = cv2.VideoCapture(vid_path)

# # ---------------------------
# # 2. Read first frame
# # ---------------------------
# ret, frame = cap.read()
# if not ret:
#     print("Error reading video")
#     exit()

# # ---------------------------
# # 3. Select ROI manually
# # ---------------------------
# bbox = cv2.selectROI("Select Object", frame, False)
# cv2.destroyWindow("Select Object")

# # ---------------------------
# # 4. Create tracker
# # ---------------------------
# tracker = cv2.TrackerCSRT_create()

# # ---------------------------
# # 5. Initialize tracker
# # ---------------------------
# tracker.init(frame, bbox)

# # ---------------------------
# # 6. LIVE GRAPH SETUP
# # ---------------------------
# plt.ion()  # interactive mode ON

# x_data = []
# y_data = []

# fig, ax = plt.subplots()
# line, = ax.plot(x_data, y_data)
# ax.set_title("Live Temperature Graph")
# ax.set_xlabel("Frame")
# ax.set_ylabel("Temperature")

# frame_count = 0
# MAX_POINTS = 200  # keep last 200 points

# # ---------------------------
# # 7. Tracking loop
# # ---------------------------
# while True:
#     ret, frame = cap.read()
#     if not ret:
#         break

#     grey_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

#     # Update tracker
#     success, bbox = tracker.update(frame)

#     if success:
#         x, y, w, h = [int(v) for v in bbox]

#         # Extract ROI
#         bbox_arr = grey_frame[y:y+h, x:x+w]

#         # Mean pixel intensity
#         bbox_arr_mean = np.mean(bbox_arr)

#         # Convert to temperature
#         temp = get_temp_from_pixel(bbox_arr_mean)

#         print(f"Frame {frame_count} | Temp: {temp:.2f}")

#         # ---------------------------
#         # UPDATE LIVE GRAPH
#         # ---------------------------
#         x_data.append(frame_count)
#         y_data.append(temp)

#         # Keep only last N points
#         if len(x_data) > MAX_POINTS:
#             x_data = x_data[-MAX_POINTS:]
#             y_data = y_data[-MAX_POINTS:]

#         line.set_xdata(x_data)
#         line.set_ydata(y_data)

#         ax.relim()
#         ax.autoscale_view()

#         plt.draw()
#         plt.pause(0.001)

#         frame_count += 1

#         # Draw bounding box
#         cv2.rectangle(frame, (x, y), (x+w, y+h), (0,255,0), 2)

#     else:
#         cv2.putText(frame, "Tracking Lost", (50,50),
#                     cv2.FONT_HERSHEY_SIMPLEX, 1, (0,0,255), 2)

#     cv2.imshow("Tracking", frame)

#     if cv2.waitKey(1) & 0xFF == 27:
#         break

# # ---------------------------
# # Cleanup
# # ---------------------------
# cap.release()
# cv2.destroyAllWindows()
# plt.ioff()
# plt.show()
###############################################################################

# added the time in x-axis LABEL instead of frame number.

# import cv2
# import numpy as np
# import matplotlib.pyplot as plt
# import matplotlib.ticker as ticker

# # ---------------------------
# # Temperature conversion
# # ---------------------------
# def get_temp_from_pixel(pixel_value):
#     m = 0.05891454 
#     b = 30.07676744
#     return m * pixel_value + b

# # ---------------------------
# # Format time (mm:ss)
# # ---------------------------
# def format_func(x, pos):
#     mins = int(x // 60)
#     secs = int(x % 60)
#     return f"{mins:02d}:{secs:02d}"

# # ---------------------------
# # 1. Read video
# # ---------------------------
# vid_path = r"C:\Users\Akash Vishwakarma\Downloads\krishna_grey_manual1.mp4"
# cap = cv2.VideoCapture(vid_path)

# # Get FPS
# fps = cap.get(cv2.CAP_PROP_FPS)
# print("FPS:", fps)

# # ---------------------------
# # 2. Read first frame
# # ---------------------------
# ret, frame = cap.read()
# if not ret:
#     print("Error reading video")
#     exit()

# # ---------------------------
# # 3. Select ROI manually
# # ---------------------------
# bbox = cv2.selectROI("Select Object", frame, False)
# cv2.destroyWindow("Select Object")

# # ---------------------------
# # 4. Create tracker
# # ---------------------------
# tracker = cv2.TrackerCSRT_create()

# # ---------------------------
# # 5. Initialize tracker
# # ---------------------------
# tracker.init(frame, bbox)

# # ---------------------------
# # 6. LIVE GRAPH SETUP
# # ---------------------------
# plt.ion()

# x_data = []
# y_data = []

# fig, ax = plt.subplots()
# line, = ax.plot(x_data, y_data)

# ax.set_title("Live Temperature Graph")
# ax.set_xlabel("Time (mm:ss)")
# ax.set_ylabel("Temperature")

# # Apply mm:ss formatter
# ax.xaxis.set_major_formatter(ticker.FuncFormatter(format_func))

# frame_count = 0
# MAX_POINTS = 200

# # ---------------------------
# # 7. Tracking loop
# # ---------------------------
# while True:
#     ret, frame = cap.read()
#     if not ret:
#         break

#     grey_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

#     # Update tracker
#     success, bbox = tracker.update(frame)

#     if success:
#         x, y, w, h = [int(v) for v in bbox]

#         # Extract ROI
#         bbox_arr = grey_frame[y:y+h, x:x+w]

#         # Mean pixel intensity
#         bbox_arr_mean = np.mean(bbox_arr)

#         # Convert to temperature
#         temp = get_temp_from_pixel(bbox_arr_mean)

#         # Time in seconds
#         time_sec = frame_count / fps

#         print(f"Time {format_func(time_sec, None)} | Temp: {temp:.2f}")

#         # ---------------------------
#         # UPDATE GRAPH
#         # ---------------------------
#         x_data.append(time_sec)
#         y_data.append(temp)

#         if len(x_data) > MAX_POINTS:
#             x_data = x_data[-MAX_POINTS:]
#             y_data = y_data[-MAX_POINTS:]

#         line.set_xdata(x_data)
#         line.set_ydata(y_data)

#         ax.relim()
#         ax.autoscale_view()

#         plt.draw()
#         plt.pause(0.001)

#         frame_count += 1

#         # Draw bounding box
#         cv2.rectangle(frame, (x, y), (x+w, y+h), (0,255,0), 2)

#     else:
#         cv2.putText(frame, "Tracking Lost", (50,50),
#                     cv2.FONT_HERSHEY_SIMPLEX, 1, (0,0,255), 2)

#     cv2.imshow("Tracking", frame)

#     if cv2.waitKey(1) & 0xFF == 27:
#         break

# # ---------------------------
# # Cleanup
# # ---------------------------
# cap.release()
# cv2.destroyAllWindows()
# plt.ioff()
# plt.show()

##########################################################

# Added smoothed graph and

import cv2
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.ticker as ticker

# ---------------------------
# Temperature conversion
# ---------------------------
def get_temp_from_pixel(pixel_value):
    m = 0.05891454 
    b = 30.07676744
    return m * pixel_value + b

# ---------------------------
# Moving average
# ---------------------------
def moving_average(signal, k=5):
    if len(signal) < k:
        return signal
    return np.convolve(signal, np.ones(k)/k, mode='same')

# ---------------------------
# Format time (mm:ss)
# ---------------------------
def format_func(x, pos):
    mins = int(x // 60)
    secs = int(x % 60)
    return f"{mins:02d}:{secs:02d}"

# ---------------------------
# VIDEO PATH
# ---------------------------
vid_path = r"C:\Users\Akash Vishwakarma\Downloads\krishna_grey_manual1.mp4"

cap = cv2.VideoCapture(vid_path)

if not cap.isOpened():
    print("Error: Cannot open video")
    exit()

fps = cap.get(cv2.CAP_PROP_FPS)
print("FPS:", fps)

# ---------------------------
# Read first frame
# ---------------------------
ret, frame = cap.read()
if not ret:
    print("Error reading first frame")
    exit()

# ---------------------------
# Select ROI
# ---------------------------
bbox = cv2.selectROI("Select ROI", frame, False)
cv2.destroyWindow("Select ROI")

# ---------------------------
# Tracker
# ---------------------------
tracker = cv2.TrackerCSRT_create()
tracker.init(frame, bbox)

# ---------------------------
# GRAPH SETUP
# ---------------------------
plt.ion()

x_data = []
y_raw = []
y_smooth = []

fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(8,6))

# Raw graph
line_raw, = ax1.plot([], [])
ax1.set_title("Raw Temperature")
ax1.set_ylabel("Temp (°C)")
ax1.xaxis.set_major_formatter(ticker.FuncFormatter(format_func))

# Smoothed graph
line_smooth, = ax2.plot([], [])
ax2.set_title("Smoothed Temperature")
ax2.set_xlabel("Time (mm:ss)")
ax2.set_ylabel("Temp (°C)")
ax2.xaxis.set_major_formatter(ticker.FuncFormatter(format_func))

frame_count = 0
MAX_POINTS = 200

# ---------------------------
# MAIN LOOP
# ---------------------------
while True:
    ret, frame = cap.read()
    if not ret:
        break

    grey = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

    success, bbox = tracker.update(frame)

    if success:
        x, y, w, h = [int(v) for v in bbox]

        # ROI extraction
        roi = grey[y:y+h, x:x+w]

        # Mean intensity → temperature
        mean_pixel = np.mean(roi)
        temp = get_temp_from_pixel(mean_pixel)

        # Time
        time_sec = frame_count / fps

        print(f"{format_func(time_sec, None)} | Temp: {temp:.2f}")

        # Store values
        x_data.append(time_sec)
        y_raw.append(temp)

        # Smooth signal
        y_smooth = moving_average(y_raw, k=15)

        # Limit window size
        if len(x_data) > MAX_POINTS:
            x_data = x_data[-MAX_POINTS:]
            y_raw = y_raw[-MAX_POINTS:]
            y_smooth = y_smooth[-MAX_POINTS:]

        # Update raw graph
        line_raw.set_xdata(x_data)
        line_raw.set_ydata(y_raw)

        # Update smooth graph
        line_smooth.set_xdata(x_data)
        line_smooth.set_ydata(y_smooth)

        # Rescale
        ax1.relim()
        ax1.autoscale_view()

        ax2.relim()
        ax2.autoscale_view()

        plt.draw()
        plt.pause(0.001)

        frame_count += 1

        # Draw box
        cv2.rectangle(frame, (x,y), (x+w, y+h), (0,255,0), 2)

    else:
        cv2.putText(frame, "Tracking Lost", (50,50),
                    cv2.FONT_HERSHEY_SIMPLEX, 1, (0,0,255), 2)

    cv2.imshow("Tracking", frame)

    # Press ESC to exit
    if cv2.waitKey(1) & 0xFF == 27:
        break

# ---------------------------
# CLEANUP
# ---------------------------
cap.release()
cv2.destroyAllWindows()
plt.ioff()
plt.show()