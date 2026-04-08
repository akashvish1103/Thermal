# import cv2
# import numpy as np
# import pyqtgraph as pg
# from pyqtgraph.Qt import QtWidgets, QtCore

# # =========================================================
# # 🔴 USER SETTINGS (EDIT THESE)
# # =========================================================
# THRESHOLD_TEMP = 0.2   # change threshold (in °C)
# SMOOTH_K = 7           # smoothing strength
# MAX_POINTS = 200       # number of points(frames) shown in graph  

# # Background colors (CHANGE THESE)
# BG_COLOR_RAW = 'm' #(30, 30, 30)
# BG_COLOR_SMOOTH = (30, 30, 30)
# BG_COLOR_HEAD = (30, 30, 30)

# # =========================================================
# # Custom Time Axis (mm:ss format)
# # =========================================================
# class TimeAxisItem(pg.AxisItem):
#     def tickStrings(self, values, scale, spacing):
#         strings = []
#         for v in values:
#             mins = int(v // 60)
#             secs = int(v % 60)
#             strings.append(f"{mins:02d}:{secs:02d}")
#         return strings

# # =========================================================
# # Temperature conversion
# # =========================================================
# def get_temp_from_pixel(pixel_value):
#     m = 0.05891454 
#     b = 30.07676744
#     return m * pixel_value + b

# # =========================================================
# # Moving average (no edge distortion)
# # =========================================================
# def moving_average(signal, k=5):
#     if len(signal) < k:
#         return signal

#     smooth = np.convolve(signal, np.ones(k)/k, mode='valid')

#     # Padding to keep same length
#     pad_left = [smooth[0]] * (k//2)
#     pad_right = [smooth[-1]] * (k//2)

#     return np.concatenate([pad_left, smooth, pad_right])

# # =========================================================
# # VIDEO SETUP
# # =========================================================
# vid_path = r"C:\Users\Akash Vishwakarma\Downloads\krishna_grey_manual1.mp4"
# cap = cv2.VideoCapture(vid_path)

# fps = cap.get(cv2.CAP_PROP_FPS)

# ret, frame = cap.read()
# if not ret:
#     print("Error reading video")
#     exit()

# # =========================================================
# # ROI SELECTION
# # =========================================================
# print("Select NOSE ROI")
# bbox_nose = cv2.selectROI("Nose ROI", frame, False)
# cv2.destroyWindow("Nose ROI")

# print("Select FOREHEAD ROI")
# bbox_head = cv2.selectROI("Forehead ROI", frame, False)
# cv2.destroyWindow("Forehead ROI")

# # =========================================================
# # TRACKERS
# # =========================================================
# tracker_nose = cv2.TrackerCSRT_create()
# tracker_head = cv2.TrackerCSRT_create()

# tracker_nose.init(frame, bbox_nose)
# tracker_head.init(frame, bbox_head)

# # =========================================================
# # PYQTGRAPH WINDOW
# # =========================================================
# app = QtWidgets.QApplication([])

# win = pg.GraphicsLayoutWidget(show=True, title="Thermal Monitoring System")
# win.resize(900, 800)

# # ---------------------------
# # Plot 1: Nose RAW
# # ---------------------------
# p1 = win.addPlot(
#     axisItems={'bottom': TimeAxisItem(orientation='bottom')},
#     title="Nose Raw Temperature"
# )
# # p1.setBackground(BG_COLOR_RAW) 
# p1.getViewBox().setBackgroundColor(BG_COLOR_RAW)  # 🔥 change color here
# curve_raw = p1.plot(pen='y')     # yellow line

# # ---------------------------
# # Plot 2: Nose SMOOTHED
# # ---------------------------
# win.nextRow()
# p2 = win.addPlot(
#     axisItems={'bottom': TimeAxisItem(orientation='bottom')},
#     title="Nose Smoothed Temperature"
# )
# # p2.setBackground(BG_COLOR_SMOOTH)
# p2.getViewBox().setBackgroundColor(BG_COLOR_SMOOTH)  # 🔥 change color here
# curve_smooth = p2.plot(pen='g')  # green line

# # ---------------------------
# # Plot 3: Forehead
# # ---------------------------
# win.nextRow()
# p3 = win.addPlot(
#     axisItems={'bottom': TimeAxisItem(orientation='bottom')},
#     title="Forehead Stress Signal"
# )
# # p3.setBackground(BG_COLOR_HEAD)
# p3.getViewBox().setBackgroundColor(BG_COLOR_HEAD)  # 🔥 change color here
# curve_head = p3.plot(pen='b')    # blue/red (dynamic)

# # =========================================================
# # DATA STORAGE
# # =========================================================
# x_data = []
# y_nose = []
# y_head = []

# frame_count = 0
# baseline = None  # first forehead temp

# # =========================================================
# # MAIN UPDATE LOOP
# # =========================================================
# def update():
#     global frame_count, baseline, x_data, y_nose, y_head

#     ret, frame = cap.read()
#     if not ret:
#         QtWidgets.QApplication.quit()
#         return

#     gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

#     success_nose, bbox_nose = tracker_nose.update(frame)
#     success_head, bbox_head = tracker_head.update(frame)

#     if success_nose and success_head:

#         # ---------------------------
#         # NOSE (breathing)
#         # ---------------------------
#         x1, y1, w1, h1 = [int(v) for v in bbox_nose]
#         roi_nose = gray[y1:y1+h1, x1:x1+w1]
#         temp_nose = get_temp_from_pixel(np.mean(roi_nose))

#         # ---------------------------
#         # FOREHEAD (stress)
#         # ---------------------------
#         x2, y2, w2, h2 = [int(v) for v in bbox_head]
#         roi_head = gray[y2:y2+h2, x2:x2+w2]
#         temp_head = get_temp_from_pixel(np.mean(roi_head))

#         # ---------------------------
#         # TIME (seconds)
#         # ---------------------------
#         time_sec = frame_count / fps

#         # Store data
#         x_data.append(time_sec)
#         y_nose.append(temp_nose)
#         y_head.append(temp_head)

#         # Set baseline from FIRST frame
#         if baseline is None:
#             baseline = temp_head

#         # Smooth breathing signal
#         y_smooth = moving_average(y_nose, SMOOTH_K)

#         # Limit data size
#         if len(x_data) > MAX_POINTS:
#             x_data = x_data[-MAX_POINTS:]
#             y_nose = y_nose[-MAX_POINTS:]
#             y_head = y_head[-MAX_POINTS:]
#             y_smooth = y_smooth[-MAX_POINTS:]

#         # ---------------------------
#         # UPDATE GRAPHS
#         # ---------------------------

#         # Nose raw
#         curve_raw.setData(x_data, y_nose)

#         # Nose smoothed
#         curve_smooth.setData(x_data, y_smooth)

#         # Forehead color logic
#         if temp_head >= baseline + THRESHOLD_TEMP:
#             curve_head.setPen('r')   # 🔴 stress
#         else:
#             curve_head.setPen('b')   # 🔵 normal

#         curve_head.setData(x_data, y_head)

#         frame_count += 1

#         # ---------------------------
#         # DRAW BOUNDING BOXES
#         # ---------------------------
#         cv2.rectangle(frame, (x1,y1), (x1+w1,y1+h1), (255,0,0), 2)
#         cv2.rectangle(frame, (x2,y2), (x2+w2,y2+h2), (0,255,0), 2)

#         # Display status
#         status = "STRESS" if temp_head >= baseline + THRESHOLD_TEMP else "NORMAL"
#         cv2.putText(frame, status, (50,100),
#                     cv2.FONT_HERSHEY_SIMPLEX, 1,
#                     (0,0,255) if status=="STRESS" else (255,0,0), 2)

#     cv2.imshow("Tracking", frame)

#     # Exit on ESC
#     if cv2.waitKey(1) & 0xFF == 27:
#         QtWidgets.QApplication.quit()

# # =========================================================
# # TIMER (drives real-time update)
# # =========================================================
# timer = QtCore.QTimer()
# timer.timeout.connect(update)
# timer.start(30)  # ~30 FPS

# # =========================================================
# # RUN APP
# # =========================================================
# QtWidgets.QApplication.instance().exec_()

# # =========================================================
# # CLEANUP
# # =========================================================
# cap.release()
# cv2.destroyAllWindows()

#################################################

# added display of temperature value(Forehead and Nose) on cv2 window


# import cv2
# import numpy as np
# import pyqtgraph as pg
# from pyqtgraph.Qt import QtWidgets, QtCore

# # =========================================================
# # 🔴 USER SETTINGS
# # =========================================================
# THRESHOLD_TEMP = 0.05   # change this (°C)
# SMOOTH_K = 5
# MAX_POINTS = 200

# # Background colors (CHANGE HERE)
# BG_COLOR_RAW = (30, 30, 30)
# BG_COLOR_SMOOTH = (30, 30, 30)
# BG_COLOR_HEAD = (30, 30, 30)

# # =========================================================
# # Custom Time Axis (mm:ss)
# # =========================================================
# class TimeAxisItem(pg.AxisItem):
#     def tickStrings(self, values, scale, spacing):
#         return [f"{int(v//60):02d}:{int(v%60):02d}" for v in values]

# # =========================================================
# # Temperature conversion
# # =========================================================
# def get_temp_from_pixel(pixel_value):
#     return 0.05891454 * pixel_value + 30.07676744

# # =========================================================
# # Moving average
# # =========================================================
# def moving_average(signal, k=5):
#     if len(signal) < k:
#         return signal

#     smooth = np.convolve(signal, np.ones(k)/k, mode='valid')
#     pad_left = [smooth[0]] * (k//2)
#     pad_right = [smooth[-1]] * (k//2)

#     return np.concatenate([pad_left, smooth, pad_right])

# # =========================================================
# # VIDEO
# # =========================================================
# vid_path = r"C:\Users\Akash Vishwakarma\Downloads\krishna_grey_manual1.mp4"
# cap = cv2.VideoCapture(vid_path)

# fps = cap.get(cv2.CAP_PROP_FPS)

# ret, frame = cap.read()
# if not ret:
#     print("Error reading video")
#     exit()

# # =========================================================
# # ROI SELECTION
# # =========================================================
# print("Select NOSE ROI")
# bbox_nose = cv2.selectROI("Nose ROI", frame, False)
# cv2.destroyWindow("Nose ROI")

# print("Select FOREHEAD ROI")
# bbox_head = cv2.selectROI("Forehead ROI", frame, False)
# cv2.destroyWindow("Forehead ROI")

# # =========================================================
# # TRACKERS
# # =========================================================
# tracker_nose = cv2.TrackerCSRT_create()
# tracker_head = cv2.TrackerCSRT_create()

# tracker_nose.init(frame, bbox_nose)
# tracker_head.init(frame, bbox_head)

# # =========================================================
# # PYQTGRAPH SETUP
# # =========================================================
# app = QtWidgets.QApplication([])
# win = pg.GraphicsLayoutWidget(show=True, title="Thermal Monitoring")
# win.resize(900, 800)

# # -------- Plot 1: Nose Raw --------
# p1 = win.addPlot(axisItems={'bottom': TimeAxisItem(orientation='bottom')}, title="Nose Raw")
# p1.getViewBox().setBackgroundColor(BG_COLOR_RAW)
# curve_raw = p1.plot(pen='y')

# # -------- Plot 2: Nose Smooth --------
# win.nextRow()
# p2 = win.addPlot(axisItems={'bottom': TimeAxisItem(orientation='bottom')}, title="Nose Smoothed")
# p2.getViewBox().setBackgroundColor(BG_COLOR_SMOOTH)
# curve_smooth = p2.plot(pen='g')

# # -------- Plot 3: Forehead --------
# win.nextRow()
# p3 = win.addPlot(axisItems={'bottom': TimeAxisItem(orientation='bottom')}, title="Forehead Stress")
# p3.getViewBox().setBackgroundColor(BG_COLOR_HEAD)

# # =========================================================
# # DATA
# # =========================================================
# x_data = []
# y_nose = []
# y_head = []

# frame_count = 0
# baseline = None

# # =========================================================
# # UPDATE LOOP
# # =========================================================
# def update():
#     global frame_count, baseline, x_data, y_nose, y_head

#     ret, frame = cap.read()
#     if not ret:
#         QtWidgets.QApplication.quit()
#         return

#     gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

#     success_nose, bbox_nose = tracker_nose.update(frame)
#     success_head, bbox_head = tracker_head.update(frame)

#     if success_nose and success_head:

#         # ---------------- NOSE ----------------
#         x1, y1, w1, h1 = [int(v) for v in bbox_nose]
#         roi_nose = gray[y1:y1+h1, x1:x1+w1]
#         temp_nose = get_temp_from_pixel(np.mean(roi_nose))
#         # -------- NOSE --------
#         cv2.putText(
#             frame,
#             f"nose temp: {temp_nose:.2f} C",
#             (x1,y1-10),   # position on screen
#             cv2.FONT_HERSHEY_SIMPLEX,
#             0.6,
#             (0, 255, 255),   # yellow color
#             2
#         )

#         # ---------------- FOREHEAD ----------------
#         x2, y2, w2, h2 = [int(v) for v in bbox_head]
#         roi_head = gray[y2:y2+h2, x2:x2+w2]
#         temp_head = get_temp_from_pixel(np.mean(roi_head))

#         # -------- DISPLAY TEMPERATURE ON FRAME --------
#         cv2.putText(
#             frame,
#             f"forehead Temp: {temp_head:.2f} C",
#             (x2, y2 - 10),  # position above forehead box
#             cv2.FONT_HERSHEY_SIMPLEX,
#             0.6,
#             (0, 255, 0),   # green color
#             2
#         )

#         # ---------------- TIME ----------------
#         time_sec = frame_count / fps

#         x_data.append(time_sec)
#         y_nose.append(temp_nose)
#         y_head.append(temp_head)

#         # Baseline (first frame)
#         if baseline is None:
#             baseline = temp_head

#         # Smooth
#         y_smooth = moving_average(y_nose, SMOOTH_K)

#         # Limit window
#         if len(x_data) > MAX_POINTS:
#             x_data = x_data[-MAX_POINTS:]
#             y_nose = y_nose[-MAX_POINTS:]
#             y_head = y_head[-MAX_POINTS:]
#             y_smooth = y_smooth[-MAX_POINTS:]

#         # -------- Update Nose Graphs --------
#         curve_raw.setData(x_data, y_nose)
#         curve_smooth.setData(x_data, y_smooth)

#         # -------- Forehead (Segment Coloring) --------
#         p3.clear()
#         p3.setTitle("Forehead Stress")
#         p3.getViewBox().setBackgroundColor(BG_COLOR_HEAD)

#         for i in range(len(x_data)-1):
#             xs = [x_data[i], x_data[i+1]]
#             ys = [y_head[i], y_head[i+1]]

#             if y_head[i] >= baseline + THRESHOLD_TEMP:
#                 color = 'r'
#             else:
#                 color = 'b'

#             p3.plot(xs, ys, pen=pg.mkPen(color, width=2))

#         # -------- Draw Boxes --------
#         cv2.rectangle(frame, (x1,y1), (x1+w1,y1+h1), (255,0,0), 2)
#         cv2.rectangle(frame, (x2,y2), (x2+w2,y2+h2), (0,255,0), 2)

#         frame_count += 1

#     cv2.imshow("Tracking", frame)

#     if cv2.waitKey(1) & 0xFF == 27:
#         QtWidgets.QApplication.quit()

# # =========================================================
# # TIMER
# # =========================================================
# timer = QtCore.QTimer()
# timer.timeout.connect(update)
# timer.start(30)

# # =========================================================
# # RUN
# # =========================================================
# QtWidgets.QApplication.instance().exec_()

# cap.release()
# cv2.destroyAllWindows()

###################################################################### 
# adding level bar for lungs capacity

# import cv2
# import numpy as np
# import pyqtgraph as pg
# from pyqtgraph.Qt import QtWidgets, QtCore

# # =========================================================
# # 🔴 USER SETTINGS
# # =========================================================
# THRESHOLD_TEMP = 0.05
# SMOOTH_K = 5
# MAX_POINTS = 200

# # Background colors
# BG_COLOR_RAW = (30, 30, 30)
# BG_COLOR_SMOOTH = (30, 30, 30)
# BG_COLOR_HEAD = (30, 30, 30)

# # -------- BREATH BAR SETTINGS --------
# BAR_X = 550
# BAR_Y = 100
# BAR_WIDTH = 40
# BAR_HEIGHT = 300

# nose_min = None
# nose_max = None

# # =========================================================
# # Custom Time Axis
# # =========================================================
# class TimeAxisItem(pg.AxisItem):
#     def tickStrings(self, values, scale, spacing):
#         return [f"{int(v//60):02d}:{int(v%60):02d}" for v in values]

# # =========================================================
# # Temperature conversion
# # =========================================================
# def get_temp_from_pixel(pixel_value):
#     return 0.05891454 * pixel_value + 30.07676744

# # =========================================================
# # Moving average
# # =========================================================
# def moving_average(signal, k=5):
#     if len(signal) < k:
#         return signal

#     smooth = np.convolve(signal, np.ones(k)/k, mode='valid')
#     pad_left = [smooth[0]] * (k//2)
#     pad_right = [smooth[-1]] * (k//2)

#     return np.concatenate([pad_left, smooth, pad_right])

# # =========================================================
# # VIDEO
# # =========================================================
# cap = cv2.VideoCapture(r"C:\Users\Akash Vishwakarma\Downloads\krishna_grey_manual1.mp4")
# fps = cap.get(cv2.CAP_PROP_FPS)

# ret, frame = cap.read()
# if not ret:
#     exit()

# print("Select NOSE ROI")
# bbox_nose = cv2.selectROI("Nose ROI", frame, False)
# cv2.destroyWindow("Nose ROI")

# print("Select FOREHEAD ROI")
# bbox_head = cv2.selectROI("Forehead ROI", frame, False)
# cv2.destroyWindow("Forehead ROI")

# tracker_nose = cv2.TrackerCSRT_create()
# tracker_head = cv2.TrackerCSRT_create()

# tracker_nose.init(frame, bbox_nose)
# tracker_head.init(frame, bbox_head)

# # =========================================================
# # UI
# # =========================================================
# app = QtWidgets.QApplication([])
# win = pg.GraphicsLayoutWidget(show=True)
# win.resize(900, 800)

# p1 = win.addPlot(axisItems={'bottom': TimeAxisItem(orientation='bottom')}, title="Nose Raw")
# p1.getViewBox().setBackgroundColor(BG_COLOR_RAW)
# curve_raw = p1.plot(pen='y')

# win.nextRow()
# p2 = win.addPlot(axisItems={'bottom': TimeAxisItem(orientation='bottom')}, title="Nose Smooth")
# p2.getViewBox().setBackgroundColor(BG_COLOR_SMOOTH)
# curve_smooth = p2.plot(pen='g')

# win.nextRow()
# p3 = win.addPlot(axisItems={'bottom': TimeAxisItem(orientation='bottom')}, title="Forehead")
# p3.getViewBox().setBackgroundColor(BG_COLOR_HEAD)
# curve_head = p3.plot(pen='c')

# # =========================================================
# # DATA
# # =========================================================
# x_data, y_nose, y_head = [], [], []
# frame_count = 0

# # =========================================================
# # LOOP
# # =========================================================
# def update():
#     global frame_count, nose_min, nose_max

#     ret, frame = cap.read()
#     if not ret:
#         QtWidgets.QApplication.quit()
#         return

#     gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

#     ok1, bbox_nose_ = tracker_nose.update(frame)
#     ok2, bbox_head_ = tracker_head.update(frame)

#     if ok1 and ok2:

#         x1,y1,w1,h1 = map(int, bbox_nose_)
#         x2,y2,w2,h2 = map(int, bbox_head_)

#         # -------- TEMPERATURE --------
#         temp_nose = get_temp_from_pixel(np.mean(gray[y1:y1+h1, x1:x1+w1]))
#         temp_head = get_temp_from_pixel(np.mean(gray[y2:y2+h2, x2:x2+w2]))

#         # -------- DISPLAY TEMPERATURE --------
#         cv2.putText(frame, f"Nose: {temp_nose:.2f} C",
#                     (50,50), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0,255,255), 2)

#         cv2.putText(frame, f"Forehead: {temp_head:.2f} C",
#                     (50,90), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0,255,0), 2)

#         # -------- TIME --------
#         t = frame_count / fps

#         x_data.append(t)
#         y_nose.append(temp_nose)
#         y_head.append(temp_head)

#         y_smooth = moving_average(y_nose, SMOOTH_K)

#         if len(x_data) > MAX_POINTS:
#             x_data[:] = x_data[-MAX_POINTS:]
#             y_nose[:] = y_nose[-MAX_POINTS:]
#             y_head[:] = y_head[-MAX_POINTS:]
#             y_smooth[:] = y_smooth[-MAX_POINTS:]

#         # -------- UPDATE GRAPHS --------
#         curve_raw.setData(x_data, y_nose)
#         curve_smooth.setData(x_data, y_smooth)
#         curve_head.setData(x_data, y_head)

#         # =========================================================
#         # 🔥 BREATH BAR LOGIC
#         # =========================================================
#         if nose_min is None:
#             nose_min = temp_nose
#             nose_max = temp_nose

#         nose_min = min(nose_min, temp_nose)
#         nose_max = max(nose_max, temp_nose)

#         if nose_max - nose_min < 0.01:
#             level = 0.5
#         else:
#             level = 1 - ((temp_nose - nose_min) / (nose_max - nose_min))

#         level = max(0, min(1, level))

#         # -------- DRAW BAR --------
#         cv2.rectangle(frame,
#                       (BAR_X, BAR_Y),
#                       (BAR_X + BAR_WIDTH, BAR_Y + BAR_HEIGHT),
#                       (200,200,200), 2)

#         fill_height = int(level * BAR_HEIGHT)

#         color = (255, int(255 * level), 0)

#         cv2.rectangle(frame,
#                       (BAR_X, BAR_Y + BAR_HEIGHT - fill_height),
#                       (BAR_X + BAR_WIDTH, BAR_Y + BAR_HEIGHT),
#                       color, -1)

#         cv2.putText(frame, "Breath",
#                     (BAR_X - 10, BAR_Y - 10),
#                     cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255,255,255), 2)

#         # -------- ROI BOXES --------
#         cv2.rectangle(frame, (x1,y1),(x1+w1,y1+h1),(255,0,0),2)
#         cv2.rectangle(frame, (x2,y2),(x2+w2,y2+h2),(0,255,0),2)

#         frame_count += 1

#     cv2.imshow("Tracking", frame)

#     if cv2.waitKey(1) & 0xFF == 27:
#         QtWidgets.QApplication.quit()

# # =========================================================
# # TIMER
# # =========================================================
# timer = QtCore.QTimer()
# timer.timeout.connect(update)
# timer.start(20)

# QtWidgets.QApplication.instance().exec_()

# cap.release()
# cv2.destroyAllWindows()

###################################################################
# code was stopping previouslt, make it to run 

# import cv2
# import numpy as np
# import pyqtgraph as pg
# from pyqtgraph.Qt import QtWidgets, QtCore

# # =========================================================
# # 🔴 USER SETTINGS
# # =========================================================
# THRESHOLD_TEMP = 0.01
# SMOOTH_K = 5
# MAX_POINTS = 200

# # Background colors
# BG_COLOR_RAW = (30, 30, 30)
# BG_COLOR_SMOOTH = (30, 30, 30)
# BG_COLOR_HEAD = (30, 30, 30)

# # -------- BREATH BAR SETTINGS --------
# BAR_X = 550
# BAR_Y = 100
# BAR_WIDTH = 40
# BAR_HEIGHT = 300

# nose_min = None
# nose_max = None

# # =========================================================
# # Time Axis
# # =========================================================
# class TimeAxisItem(pg.AxisItem):
#     def tickStrings(self, values, scale, spacing):
#         return [f"{int(v//60):02d}:{int(v%60):02d}" for v in values]

# # =========================================================
# # FUNCTIONS
# # =========================================================
# def get_temp_from_pixel(p):
#     return 0.05891454 * p + 30.07676744

# def moving_average(signal, k=5):
#     if len(signal) < k:
#         return signal

#     smooth = np.convolve(signal, np.ones(k)/k, mode='valid')
#     pad_left = [smooth[0]] * (k//2)
#     pad_right = [smooth[-1]] * (k//2)

#     return list(np.concatenate([pad_left, smooth, pad_right]))

# # =========================================================
# # VIDEO
# # =========================================================
# cap = cv2.VideoCapture(r"C:\Users\Akash Vishwakarma\Downloads\krishna_grey_manual1.mp4")
# fps = cap.get(cv2.CAP_PROP_FPS)

# ret, frame = cap.read()
# if not ret:
#     exit()

# print("Select NOSE ROI")
# bbox_nose = cv2.selectROI("Nose ROI", frame, False)
# cv2.destroyWindow("Nose ROI")

# print("Select FOREHEAD ROI")
# bbox_head = cv2.selectROI("Forehead ROI", frame, False)
# cv2.destroyWindow("Forehead ROI")

# tracker_nose = cv2.TrackerCSRT_create()
# tracker_head = cv2.TrackerCSRT_create()

# tracker_nose.init(frame, bbox_nose)
# tracker_head.init(frame, bbox_head)

# # =========================================================
# # UI
# # =========================================================
# app = QtWidgets.QApplication([])
# win = pg.GraphicsLayoutWidget(show=True)
# win.resize(900, 800)

# p1 = win.addPlot(axisItems={'bottom': TimeAxisItem(orientation='bottom')}, title="Nose Raw")
# p1.getViewBox().setBackgroundColor(BG_COLOR_RAW)
# curve_raw = p1.plot(pen='y')

# win.nextRow()
# p2 = win.addPlot(axisItems={'bottom': TimeAxisItem(orientation='bottom')}, title="Nose Smooth")
# p2.getViewBox().setBackgroundColor(BG_COLOR_SMOOTH)
# curve_smooth = p2.plot(pen='g')

# win.nextRow()
# p3 = win.addPlot(axisItems={'bottom': TimeAxisItem(orientation='bottom')}, title="Forehead")
# p3.getViewBox().setBackgroundColor(BG_COLOR_HEAD)
# curve_head = p3.plot(pen='c')

# # =========================================================
# # DATA
# # =========================================================
# x_data, y_nose, y_head = [], [], []
# frame_count = 0

# # =========================================================
# # LOOP
# # =========================================================
# def update():
#     global frame_count, nose_min, nose_max, x_data, y_nose, y_head

#     ret, frame = cap.read()
#     if not ret:
#         QtWidgets.QApplication.quit()
#         return

#     gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

#     ok1, bbox_nose_ = tracker_nose.update(frame)
#     ok2, bbox_head_ = tracker_head.update(frame)

#     if ok1 and ok2:

#         x1,y1,w1,h1 = map(int, bbox_nose_)
#         x2,y2,w2,h2 = map(int, bbox_head_)

#         # -------- TEMPERATURE --------
#         temp_nose = get_temp_from_pixel(np.mean(gray[y1:y1+h1, x1:x1+w1]))
#         temp_head = get_temp_from_pixel(np.mean(gray[y2:y2+h2, x2:x2+w2]))

#         # -------- DISPLAY --------
#         cv2.putText(frame, f"Nose: {temp_nose:.2f} C",
#                     (50,50), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0,255,255), 2)

#         cv2.putText(frame, f"Forehead: {temp_head:.2f} C",
#                     (50,90), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0,255,0), 2)

#         # -------- TIME --------
#         t = frame_count / fps

#         x_data.append(t)
#         y_nose.append(temp_nose)
#         y_head.append(temp_head)

#         # -------- SMOOTH --------
#         y_smooth = moving_average(y_nose, SMOOTH_K)

#         # -------- LIMIT SIZE (FIXED BUG) --------
#         if len(x_data) > MAX_POINTS:
#             x_data = x_data[-MAX_POINTS:]
#             y_nose = y_nose[-MAX_POINTS:]
#             y_head = y_head[-MAX_POINTS:]
#             y_smooth = y_smooth[-MAX_POINTS:]

#         # -------- UPDATE GRAPHS --------
#         curve_raw.setData(x_data, y_nose)
#         curve_smooth.setData(x_data, y_smooth)
#         curve_head.setData(x_data, y_head)

#         # =========================================================
#         # 🔥 BREATH BAR
#         # =========================================================
#         if nose_min is None:
#             nose_min = temp_nose
#             nose_max = temp_nose

#         nose_min = min(nose_min, temp_nose)
#         nose_max = max(nose_max, temp_nose)

#         if nose_max - nose_min < 0.01:
#             level = 0.5
#         else:
#             level = 1 - ((temp_nose - nose_min) / (nose_max - nose_min))

#         level = max(0, min(1, level))

#         # Outer box
#         cv2.rectangle(frame,
#                       (BAR_X, BAR_Y),
#                       (BAR_X + BAR_WIDTH, BAR_Y + BAR_HEIGHT),
#                       (200,200,200), 2)

#         # Fill
#         fill_h = int(level * BAR_HEIGHT)
#         color = (255, int(255 * level), 0)

#         cv2.rectangle(frame,
#                       (BAR_X, BAR_Y + BAR_HEIGHT - fill_h),
#                       (BAR_X + BAR_WIDTH, BAR_Y + BAR_HEIGHT),
#                       color, -1)

#         cv2.putText(frame, "Breath",
#                     (BAR_X - 10, BAR_Y - 10),
#                     cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255,255,255), 2)

#         # ROI boxes
#         cv2.rectangle(frame, (x1,y1),(x1+w1,y1+h1),(255,0,0),2)
#         cv2.rectangle(frame, (x2,y2),(x2+w2,y2+h2),(0,255,0),2)

#         frame_count += 1

#     cv2.imshow("Tracking", frame)

#     if cv2.waitKey(1) & 0xFF == 27:
#         QtWidgets.QApplication.quit()

# # =========================================================
# # TIMER
# # =========================================================
# timer = QtCore.QTimer()
# timer.timeout.connect(update)
# timer.start(20)

# QtWidgets.QApplication.instance().exec_()

# cap.release()
# cv2.destroyAllWindows()
######################################################
# With impred red/blue color for forehead graph
import cv2
import numpy as np
import pyqtgraph as pg
from pyqtgraph.Qt import QtWidgets, QtCore

# =========================================================
# SETTINGS
# =========================================================
THRESHOLD_TEMP = 0.05          # How  much temp must rise above baseline to be called as "stress" or "cognitive load"
SMOOTH_K = 5
MAX_POINTS = 200

BAR_X, BAR_Y = 550, 100
BAR_WIDTH, BAR_HEIGHT = 40, 300

nose_min, nose_max = None, None

# =========================================================
# TIME AXIS
# =========================================================
class TimeAxisItem(pg.AxisItem):
    def tickStrings(self, values, scale, spacing):
        return [f"{int(v//60):02d}:{int(v%60):02d}" for v in values]

# =========================================================
# FUNCTIONS
# =========================================================
def get_temp_from_pixel(p):
    return 0.05891454 * p + 30.07676744

def moving_average(signal, k=5):
    if len(signal) < k:
        return signal
    smooth = np.convolve(signal, np.ones(k)/k, mode='valid')
    pad_left = [smooth[0]] * (k//2)
    pad_right = [smooth[-1]] * (k//2)
    return list(np.concatenate([pad_left, smooth, pad_right]))

# =========================================================
# VIDEO
# =========================================================
cap = cv2.VideoCapture(r"C:\Users\Akash Vishwakarma\Downloads\krishna_grey_manual1.mp4")
fps = cap.get(cv2.CAP_PROP_FPS)

ret, frame = cap.read()
if not ret:
    exit()

print("Select NOSE ROI")
bbox_nose = cv2.selectROI("Nose ROI", frame, False)
cv2.destroyWindow("Nose ROI")

print("Select FOREHEAD ROI")
bbox_head = cv2.selectROI("Forehead ROI", frame, False)
cv2.destroyWindow("Forehead ROI")

tracker_nose = cv2.TrackerCSRT_create()
tracker_head = cv2.TrackerCSRT_create()
tracker_nose.init(frame, bbox_nose)
tracker_head.init(frame, bbox_head)

# =========================================================
# UI
# =========================================================
app = QtWidgets.QApplication([])
win = pg.GraphicsLayoutWidget(show=True)
win.resize(900, 800)

p1 = win.addPlot(axisItems={'bottom': TimeAxisItem(orientation='bottom')}, title="Nose Raw")
curve_raw = p1.plot(pen='y')

win.nextRow()
p2 = win.addPlot(axisItems={'bottom': TimeAxisItem(orientation='bottom')}, title="Nose Smooth")
curve_smooth = p2.plot(pen='g')

win.nextRow()
p3 = win.addPlot(axisItems={'bottom': TimeAxisItem(orientation='bottom')}, title="Forehead")
curve_blue = p3.plot(pen='b')
curve_red = p3.plot(pen='r')

# =========================================================
# DATA
# =========================================================
x_data, y_nose, y_head = [], [], []
frame_count = 0

# =========================================================
# LOOP
# =========================================================
def update():
    global frame_count, nose_min, nose_max
    global x_data, y_nose, y_head

    ret, frame = cap.read()
    if not ret:
        QtWidgets.QApplication.quit()
        return

    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

    ok1, b1 = tracker_nose.update(frame)
    ok2, b2 = tracker_head.update(frame)

    if ok1 and ok2:

        x1,y1,w1,h1 = map(int, b1)
        x2,y2,w2,h2 = map(int, b2)

        temp_nose = get_temp_from_pixel(np.mean(gray[y1:y1+h1, x1:x1+w1]))
        temp_head = get_temp_from_pixel(np.mean(gray[y2:y2+h2, x2:x2+w2]))

        # -------- DISPLAY --------
        cv2.putText(frame, f"Nose: {temp_nose:.2f} C", (50,50),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0,255,255), 2)

        cv2.putText(frame, f"Forehead: {temp_head:.2f} C", (50,90),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0,255,0), 2)

        # -------- TIME --------
        t = frame_count / fps
        x_data.append(t)
        y_nose.append(temp_nose)
        y_head.append(temp_head)

        y_smooth = moving_average(y_nose, SMOOTH_K)

        if len(x_data) > MAX_POINTS:
            x_data = x_data[-MAX_POINTS:]
            y_nose = y_nose[-MAX_POINTS:]
            y_head = y_head[-MAX_POINTS:]
            y_smooth = y_smooth[-MAX_POINTS:]

        # -------- GRAPHS --------
        curve_raw.setData(x_data, y_nose)
        curve_smooth.setData(x_data, y_smooth)

        # -------- FOREHEAD COLOR LOGIC --------
        baseline = np.mean(y_head[:20]) if len(y_head) >= 20 else y_head[0]

        y_blue, y_red = [], []
        for val in y_head:
            if val >= baseline + THRESHOLD_TEMP:
                y_red.append(val)
                y_blue.append(np.nan)
            else:
                y_blue.append(val)
                y_red.append(np.nan)

        curve_blue.setData(x_data, y_blue)
        curve_red.setData(x_data, y_red)

        # -------- BREATH BAR --------
        if nose_min is None:
            nose_min, nose_max = temp_nose, temp_nose

        nose_min = min(nose_min, temp_nose)
        nose_max = max(nose_max, temp_nose)

        if nose_max - nose_min < 0.01:
            level = 0.5
        else:
            level = 1 - ((temp_nose - nose_min) / (nose_max - nose_min))

        level = max(0, min(1, level))

        cv2.rectangle(frame, (BAR_X, BAR_Y),
                      (BAR_X+BAR_WIDTH, BAR_Y+BAR_HEIGHT),
                      (200,200,200), 2)

        fill_h = int(level * BAR_HEIGHT)

        cv2.rectangle(frame,
                      (BAR_X, BAR_Y+BAR_HEIGHT-fill_h),
                      (BAR_X+BAR_WIDTH, BAR_Y+BAR_HEIGHT),
                      (255, int(255*level), 0), -1)

        cv2.putText(frame, "Breath", (BAR_X-10, BAR_Y-10),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255,255,255), 2)

        # -------- ROI BOXES --------
        cv2.rectangle(frame,(x1,y1),(x1+w1,y1+h1),(255,0,0),2)
        cv2.rectangle(frame,(x2,y2),(x2+w2,y2+h2),(0,255,0),2)

        frame_count += 1

    cv2.imshow("Tracking", frame)

    if cv2.waitKey(1) & 0xFF == 27:
        QtWidgets.QApplication.quit()

# =========================================================
# RUN
# =========================================================
timer = QtCore.QTimer()
timer.timeout.connect(update)
timer.start(20)

QtWidgets.QApplication.instance().exec_()

cap.release()
cv2.destroyAllWindows()