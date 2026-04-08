# import cv2
# import numpy as np
# import pyqtgraph as pg
# from pyqtgraph.Qt import QtWidgets, QtCore

# # =========================================================
# # SETTINGS
# # =========================================================
# THRESHOLD_TEMP = 0.05
# SMOOTH_K = 5
# MAX_POINTS = 200

# # 🔥 BREATH DETECTION SETTINGS
# MIN_AMPLITUDE = 0.05   # ignore small fluctuations
# MIN_TIME_GAP = 1.0     # seconds between peaks

# BAR_X, BAR_Y = 550, 100
# BAR_WIDTH, BAR_HEIGHT = 40, 300

# nose_min, nose_max = None, None

# # =========================================================
# # TIME AXIS
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

# # 🔥 BREATH DETECTION FUNCTION
# def detect_breath_peaks(x, y_smooth):
#     if len(y_smooth) < 3:
#         return []

#     dy = np.diff(y_smooth)
#     peaks = []

#     last_peak_time = -999
#     last_peak_value = None

#     for i in range(1, len(dy)):
#         # detect peak (up -> down)
#         if dy[i-1] > 0 and dy[i] < 0:
#             peak_val = y_smooth[i]
#             peak_time = x[i]

#             # amplitude check
#             if last_peak_value is None or abs(peak_val - last_peak_value) > MIN_AMPLITUDE:
#                 # time gap check
#                 if peak_time - last_peak_time > MIN_TIME_GAP:
#                     peaks.append((peak_time, peak_val))
#                     last_peak_time = peak_time
#                     last_peak_value = peak_val

#     return peaks

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
# curve_raw = p1.plot(pen='y')

# win.nextRow()
# p2 = win.addPlot(axisItems={'bottom': TimeAxisItem(orientation='bottom')}, title="Nose Smooth")
# curve_smooth = p2.plot(pen='g')

# # 🔴 show detected peaks
# scatter_peaks = pg.ScatterPlotItem(pen='r', brush='r', size=8)
# p2.addItem(scatter_peaks)

# win.nextRow()
# p3 = win.addPlot(axisItems={'bottom': TimeAxisItem(orientation='bottom')}, title="Forehead")
# curve_blue = p3.plot(pen='b')
# curve_red = p3.plot(pen='r')

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
#     global x_data, y_nose, y_head

#     ret, frame = cap.read()
#     if not ret:
#         QtWidgets.QApplication.quit()
#         return

#     gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

#     ok1, b1 = tracker_nose.update(frame)
#     ok2, b2 = tracker_head.update(frame)

#     if ok1 and ok2:

#         x1,y1,w1,h1 = map(int, b1)
#         x2,y2,w2,h2 = map(int, b2)

#         temp_nose = get_temp_from_pixel(np.mean(gray[y1:y1+h1, x1:x1+w1]))
#         temp_head = get_temp_from_pixel(np.mean(gray[y2:y2+h2, x2:x2+w2]))

#         # -------- DISPLAY --------
#         cv2.putText(frame, f"Nose: {temp_nose:.2f} C", (50,50),
#                     cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0,255,255), 2)

#         cv2.putText(frame, f"Forehead: {temp_head:.2f} C", (50,90),
#                     cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0,255,0), 2)

#         # -------- TIME --------
#         t = frame_count / fps
#         x_data.append(t)
#         y_nose.append(temp_nose)
#         y_head.append(temp_head)

#         y_smooth = moving_average(y_nose, SMOOTH_K)

#         if len(x_data) > MAX_POINTS:
#             x_data = x_data[-MAX_POINTS:]
#             y_nose = y_nose[-MAX_POINTS:]
#             y_head = y_head[-MAX_POINTS:]
#             y_smooth = y_smooth[-MAX_POINTS:]

#         # -------- GRAPHS --------
#         curve_raw.setData(x_data, y_nose)
#         curve_smooth.setData(x_data, y_smooth)

#         # 🔥 DETECT PEAKS
#         peaks = detect_breath_peaks(x_data, y_smooth)

#         # 🔴 plot peaks
#         if peaks:
#             px, py = zip(*peaks)
#             scatter_peaks.setData(px, py)

#         # 🔥 BPM CALCULATION
#         if len(peaks) >= 2:
#             total_time = x_data[-1] - x_data[0]
#             bpm = (len(peaks) / total_time) * 60
#         else:
#             bpm = 0

#         # 🔥 DISPLAY BPM
#         cv2.putText(frame, f"BPM: {bpm:.2f}", (50,130),
#                     cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0,255,255), 2)

#         # -------- FOREHEAD COLOR LOGIC --------
#         baseline = np.mean(y_head[:20]) if len(y_head) >= 20 else y_head[0]

#         y_blue, y_red = [], []
#         for val in y_head:
#             if val >= baseline + THRESHOLD_TEMP:
#                 y_red.append(val)
#                 y_blue.append(np.nan)
#             else:
#                 y_blue.append(val)
#                 y_red.append(np.nan)

#         curve_blue.setData(x_data, y_blue)
#         curve_red.setData(x_data, y_red)

#         # -------- BREATH BAR --------
#         if nose_min is None:
#             nose_min, nose_max = temp_nose, temp_nose

#         nose_min = min(nose_min, temp_nose)
#         nose_max = max(nose_max, temp_nose)

#         if nose_max - nose_min < 0.01:
#             level = 0.5
#         else:
#             level = 1 - ((temp_nose - nose_min) / (nose_max - nose_min))

#         level = max(0, min(1, level))

#         cv2.rectangle(frame, (BAR_X, BAR_Y),
#                       (BAR_X+BAR_WIDTH, BAR_Y+BAR_HEIGHT),
#                       (200,200,200), 2)

#         fill_h = int(level * BAR_HEIGHT)

#         cv2.rectangle(frame,
#                       (BAR_X, BAR_Y+BAR_HEIGHT-fill_h),
#                       (BAR_X+BAR_WIDTH, BAR_Y+BAR_HEIGHT),
#                       (255, int(255*level), 0), -1)

#         cv2.putText(frame, "Breath", (BAR_X-10, BAR_Y-10),
#                     cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255,255,255), 2)

#         # -------- ROI BOXES --------
#         cv2.rectangle(frame,(x1,y1),(x1+w1,y1+h1),(255,0,0),2)
#         cv2.rectangle(frame,(x2,y2),(x2+w2,y2+h2),(0,255,0),2)

#         frame_count += 1

#     cv2.imshow("Tracking", frame)

#     if cv2.waitKey(1) & 0xFF == 27:
#         QtWidgets.QApplication.quit()

# # =========================================================
# # RUN
# # =========================================================
# timer = QtCore.QTimer()
# timer.timeout.connect(update)
# timer.start(20)

# QtWidgets.QApplication.instance().exec_()

# cap.release()
# cv2.destroyAllWindows()

##############################################################################



# import cv2
# import numpy as np
# import pyqtgraph as pg
# from pyqtgraph.Qt import QtWidgets, QtCore

# # =========================================================
# # SETTINGS
# # =========================================================
# THRESHOLD_TEMP = 0.05
# SMOOTH_K = 7
# MAX_POINTS = 200

# # 🔥 BREATH DETECTION SETTINGS
# MIN_AMPLITUDE = 0.1   # increased to remove double peaks
# MIN_TIME_GAP = 1.2     # seconds

# BAR_X, BAR_Y = 550, 100
# BAR_WIDTH, BAR_HEIGHT = 40, 300

# nose_min, nose_max = None, None

# # =========================================================
# # TIME AXIS
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
# # 🔥 STATE-BASED BREATH DETECTION
# # =========================================================
# def detect_breath_peaks(x, y_smooth):
#     if len(y_smooth) < 3:
#         return []

#     dy = np.diff(y_smooth)

#     peaks = []

#     state = "looking_for_peak"
#     last_peak = None
#     last_valley = None
#     last_time = -999

#     for i in range(1, len(dy)):

#         val = y_smooth[i]
#         time = x[i]

#         # -------- PEAK --------
#         if dy[i-1] > 0 and dy[i] < 0:

#             if state == "looking_for_peak":

#                 if last_valley is None or abs(val - last_valley) > MIN_AMPLITUDE:

#                     if time - last_time > MIN_TIME_GAP:
#                         peaks.append((time, val))

#                         last_peak = val
#                         last_time = time
#                         state = "looking_for_valley"

#         # -------- VALLEY --------
#         elif dy[i-1] < 0 and dy[i] > 0:

#             if state == "looking_for_valley":

#         # 🔥 STRICT VALLEY CONDITION
#                 if last_peak is not None:
#                     if abs(val - last_peak) < MIN_AMPLITUDE:
#                         continue

#                 last_valley = val
#                 last_time = time
#                 state = "looking_for_peak"

#     return peaks

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
# curve_raw = p1.plot(pen='y')

# win.nextRow()
# p2 = win.addPlot(axisItems={'bottom': TimeAxisItem(orientation='bottom')}, title="Nose Smooth")
# curve_smooth = p2.plot(pen='g')

# # 🔴 peak markers
# scatter_peaks = pg.ScatterPlotItem(pen='r', brush='r', size=8)
# p2.addItem(scatter_peaks)

# win.nextRow()
# p3 = win.addPlot(axisItems={'bottom': TimeAxisItem(orientation='bottom')}, title="Forehead")
# curve_blue = p3.plot(pen='b')
# curve_red = p3.plot(pen='r')

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
#     global x_data, y_nose, y_head

#     ret, frame = cap.read()
#     if not ret:
#         QtWidgets.QApplication.quit()
#         return

#     gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

#     ok1, b1 = tracker_nose.update(frame)
#     ok2, b2 = tracker_head.update(frame)

#     if ok1 and ok2:

#         x1,y1,w1,h1 = map(int, b1)
#         x2,y2,w2,h2 = map(int, b2)

#         temp_nose = get_temp_from_pixel(np.mean(gray[y1:y1+h1, x1:x1+w1]))
#         temp_head = get_temp_from_pixel(np.mean(gray[y2:y2+h2, x2:x2+w2]))

#         # -------- DISPLAY --------
#         cv2.putText(frame, f"Nose: {temp_nose:.2f} C", (50,50),
#                     cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0,255,255), 2)

#         cv2.putText(frame, f"Forehead: {temp_head:.2f} C", (50,90),
#                     cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0,255,0), 2)

#         # -------- TIME --------
#         t = frame_count / fps
#         x_data.append(t)
#         y_nose.append(temp_nose)
#         y_head.append(temp_head)

#         y_smooth = moving_average(y_nose, SMOOTH_K)

#         if len(x_data) > MAX_POINTS:
#             x_data = x_data[-MAX_POINTS:]
#             y_nose = y_nose[-MAX_POINTS:]
#             y_head = y_head[-MAX_POINTS:]
#             y_smooth = y_smooth[-MAX_POINTS:]

#         # -------- GRAPHS --------
#         curve_raw.setData(x_data, y_nose)
#         curve_smooth.setData(x_data, y_smooth)

#         # 🔥 DETECT PEAKS (FIXED)
#         peaks = detect_breath_peaks(x_data, y_smooth)

#         if peaks:
#             px, py = zip(*peaks)
#             scatter_peaks.setData(px, py)

#         # 🔥 BPM
#         if len(peaks) >= 2:
#             total_time = x_data[-1] - x_data[0]
#             bpm = (len(peaks) / total_time) * 60
#         else:
#             bpm = 0

#         cv2.putText(frame, f"BPM: {bpm:.2f}", (50,130),
#                     cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0,255,255), 2)

#         # -------- FOREHEAD --------
#         baseline = np.mean(y_head[:20]) if len(y_head) >= 20 else y_head[0]

#         y_blue, y_red = [], []
#         for val in y_head:
#             if val >= baseline + THRESHOLD_TEMP:
#                 y_red.append(val)
#                 y_blue.append(np.nan)
#             else:
#                 y_blue.append(val)
#                 y_red.append(np.nan)

#         curve_blue.setData(x_data, y_blue)
#         curve_red.setData(x_data, y_red)

#         # -------- BREATH BAR --------
#         if nose_min is None:
#             nose_min, nose_max = temp_nose, temp_nose

#         nose_min = min(nose_min, temp_nose)
#         nose_max = max(nose_max, temp_nose)

#         if nose_max - nose_min < 0.01:
#             level = 0.5
#         else:
#             level = 1 - ((temp_nose - nose_min) / (nose_max - nose_min))

#         level = max(0, min(1, level))

#         cv2.rectangle(frame, (BAR_X, BAR_Y),
#                       (BAR_X+BAR_WIDTH, BAR_Y+BAR_HEIGHT),
#                       (200,200,200), 2)

#         fill_h = int(level * BAR_HEIGHT)

#         cv2.rectangle(frame,
#                       (BAR_X, BAR_Y+BAR_HEIGHT-fill_h),
#                       (BAR_X+BAR_WIDTH, BAR_Y+BAR_HEIGHT),
#                       (255, int(255*level), 0), -1)

#         cv2.putText(frame, "Breath", (BAR_X-10, BAR_Y-10),
#                     cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255,255,255), 2)

#         # -------- ROI BOXES --------
#         cv2.rectangle(frame,(x1,y1),(x1+w1,y1+h1),(255,0,0),2)
#         cv2.rectangle(frame,(x2,y2),(x2+w2,y2+h2),(0,255,0),2)

#         frame_count += 1

#     cv2.imshow("Tracking", frame)

#     if cv2.waitKey(1) & 0xFF == 27:
#         QtWidgets.QApplication.quit()

# # =========================================================
# # RUN
# # =========================================================
# timer = QtCore.QTimer()
# timer.timeout.connect(update)
# timer.start(20)

# QtWidgets.QApplication.instance().exec_()

# cap.release()
# cv2.destroyAllWindows()

########################################
#getting doublepeak probelm

# import cv2
# import numpy as np
# import pyqtgraph as pg
# from pyqtgraph.Qt import QtWidgets, QtCore

# # =========================================================
# # SETTINGS
# # =========================================================
# THRESHOLD_TEMP = 0.05
# SMOOTH_K = 7
# MAX_POINTS = 200

# # 🔥 BREATH DETECTION (FINAL FIX)
# REFRACTORY_PERIOD = 2.0   # seconds (NO second peak allowed in this window)

# BAR_X, BAR_Y = 550, 100
# BAR_WIDTH, BAR_HEIGHT = 40, 300

# nose_min, nose_max = None, None

# # =========================================================
# # TIME AXIS
# # =========================================================
# class TimeAxisItem(pg.AxisItem):
#     def tickStrings(self, values, scale, spacing):
#         return [f"{int(v//60):02d}:{int(v%60):02d}" for v in values]

# # =========================================================
# # FUNCTIONS
# # =========================================================
# def get_temp_from_pixel(p):
#     return 0.05891454 * p + 30.07676744

# def moving_average(signal, k=7):
#     if len(signal) < k:
#         return signal
#     smooth = np.convolve(signal, np.ones(k)/k, mode='valid')
#     pad_left = [smooth[0]] * (k//2)
#     pad_right = [smooth[-1]] * (k//2)
#     return list(np.concatenate([pad_left, smooth, pad_right]))

# # =========================================================
# # 🔥 FINAL BREATH DETECTION (REFRACTORY METHOD)
# # =========================================================
# def detect_breath_peaks(x, y_smooth):
#     if len(y_smooth) < 3:
#         return []

#     dy = np.diff(y_smooth)
#     peaks = []

#     last_peak_time = -999

#     for i in range(1, len(dy)):

#         # basic peak condition
#         if dy[i-1] > 0 and dy[i] < 0:

#             time = x[i]
#             val = y_smooth[i]

#             # 🔥 KEY FIX: BLOCK CLOSE PEAKS
#             if time - last_peak_time < REFRACTORY_PERIOD:
#                 continue

#             peaks.append((time, val))
#             last_peak_time = time

#     return peaks

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
# curve_raw = p1.plot(pen='y')

# win.nextRow()
# p2 = win.addPlot(axisItems={'bottom': TimeAxisItem(orientation='bottom')}, title="Nose Smooth")
# curve_smooth = p2.plot(pen='g')

# # 🔴 peaks
# scatter_peaks = pg.ScatterPlotItem(pen='r', brush='r', size=8)
# p2.addItem(scatter_peaks)

# win.nextRow()
# p3 = win.addPlot(axisItems={'bottom': TimeAxisItem(orientation='bottom')}, title="Forehead")
# curve_blue = p3.plot(pen='b')
# curve_red = p3.plot(pen='r')

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
#     global x_data, y_nose, y_head

#     ret, frame = cap.read()
#     if not ret:
#         QtWidgets.QApplication.quit()
#         return

#     gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

#     ok1, b1 = tracker_nose.update(frame)
#     ok2, b2 = tracker_head.update(frame)

#     if ok1 and ok2:

#         x1,y1,w1,h1 = map(int, b1)
#         x2,y2,w2,h2 = map(int, b2)

#         temp_nose = get_temp_from_pixel(np.mean(gray[y1:y1+h1, x1:x1+w1]))
#         temp_head = get_temp_from_pixel(np.mean(gray[y2:y2+h2, x2:x2+w2]))

#         # -------- TEXT --------
#         cv2.putText(frame, f"Nose: {temp_nose:.2f} C", (50,50),
#                     cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0,255,255), 2)

#         cv2.putText(frame, f"Forehead: {temp_head:.2f} C", (50,90),
#                     cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0,255,0), 2)

#         # -------- TIME --------
#         t = frame_count / fps
#         x_data.append(t)
#         y_nose.append(temp_nose)
#         y_head.append(temp_head)

#         y_smooth = moving_average(y_nose, SMOOTH_K)

#         if len(x_data) > MAX_POINTS:
#             x_data = x_data[-MAX_POINTS:]
#             y_nose = y_nose[-MAX_POINTS:]
#             y_head = y_head[-MAX_POINTS:]
#             y_smooth = y_smooth[-MAX_POINTS:]

#         # -------- PLOTS --------
#         curve_raw.setData(x_data, y_nose)
#         curve_smooth.setData(x_data, y_smooth)

#         # 🔥 DETECT PEAKS
#         peaks = detect_breath_peaks(x_data, y_smooth)

#         if peaks:
#             px, py = zip(*peaks)
#             scatter_peaks.setData(px, py)

#         # -------- BPM --------
#         if len(peaks) >= 2:
#             total_time = x_data[-1] - x_data[0]
#             bpm = (len(peaks) / total_time) * 60
#         else:
#             bpm = 0

#         cv2.putText(frame, f"BPM: {bpm:.2f}", (50,130),
#                     cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0,255,255), 2)

#         # -------- FOREHEAD --------
#         baseline = np.mean(y_head[:20]) if len(y_head) >= 20 else y_head[0]

#         y_blue, y_red = [], []
#         for val in y_head:
#             if val >= baseline + THRESHOLD_TEMP:
#                 y_red.append(val)
#                 y_blue.append(np.nan)
#             else:
#                 y_blue.append(val)
#                 y_red.append(np.nan)

#         curve_blue.setData(x_data, y_blue)
#         curve_red.setData(x_data, y_red)

#         # -------- BREATH BAR --------
#         if nose_min is None:
#             nose_min, nose_max = temp_nose, temp_nose

#         nose_min = min(nose_min, temp_nose)
#         nose_max = max(nose_max, temp_nose)

#         if nose_max - nose_min < 0.01:
#             level = 0.5
#         else:
#             level = 1 - ((temp_nose - nose_min) / (nose_max - nose_min))

#         level = max(0, min(1, level))

#         cv2.rectangle(frame, (BAR_X, BAR_Y),
#                       (BAR_X+BAR_WIDTH, BAR_Y+BAR_HEIGHT),
#                       (200,200,200), 2)

#         fill_h = int(level * BAR_HEIGHT)

#         cv2.rectangle(frame,
#                       (BAR_X, BAR_Y+BAR_HEIGHT-fill_h),
#                       (BAR_X+BAR_WIDTH, BAR_Y+BAR_HEIGHT),
#                       (255, int(255*level), 0), -1)

#         cv2.putText(frame, "Breath", (BAR_X-10, BAR_Y-10),
#                     cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255,255,255), 2)

#         # -------- ROI BOXES --------
#         cv2.rectangle(frame,(x1,y1),(x1+w1,y1+h1),(255,0,0),2)
#         cv2.rectangle(frame,(x2,y2),(x2+w2,y2+h2),(0,255,0),2)

#         frame_count += 1

#     cv2.imshow("Tracking", frame)

#     if cv2.waitKey(1) & 0xFF == 27:
#         QtWidgets.QApplication.quit()

# # =========================================================
# # RUN
# # =========================================================
# timer = QtCore.QTimer()
# timer.timeout.connect(update)
# timer.start(20)

# QtWidgets.QApplication.instance().exec_()

# cap.release()
# cv2.destroyAllWindows()

######################################################
# IMPROVED FINAL BREATH DETECTION (REFRACTORY METHOD) FROM CLAUDE
# import cv2
# import numpy as np
# import pyqtgraph as pg
# from pyqtgraph.Qt import QtWidgets, QtCore
 
# # =========================================================
# # SETTINGS
# # =========================================================
# THRESHOLD_TEMP   = 0.05
# SMOOTH_K         = 7
# MAX_POINTS       = 200
 
# # 🔥 BREATH DETECTION
# MIN_PEAK_VALLEY_DIFF = 0.03   # minimum temp drop after a peak to count as real breath
# REFRACTORY_PERIOD    = 2.0    # seconds — minimum gap between two counted breaths
 
# BAR_X, BAR_Y   = 550, 100
# BAR_WIDTH, BAR_HEIGHT = 40, 300
 
# nose_min, nose_max = None, None
 
# # =========================================================
# # TIME AXIS
# # =========================================================
# class TimeAxisItem(pg.AxisItem):
#     def tickStrings(self, values, scale, spacing):
#         return [f"{int(v//60):02d}:{int(v%60):02d}" for v in values]
 
# # =========================================================
# # FUNCTIONS
# # =========================================================
# def get_temp_from_pixel(p):
#     return 0.05891454 * p + 30.07676744
 
# def moving_average(signal, k=7):
#     if len(signal) < k:
#         return signal
#     smooth = np.convolve(signal, np.ones(k)/k, mode='valid')
#     pad_left  = [smooth[0]] * (k // 2)
#     pad_right = [smooth[-1]] * (k // 2)
#     return list(np.concatenate([pad_left, smooth, pad_right]))
 
# # =========================================================
# # 🔥 BREATH DETECTION — PEAK + VALLEY CYCLE METHOD
# #
# #   A breath is only counted when:
# #     1. A local peak is found
# #     2. A valley follows the peak with a drop >= MIN_PEAK_VALLEY_DIFF
# #     3. The peak is at least REFRACTORY_PERIOD seconds after the last counted breath
# #
# #   This prevents:
# #     - Double-counting consecutive peaks (no valley between them)
# #     - Counting small wiggles as breaths
# # =========================================================
# def detect_breath_peaks(x, y_smooth):
#     if len(y_smooth) < 5:
#         return []
 
#     y  = np.array(y_smooth)
#     dy = np.diff(y)
 
#     raw_peaks   = []
#     raw_valleys = []
 
#     # collect ALL local peaks and valleys
#     for i in range(1, len(dy)):
#         if dy[i-1] > 0 and dy[i] <= 0:
#             raw_peaks.append(i)       # local peak index
#         elif dy[i-1] < 0 and dy[i] >= 0:
#             raw_valleys.append(i)     # local valley index
 
#     if not raw_peaks or not raw_valleys:
#         return []
 
#     # match each peak → its next valley → one breath cycle
#     breath_markers  = []   # list of (time, value) for confirmed breath peaks
#     last_cycle_time = -999
#     used_valleys    = set()
 
#     for pi in raw_peaks:
#         # find the first unused valley that comes AFTER this peak
#         next_valleys = [vi for vi in raw_valleys if vi > pi and vi not in used_valleys]
#         if not next_valleys:
#             continue
 
#         vi = next_valleys[0]
 
#         peak_val   = y[pi]
#         valley_val = y[vi]
 
#         # must have a meaningful temperature drop to count
#         if peak_val - valley_val < MIN_PEAK_VALLEY_DIFF:
#             continue
 
#         # refractory guard — no two breaths counted too close in time
#         t_peak = x[pi]
#         if t_peak - last_cycle_time < REFRACTORY_PERIOD:
#             continue
 
#         breath_markers.append((t_peak, peak_val))
#         used_valleys.add(vi)
#         last_cycle_time = t_peak
 
#     return breath_markers
 
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
# win.setWindowTitle("Breath Monitor")
 
# p1 = win.addPlot(axisItems={'bottom': TimeAxisItem(orientation='bottom')}, title="Nose Raw")
# curve_raw = p1.plot(pen='y')
 
# win.nextRow()
# p2 = win.addPlot(axisItems={'bottom': TimeAxisItem(orientation='bottom')}, title="Nose Smooth  |  🔴 = confirmed breath cycle")
# curve_smooth = p2.plot(pen='g')
 
# # red dots — only on confirmed breath cycles
# scatter_peaks = pg.ScatterPlotItem(pen=pg.mkPen('r', width=2), brush='r', size=10)
# p2.addItem(scatter_peaks)
 
# # BPM text label on the smooth plot
# bpm_label = pg.TextItem(text="BPM: --", color='w', anchor=(0, 0))
# bpm_label.setPos(0, 0)
# p2.addItem(bpm_label)
 
# win.nextRow()
# p3 = win.addPlot(axisItems={'bottom': TimeAxisItem(orientation='bottom')}, title="Forehead")
# curve_blue = p3.plot(pen='b')
# curve_red  = p3.plot(pen='r')
 
# # =========================================================
# # DATA
# # =========================================================
# x_data, y_nose, y_head = [], [], []
# frame_count = 0
 
# # =========================================================
# # MAIN LOOP
# # =========================================================
# def update():
#     global frame_count, nose_min, nose_max
#     global x_data, y_nose, y_head
 
#     ret, frame = cap.read()
#     if not ret:
#         QtWidgets.QApplication.quit()
#         return
 
#     gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
 
#     ok1, b1 = tracker_nose.update(frame)
#     ok2, b2 = tracker_head.update(frame)
 
#     if ok1 and ok2:
 
#         x1, y1, w1, h1 = map(int, b1)
#         x2, y2, w2, h2 = map(int, b2)
 
#         temp_nose = get_temp_from_pixel(np.mean(gray[y1:y1+h1, x1:x1+w1]))
#         temp_head = get_temp_from_pixel(np.mean(gray[y2:y2+h2, x2:x2+w2]))
 
#         # -------- TEXT on frame --------
#         cv2.putText(frame, f"Nose: {temp_nose:.2f} C",      (50, 50),
#                     cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 255), 2)
#         cv2.putText(frame, f"Forehead: {temp_head:.2f} C",  (50, 90),
#                     cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0),   2)
 
#         # -------- TIME --------
#         t = frame_count / fps
#         x_data.append(t)
#         y_nose.append(temp_nose)
#         y_head.append(temp_head)
 
#         y_smooth = moving_average(y_nose, SMOOTH_K)
 
#         if len(x_data) > MAX_POINTS:
#             x_data   = x_data[-MAX_POINTS:]
#             y_nose   = y_nose[-MAX_POINTS:]
#             y_head   = y_head[-MAX_POINTS:]
#             y_smooth = y_smooth[-MAX_POINTS:]
 
#         # -------- PLOTS --------
#         curve_raw.setData(x_data, y_nose)
#         curve_smooth.setData(x_data, y_smooth)
 
#         # -------- 🔥 DETECT BREATHS (peak + valley cycle) --------
#         peaks = detect_breath_peaks(x_data, y_smooth)
 
#         if peaks:
#             px, py = zip(*peaks)
#             scatter_peaks.setData(list(px), list(py))
#         else:
#             scatter_peaks.setData([], [])
 
#         # -------- BPM --------
#         if len(peaks) >= 2:
#             total_time = x_data[-1] - x_data[0]
#             bpm = (len(peaks) / total_time) * 60
#         else:
#             bpm = 0
 
#         bpm_label.setText(f"BPM: {bpm:.1f}")
#         if len(x_data) > 0:
#             bpm_label.setPos(x_data[0], max(y_smooth) if y_smooth else 0)
 
#         cv2.putText(frame, f"BPM: {bpm:.1f}", (50, 130),
#                     cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 255), 2)
 
#         # -------- FOREHEAD --------
#         baseline = np.mean(y_head[:20]) if len(y_head) >= 20 else y_head[0]
 
#         y_blue, y_red = [], []
#         for val in y_head:
#             if val >= baseline + THRESHOLD_TEMP:
#                 y_red.append(val)
#                 y_blue.append(np.nan)
#             else:
#                 y_blue.append(val)
#                 y_red.append(np.nan)
 
#         curve_blue.setData(x_data, y_blue)
#         curve_red.setData(x_data, y_red)
 
#         # -------- BREATH BAR --------
#         if nose_min is None:
#             nose_min, nose_max = temp_nose, temp_nose
#         # update globals
#         globals()['nose_min'] = min(nose_min, temp_nose)
#         globals()['nose_max'] = max(nose_max, temp_nose)
 
#         if nose_max - nose_min < 0.01:
#             level = 0.5
#         else:
#             level = 1 - ((temp_nose - nose_min) / (nose_max - nose_min))
#         level = max(0.0, min(1.0, level))
 
#         cv2.rectangle(frame,
#                       (BAR_X, BAR_Y),
#                       (BAR_X + BAR_WIDTH, BAR_Y + BAR_HEIGHT),
#                       (200, 200, 200), 2)
 
#         fill_h = int(level * BAR_HEIGHT)
#         cv2.rectangle(frame,
#                       (BAR_X, BAR_Y + BAR_HEIGHT - fill_h),
#                       (BAR_X + BAR_WIDTH, BAR_Y + BAR_HEIGHT),
#                       (255, int(255 * level), 0), -1)
 
#         cv2.putText(frame, "Breath", (BAR_X - 10, BAR_Y - 10),
#                     cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2)
 
#         # -------- ROI BOXES --------
#         cv2.rectangle(frame, (x1, y1), (x1+w1, y1+h1), (255, 0,   0), 2)
#         cv2.rectangle(frame, (x2, y2), (x2+w2, y2+h2), (0,   255, 0), 2)
 
#         frame_count += 1
 
#     cv2.imshow("Tracking", frame)
 
#     if cv2.waitKey(1) & 0xFF == 27:   # ESC to quit
#         QtWidgets.QApplication.quit()
 
# # =========================================================
# # RUN
# # =========================================================
# timer = QtCore.QTimer()
# timer.timeout.connect(update)
# timer.start(20)
 
# QtWidgets.QApplication.instance().exec_()
 
# cap.release()
# cv2.destroyAllWindows()

#########################################################################


import cv2
import numpy as np
import pyqtgraph as pg
from pyqtgraph.Qt import QtWidgets, QtCore

# =========================================================
# ⚙️  TUNING PARAMETERS — adjust these to calibrate
# =========================================================

# --- Smoothing ---
SMOOTH_K_NOSE     = 7     # moving average window for NOSE signal (higher = smoother, more lag)
SMOOTH_K_FOREHEAD = 11    # moving average window for FOREHEAD signal (higher = smoother, more lag)
                          # tip: forehead benefits from more smoothing (more noise from skin)

# --- Breath Detection ---
MIN_PEAK_VALLEY_DIFF = 0.08   # 🔥 minimum temp drop (°C) after a peak to count as a real breath
                               # raise → fewer dots (ignore small wiggles)
                               # lower → more dots (catch shallow breaths)

REFRACTORY_PERIOD    = 2.0    # minimum seconds between two counted breaths
                               # raise → cap max detectable BPM (2.0s = 30 BPM max)
                               # lower → allow faster breathing detection

# --- Stress Detection (Forehead) ---
STRESS_BASELINE_FRAMES = 20   # how many frames to average for the baseline temperature
                               # more frames = more stable baseline, but slower to adapt

STRESS_THRESHOLD = 0.05       # 🔥 temperature rise (°C) above baseline = stress/elevated state
                               # raise → only flag strong temperature spikes as stress
                               # lower → more sensitive, flags subtle rises

# --- Display ---
MAX_POINTS   = 200            # number of data points shown on the rolling graph window
BAR_X, BAR_Y = 550, 100
BAR_WIDTH, BAR_HEIGHT = 40, 300

# =========================================================
# STATE — do not modify
# =========================================================
nose_min, nose_max = None, None

# =========================================================
# TIME AXIS — shows MM:SS on x-axis
# =========================================================
class TimeAxisItem(pg.AxisItem):
    def tickStrings(self, values, scale, spacing):
        return [f"{int(v//60):02d}:{int(v%60):02d}" for v in values]

# =========================================================
# UTILITY FUNCTIONS
# =========================================================

def get_temp_from_pixel(pixel_value):
    """
    Convert grayscale pixel intensity → temperature (°C).
    Calibration formula: T = 0.05891454 * pixel + 30.07676744
    Adjust these coefficients to match your thermal camera calibration.
    """
    return 0.05891454 * pixel_value + 30.07676744


def moving_average(signal, k=7):
    """
    Smooth a signal using a centered moving average of window size k.
    Edges are padded by repeating the first/last smoothed value.
    Larger k = smoother curve but introduces more lag.
    """
    if len(signal) < k:
        return signal
    smooth    = np.convolve(signal, np.ones(k) / k, mode='valid')
    pad_left  = [smooth[0]]  * (k // 2)
    pad_right = [smooth[-1]] * (k // 2)
    return list(np.concatenate([pad_left, smooth, pad_right]))


# =========================================================
# 🔥 BREATH DETECTION — peak + valley cycle method
#
#  A breath is counted ONLY when ALL 3 conditions are met:
#    1. A local peak exists (temp rises then falls)
#    2. A valley follows the peak with drop >= MIN_PEAK_VALLEY_DIFF
#       → filters out small noise bumps
#    3. At least REFRACTORY_PERIOD seconds since last counted breath
#       → prevents double-counting one breath as two
#
#  Returns: list of (time, value) tuples for confirmed breath peaks
# =========================================================
def detect_breath_peaks(x, y_smooth):
    if len(y_smooth) < 5:
        return []

    y  = np.array(y_smooth)
    dy = np.diff(y)

    raw_peaks   = []
    raw_valleys = []

    # find ALL local peaks (rise→fall) and valleys (fall→rise)
    for i in range(1, len(dy)):
        if dy[i-1] > 0 and dy[i] <= 0:
            raw_peaks.append(i)
        elif dy[i-1] < 0 and dy[i] >= 0:
            raw_valleys.append(i)

    if not raw_peaks or not raw_valleys:
        return []

    breath_markers  = []
    last_cycle_time = -999
    used_valleys    = set()

    for pi in raw_peaks:
        # find first unused valley after this peak
        next_valleys = [vi for vi in raw_valleys if vi > pi and vi not in used_valleys]
        if not next_valleys:
            continue

        vi = next_valleys[0]

        peak_val   = y[pi]
        valley_val = y[vi]

        # condition 2: meaningful drop required
        if peak_val - valley_val < MIN_PEAK_VALLEY_DIFF:
            continue

        # condition 3: refractory period
        t_peak = x[pi]
        if t_peak - last_cycle_time < REFRACTORY_PERIOD:
            continue

        breath_markers.append((t_peak, peak_val))
        used_valleys.add(vi)
        last_cycle_time = t_peak

    return breath_markers


# =========================================================
# VIDEO — open and select ROIs
# =========================================================
cap = cv2.VideoCapture(r"C:\Users\Akash Vishwakarma\Downloads\krishna_grey_manual1.mp4")
fps = cap.get(cv2.CAP_PROP_FPS)

ret, frame = cap.read()
if not ret:
    print("ERROR: Could not read video file.")
    exit()

print("Draw a box around the NOSE, then press ENTER or SPACE")
bbox_nose = cv2.selectROI("Nose ROI", frame, False)
cv2.destroyWindow("Nose ROI")

print("Draw a box around the FOREHEAD, then press ENTER or SPACE")
bbox_head = cv2.selectROI("Forehead ROI", frame, False)
cv2.destroyWindow("Forehead ROI")

# CSRT tracker — accurate but slower; swap to KCF if lag is too high
tracker_nose = cv2.TrackerCSRT_create()
tracker_head = cv2.TrackerCSRT_create()
tracker_nose.init(frame, bbox_nose)
tracker_head.init(frame, bbox_head)

# =========================================================
# PYQTGRAPH UI — 3 rows of plots
# =========================================================
app = QtWidgets.QApplication([])
win = pg.GraphicsLayoutWidget(show=True)
win.resize(1000, 900)
win.setWindowTitle("Breath & Stress Monitor")

# --- Row 1: Nose Raw ---
p1 = win.addPlot(
    axisItems={'bottom': TimeAxisItem(orientation='bottom')},
    title="Nose — Raw Temperature"
)
p1.setLabel('left',   'Temp (°C)')
p1.setLabel('bottom', 'Time')
curve_nose_raw = p1.plot(pen=pg.mkPen('y', width=1))

# --- Row 2: Nose Smooth + breath peaks ---
win.nextRow()
p2 = win.addPlot(
    axisItems={'bottom': TimeAxisItem(orientation='bottom')},
    title="Nose — Smoothed  |  🔴 = confirmed breath (exhale peak)"
)
p2.setLabel('left',   'Temp (°C)')
p2.setLabel('bottom', 'Time')
curve_nose_smooth = p2.plot(pen=pg.mkPen('g', width=2))

# red dots on confirmed breath peaks
scatter_peaks = pg.ScatterPlotItem(
    pen=pg.mkPen('r', width=2), brush='r', size=10
)
p2.addItem(scatter_peaks)

# floating BPM label on the plot
bpm_label = pg.TextItem(text="BPM: --", color=(255, 255, 0), anchor=(0, 1))
p2.addItem(bpm_label)

# --- Row 3: Forehead Smooth — blue=normal, red=elevated (stress) ---
win.nextRow()
p3 = win.addPlot(
    axisItems={'bottom': TimeAxisItem(orientation='bottom')},
    title=f"Forehead — Smoothed  |  🔵 normal  🔴 elevated (STRESS_THRESHOLD = {STRESS_THRESHOLD}°C above baseline)"
)
p3.setLabel('left',   'Temp (°C)')
p3.setLabel('bottom', 'Time')

# blue = within normal range
curve_forehead_normal = p3.plot(pen=pg.mkPen('b', width=2))
# red = above stress threshold
curve_forehead_stress = p3.plot(pen=pg.mkPen('r', width=2))

# dashed baseline reference line
baseline_line = pg.InfiniteLine(
    angle=0, movable=False,
    pen=pg.mkPen(color=(150, 150, 150), style=QtCore.Qt.DashLine)
)
p3.addItem(baseline_line)

# stress label
stress_label = pg.TextItem(text="", color=(255, 80, 80), anchor=(0, 1))
p3.addItem(stress_label)

# =========================================================
# DATA BUFFERS
# =========================================================
x_data = []   # time in seconds
y_nose = []   # raw nose temperatures
y_head = []   # raw forehead temperatures
frame_count = 0

# =========================================================
# MAIN UPDATE LOOP — called every 20 ms by QTimer
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

    if not (ok1 and ok2):
        cv2.imshow("Tracking", frame)
        cv2.waitKey(1)
        return

    # ---- extract ROI pixel means → temperatures ----
    x1, y1, w1, h1 = map(int, b1)
    x2, y2, w2, h2 = map(int, b2)

    temp_nose = get_temp_from_pixel(np.mean(gray[y1:y1+h1, x1:x1+w1]))
    temp_head = get_temp_from_pixel(np.mean(gray[y2:y2+h2, x2:x2+w2]))

    # ---- overlay temperatures on video frame ----
    cv2.putText(frame, f"Nose:     {temp_nose:.2f} C", (50,  50),
                cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 255), 2)
    cv2.putText(frame, f"Forehead: {temp_head:.2f} C", (50,  90),
                cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255,   0), 2)

    # ---- append to rolling buffers ----
    t = frame_count / fps
    x_data.append(t)
    y_nose.append(temp_nose)
    y_head.append(temp_head)

    # ---- smooth both signals ----
    y_nose_smooth = moving_average(y_nose, SMOOTH_K_NOSE)
    y_head_smooth = moving_average(y_head, SMOOTH_K_FOREHEAD)

    # ---- trim to MAX_POINTS rolling window ----
    if len(x_data) > MAX_POINTS:
        x_data        = x_data[-MAX_POINTS:]
        y_nose        = y_nose[-MAX_POINTS:]
        y_head        = y_head[-MAX_POINTS:]
        y_nose_smooth = y_nose_smooth[-MAX_POINTS:]
        y_head_smooth = y_head_smooth[-MAX_POINTS:]

    # =====================================================
    # PLOT 1 — Nose Raw
    # =====================================================
    curve_nose_raw.setData(x_data, y_nose)

    # =====================================================
    # PLOT 2 — Nose Smooth + Breath Detection
    # =====================================================
    curve_nose_smooth.setData(x_data, y_nose_smooth)

    peaks = detect_breath_peaks(x_data, y_nose_smooth)

    if peaks:
        px, py = zip(*peaks)
        scatter_peaks.setData(list(px), list(py))
    else:
        scatter_peaks.setData([], [])

    # ---- BPM calculation ----
    if len(peaks) >= 2:
        total_time = x_data[-1] - x_data[0]
        bpm = (len(peaks) / total_time) * 60 if total_time > 0 else 0
    else:
        bpm = 0

    bpm_text = f"BPM: {bpm:.1f}"
    bpm_label.setText(bpm_text)
    if x_data and y_nose_smooth:
        bpm_label.setPos(x_data[0], min(y_nose_smooth))

    cv2.putText(frame, bpm_text, (50, 130),
                cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 255), 2)

    # =====================================================
    # PLOT 3 — Forehead Smoothed (stress detection)
    #
    # baseline = mean of first STRESS_BASELINE_FRAMES smoothed values
    # if smoothed temp > baseline + STRESS_THRESHOLD → red (elevated/stress)
    # otherwise → blue (normal)
    #
    # To tune:
    #   raise STRESS_THRESHOLD → only flag obvious spikes
    #   lower STRESS_THRESHOLD → more sensitive to subtle rises
    # =====================================================
    if len(y_head_smooth) >= STRESS_BASELINE_FRAMES:
        baseline = np.mean(y_head_smooth[:STRESS_BASELINE_FRAMES])
    else:
        baseline = y_head_smooth[0] if y_head_smooth else temp_head

    # update baseline reference line position
    baseline_line.setValue(baseline + STRESS_THRESHOLD)

    y_normal = []
    y_stress = []
    stress_now = False

    for val in y_head_smooth:
        if val >= baseline + STRESS_THRESHOLD:
            # elevated — potential stress
            y_stress.append(val)
            y_normal.append(np.nan)
            stress_now = True
        else:
            y_normal.append(val)
            y_stress.append(np.nan)

    curve_forehead_normal.setData(x_data, y_normal)
    curve_forehead_stress.setData(x_data, y_stress)

    # update stress label and video overlay
    if stress_now:
        stress_label.setText(f"⚠ ELEVATED  (+{STRESS_THRESHOLD}°C above baseline {baseline:.2f}°C)")
        if x_data and y_head_smooth:
            stress_label.setPos(x_data[0], min(y_head_smooth))
        cv2.putText(frame, "FOREHEAD: ELEVATED", (50, 170),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)
    else:
        stress_label.setText("")

    # =====================================================
    # BREATH BAR — visual breath indicator on video frame
    # =====================================================
    if nose_min is None:
        nose_min_v, nose_max_v = temp_nose, temp_nose
    else:
        nose_min_v = min(nose_min, temp_nose)
        nose_max_v = max(nose_max, temp_nose)

    globals()['nose_min'] = nose_min_v
    globals()['nose_max'] = nose_max_v

    level = 0.5 if (nose_max_v - nose_min_v) < 0.01 else \
            1 - ((temp_nose - nose_min_v) / (nose_max_v - nose_min_v))
    level = max(0.0, min(1.0, level))

    cv2.rectangle(frame,
                  (BAR_X, BAR_Y),
                  (BAR_X + BAR_WIDTH, BAR_Y + BAR_HEIGHT),
                  (200, 200, 200), 2)

    fill_h = int(level * BAR_HEIGHT)
    cv2.rectangle(frame,
                  (BAR_X,          BAR_Y + BAR_HEIGHT - fill_h),
                  (BAR_X + BAR_WIDTH, BAR_Y + BAR_HEIGHT),
                  (255, int(255 * level), 0), -1)

    cv2.putText(frame, "Breath", (BAR_X - 10, BAR_Y - 10),
                cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2)

    # ---- draw ROI boxes ----
    cv2.rectangle(frame, (x1, y1), (x1+w1, y1+h1), (255,   0, 0), 2)
    cv2.rectangle(frame, (x2, y2), (x2+w2, y2+h2), (0,   255, 0), 2)

    frame_count += 1

    cv2.imshow("Tracking", frame)
    if cv2.waitKey(1) & 0xFF == 27:   # ESC to quit
        QtWidgets.QApplication.quit()

# =========================================================
# RUN
# =========================================================
timer = QtCore.QTimer()
timer.timeout.connect(update)
timer.start(20)   # ~50 fps UI refresh

QtWidgets.QApplication.instance().exec_()

cap.release()
cv2.destroyAllWindows()

#$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$

# import cv2
# import numpy as np
# import pyqtgraph as pg
# from pyqtgraph.Qt import QtWidgets, QtCore

# # =========================================================
# # ⚙️ SETTINGS
# # =========================================================
# SMOOTH_K_NOSE     = 7
# SMOOTH_K_FOREHEAD = 11

# MIN_PEAK_VALLEY_DIFF = 0.08
# REFRACTORY_PERIOD    = 2.0

# STRESS_BASELINE_FRAMES = 20
# STRESS_THRESHOLD       = 0.05

# MAX_POINTS = 200

# BAR_X, BAR_Y = 550, 100
# BAR_WIDTH, BAR_HEIGHT = 40, 300

# # =========================================================
# # STATE
# # =========================================================
# nose_min, nose_max = None, None
# baseline_fixed = None   # 🔥 NEW (fixed baseline)

# # =========================================================
# # TIME AXIS
# # =========================================================
# class TimeAxisItem(pg.AxisItem):
#     def tickStrings(self, values, scale, spacing):
#         return [f"{int(v//60):02d}:{int(v%60):02d}" for v in values]

# # =========================================================
# # FUNCTIONS
# # =========================================================
# def get_temp_from_pixel(p):
#     return 0.05891454 * p + 30.07676744

# def moving_average(signal, k):
#     if len(signal) < k:
#         return signal
#     smooth = np.convolve(signal, np.ones(k)/k, mode='valid')
#     pad_left = [smooth[0]] * (k//2)
#     pad_right = [smooth[-1]] * (k//2)
#     return list(np.concatenate([pad_left, smooth, pad_right]))

# # =========================================================
# # BREATH DETECTION
# # =========================================================
# def detect_breath_peaks(x, y_smooth):
#     if len(y_smooth) < 5:
#         return []

#     y = np.array(y_smooth)
#     dy = np.diff(y)

#     peaks = []
#     last_peak_time = -999

#     for i in range(1, len(dy)):
#         if dy[i-1] > 0 and dy[i] <= 0:

#             time = x[i]
#             val = y[i]

#             if time - last_peak_time < REFRACTORY_PERIOD:
#                 continue

#             peaks.append((time, val))
#             last_peak_time = time

#     return peaks

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
# win.resize(1000, 900)

# p1 = win.addPlot(axisItems={'bottom': TimeAxisItem(orientation='bottom')}, title="Nose Raw")
# curve_raw = p1.plot(pen='y')

# win.nextRow()
# p2 = win.addPlot(axisItems={'bottom': TimeAxisItem(orientation='bottom')}, title="Nose Smooth")
# curve_smooth = p2.plot(pen='g')

# scatter_peaks = pg.ScatterPlotItem(pen='r', brush='r', size=10)
# p2.addItem(scatter_peaks)

# bpm_label = pg.TextItem(text="BPM: --", color=(255,255,0), anchor=(0,1))
# p2.addItem(bpm_label)

# win.nextRow()
# p3 = win.addPlot(axisItems={'bottom': TimeAxisItem(orientation='bottom')}, title="Forehead")
# curve_blue = p3.plot(pen='b')
# curve_red = p3.plot(pen='r')

# baseline_line = pg.InfiniteLine(angle=0, movable=False,
#                                pen=pg.mkPen((150,150,150), style=QtCore.Qt.DashLine))
# p3.addItem(baseline_line)

# # =========================================================
# # DATA
# # =========================================================
# x_data, y_nose, y_head = [], [], []
# frame_count = 0

# # =========================================================
# # LOOP
# # =========================================================
# def update():
#     global frame_count, nose_min, nose_max, baseline_fixed
#     global x_data, y_nose, y_head

#     ret, frame = cap.read()
#     if not ret:
#         QtWidgets.QApplication.quit()
#         return

#     gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

#     ok1, b1 = tracker_nose.update(frame)
#     ok2, b2 = tracker_head.update(frame)

#     if ok1 and ok2:

#         x1,y1,w1,h1 = map(int, b1)
#         x2,y2,w2,h2 = map(int, b2)

#         temp_nose = get_temp_from_pixel(np.mean(gray[y1:y1+h1, x1:x1+w1]))
#         temp_head = get_temp_from_pixel(np.mean(gray[y2:y2+h2, x2:x2+w2]))

#         cv2.putText(frame, f"Nose: {temp_nose:.2f}", (50,50),
#                     cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0,255,255), 2)

#         cv2.putText(frame, f"Forehead: {temp_head:.2f}", (50,90),
#                     cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0,255,0), 2)

#         t = frame_count / fps
#         x_data.append(t)
#         y_nose.append(temp_nose)
#         y_head.append(temp_head)

#         y_nose_smooth = moving_average(y_nose, SMOOTH_K_NOSE)
#         y_head_smooth = moving_average(y_head, SMOOTH_K_FOREHEAD)

#         if len(x_data) > MAX_POINTS:
#             x_data = x_data[-MAX_POINTS:]
#             y_nose = y_nose[-MAX_POINTS:]
#             y_head = y_head[-MAX_POINTS:]
#             y_nose_smooth = y_nose_smooth[-MAX_POINTS:]
#             y_head_smooth = y_head_smooth[-MAX_POINTS:]

#         # -------- Nose plots --------
#         curve_raw.setData(x_data, y_nose)
#         curve_smooth.setData(x_data, y_nose_smooth)

#         peaks = detect_breath_peaks(x_data, y_nose_smooth)

#         if peaks:
#             px, py = zip(*peaks)
#             scatter_peaks.setData(px, py)

#         # -------- BPM --------
#         if len(peaks) >= 2:
#             total_time = x_data[-1] - x_data[0]
#             bpm = (len(peaks)/total_time)*60
#         else:
#             bpm = 0

#         cv2.putText(frame, f"BPM: {bpm:.2f}", (50,130),
#                     cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0,255,255), 2)

#         bpm_label.setText(f"BPM: {bpm:.1f}")

#         # =====================================================
#         # 🔥 FIXED BASELINE LOGIC
#         # =====================================================
#         if baseline_fixed is None:
#             if len(y_head_smooth) >= STRESS_BASELINE_FRAMES:
#                 baseline_fixed = np.mean(y_head_smooth[:STRESS_BASELINE_FRAMES])
#             else:
#                 baseline_fixed = y_head_smooth[0]

#         baseline = baseline_fixed

#         baseline_line.setValue(baseline + STRESS_THRESHOLD)

#         y_blue, y_red = [], []
#         for val in y_head_smooth:
#             if val >= baseline + STRESS_THRESHOLD:
#                 y_red.append(val)
#                 y_blue.append(np.nan)
#             else:
#                 y_blue.append(val)
#                 y_red.append(np.nan)

#         curve_blue.setData(x_data, y_blue)
#         curve_red.setData(x_data, y_red)

#         # -------- Breath bar --------
#         if nose_min is None:
#             nose_min, nose_max = temp_nose, temp_nose

#         nose_min = min(nose_min, temp_nose)
#         nose_max = max(nose_max, temp_nose)

#         level = 1 - ((temp_nose - nose_min)/(nose_max - nose_min + 1e-6))

#         cv2.rectangle(frame,(BAR_X,BAR_Y),(BAR_X+BAR_WIDTH,BAR_Y+BAR_HEIGHT),(200,200,200),2)

#         fill_h = int(level*BAR_HEIGHT)

#         cv2.rectangle(frame,
#                       (BAR_X, BAR_Y+BAR_HEIGHT-fill_h),
#                       (BAR_X+BAR_WIDTH, BAR_Y+BAR_HEIGHT),
#                       (255,int(255*level),0), -1)

#         frame_count += 1

#     cv2.imshow("Tracking", frame)

#     if cv2.waitKey(1) & 0xFF == 27:
#         QtWidgets.QApplication.quit()

# # =========================================================
# # RUN
# # =========================================================
# timer = QtCore.QTimer()
# timer.timeout.connect(update)
# timer.start(20)

# QtWidgets.QApplication.instance().exec_()

# cap.release()
# cv2.destroyAllWindows()