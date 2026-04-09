# import cv2
# import numpy as np
# import pyqtgraph as pg
# from pyqtgraph.Qt import QtWidgets, QtCore

# # =========================================================
# # ⚙️  TUNING PARAMETERS — adjust these to calibrate
# # =========================================================

# # --- Smoothing ---
# SMOOTH_K_NOSE     = 7     # moving average window for NOSE signal (higher = smoother, more lag)
# SMOOTH_K_FOREHEAD = 5    # moving average window for FOREHEAD signal (higher = smoother, more lag)
#                           # tip: forehead benefits from more smoothing (more noise from skin)

# # --- Breath Detection ---
# MIN_PEAK_VALLEY_DIFF = 0.08   # 🔥 minimum temp drop (°C) after a peak to count as a real breath
#                                # raise → fewer dots (ignore small wiggles)
#                                # lower → more dots (catch shallow breaths)

# REFRACTORY_PERIOD    = 2.0    # minimum seconds between two counted breaths
#                                # raise → cap max detectable BPM (2.0s = 30 BPM max)
#                                # lower → allow faster breathing detection

# # --- Stress Detection (Forehead) ---
# STRESS_BASELINE_FRAMES = 50   # how many frames to average for the baseline temperature
#                                # more frames = more stable baseline, but slower to adapt

# STRESS_THRESHOLD = 0.1     # 🔥 temperature rise (°C) above baseline = stress/elevated state
#                                # raise → only flag strong temperature spikes as stress
#                                # lower → more sensitive, flags subtle rises

# # --- Second Forehead Threshold ---
# STRESS_THRESHOLD_2 = 0.5   # 🔥 UPDATE THIS VALUE — second forehead threshold (°C above baseline)
#                              # e.g. 0.3 = flag only stronger/more sustained temperature rises
#                              # raise → stricter detection, lower → more sensitive

# # --- Display ---
# MAX_POINTS   = 200            # number of data points shown on the rolling graph window
# BAR_X, BAR_Y = 550, 100
# BAR_WIDTH, BAR_HEIGHT = 40, 300

# # =========================================================
# # STATE — do not modify
# # =========================================================
# nose_min, nose_max = None, None

# # =========================================================
# # TIME AXIS — shows MM:SS on x-axis
# # =========================================================
# class TimeAxisItem(pg.AxisItem):
#     def tickStrings(self, values, scale, spacing):
#         return [f"{int(v//60):02d}:{int(v%60):02d}" for v in values]

# # =========================================================
# # UTILITY FUNCTIONS
# # =========================================================

# def get_temp_from_pixel(pixel_value):
#     """
#     Convert grayscale pixel intensity → temperature (°C).
#     Calibration formula: T = 0.05891454 * pixel + 30.07676744
#     Adjust these coefficients to match your thermal camera calibration.
#     """
#     return 0.05891454 * pixel_value + 30.07676744


# def moving_average(signal, k=7):
#     """
#     Smooth a signal using a centered moving average of window size k.
#     Edges are padded by repeating the first/last smoothed value.
#     Larger k = smoother curve but introduces more lag.
#     """
#     if len(signal) < k:
#         return signal
#     smooth    = np.convolve(signal, np.ones(k) / k, mode='valid')
#     pad_left  = [smooth[0]]  * (k // 2)
#     pad_right = [smooth[-1]] * (k // 2)
#     return list(np.concatenate([pad_left, smooth, pad_right]))


# # =========================================================
# # 🔥 BREATH DETECTION — peak + valley cycle method
# #
# #  A breath is counted ONLY when ALL 3 conditions are met:
# #    1. A local peak exists (temp rises then falls)
# #    2. A valley follows the peak with drop >= MIN_PEAK_VALLEY_DIFF
# #       → filters out small noise bumps
# #    3. At least REFRACTORY_PERIOD seconds since last counted breath
# #       → prevents double-counting one breath as two
# #
# #  Returns: list of (time, value) tuples for confirmed breath peaks
# # =========================================================
# def detect_breath_peaks(x, y_smooth):
#     if len(y_smooth) < 5:
#         return []

#     y  = np.array(y_smooth)
#     dy = np.diff(y)

#     raw_peaks   = []
#     raw_valleys = []

#     # find ALL local peaks (rise→fall) and valleys (fall→rise)
#     for i in range(1, len(dy)):
#         if dy[i-1] > 0 and dy[i] <= 0:
#             raw_peaks.append(i)
#         elif dy[i-1] < 0 and dy[i] >= 0:
#             raw_valleys.append(i)

#     if not raw_peaks or not raw_valleys:
#         return []

#     breath_markers  = []
#     last_cycle_time = -999
#     used_valleys    = set()

#     for pi in raw_peaks:
#         # find first unused valley after this peak
#         next_valleys = [vi for vi in raw_valleys if vi > pi and vi not in used_valleys]
#         if not next_valleys:
#             continue

#         vi = next_valleys[0]

#         peak_val   = y[pi]
#         valley_val = y[vi]

#         # condition 2: meaningful drop required
#         if peak_val - valley_val < MIN_PEAK_VALLEY_DIFF:
#             continue

#         # condition 3: refractory period
#         t_peak = x[pi]
#         if t_peak - last_cycle_time < REFRACTORY_PERIOD:
#             continue

#         breath_markers.append((t_peak, peak_val))
#         used_valleys.add(vi)
#         last_cycle_time = t_peak

#     return breath_markers


# # =========================================================
# # VIDEO — open and select ROIs
# # =========================================================
# # vid_path = r"D:\Lie Detection Data HTI\Lie_detection_ex2\Thermal_lie_detection_ex2\grey_manual\pratham_grey_manual.wmv"
# cap = cv2.VideoCapture(r"C:\Users\Akash Vishwakarma\Downloads\krishna_grey_manual1.mp4")
# # vid_path = r"D:\Lie Detection Data HTI\Lie_detection_ex2\Thermal_lie_detection_ex2\grey_manual\priyank_grey_manual.wmv"
# # cap = cv2.VideoCapture(vid_path)
# fps = cap.get(cv2.CAP_PROP_FPS)

# ret, frame = cap.read()
# if not ret:
#     print("ERROR: Could not read video file.")
#     exit()

# print("Draw a box around the NOSE, then press ENTER or SPACE")
# bbox_nose = cv2.selectROI("Nose ROI", frame, False)
# cv2.destroyWindow("Nose ROI")

# print("Draw a box around the FOREHEAD, then press ENTER or SPACE")
# bbox_head = cv2.selectROI("Forehead ROI", frame, False)
# cv2.destroyWindow("Forehead ROI")

# # CSRT tracker — accurate but slower; swap to KCF if lag is too high
# tracker_nose = cv2.TrackerCSRT_create()
# tracker_head = cv2.TrackerCSRT_create()
# tracker_nose.init(frame, bbox_nose)
# tracker_head.init(frame, bbox_head)

# # =========================================================
# # PYQTGRAPH UI — 3 rows of plots
# # =========================================================
# app = QtWidgets.QApplication([])
# win = pg.GraphicsLayoutWidget(show=True)
# win.resize(1000, 900)
# win.setWindowTitle("Breath & Stress Monitor")

# # --- Row 1: Nose Smoothed + breath peaks ---
# p1 = win.addPlot(
#     axisItems={'bottom': TimeAxisItem(orientation='bottom')},
#     title="Nose — Smoothed  |  🔴 = confirmed breath (exhale peak)"
# )
# p1.setLabel('left',   'Temp (°C)')
# p1.setLabel('bottom', 'Time')
# curve_nose_smooth = p1.plot(pen=pg.mkPen('g', width=2))

# # red dots on confirmed breath peaks
# scatter_peaks = pg.ScatterPlotItem(
#     pen=pg.mkPen('r', width=2), brush='r', size=10
# )
# p1.addItem(scatter_peaks)

# # floating BPM label on the plot
# bpm_label = pg.TextItem(text="BPM: --", color=(255, 255, 0), anchor=(0, 1))
# p1.addItem(bpm_label)

# # --- Row 2: Forehead Smooth — blue=normal, red=elevated (Threshold T1) ---
# win.nextRow()
# p2 = win.addPlot(
#     axisItems={'bottom': TimeAxisItem(orientation='bottom')},
#     title=f"Forehead — Threshold T1  |  🔵 normal  🔴 elevated (T1 = {STRESS_THRESHOLD}°C above baseline)"
# )
# p2.setLabel('left',   'Temp (°C)')
# p2.setLabel('bottom', 'Time')

# # blue = within normal range (T1)
# curve_forehead_normal_t1 = p2.plot(pen=pg.mkPen('b', width=2))
# # red = above T1 threshold
# curve_forehead_stress_t1 = p2.plot(pen=pg.mkPen('r', width=2))

# # dashed baseline reference line for T1
# baseline_line_t1 = pg.InfiniteLine(
#     angle=0, movable=False,
#     pen=pg.mkPen(color=(150, 150, 150), style=QtCore.Qt.DashLine)
# )
# p2.addItem(baseline_line_t1)

# # stress label T1
# stress_label_t1 = pg.TextItem(text="", color=(255, 80, 80), anchor=(0, 1))
# p2.addItem(stress_label_t1)

# # --- Row 3: Forehead Smooth — blue=normal, red=elevated (Threshold T2) ---
# win.nextRow()
# p3 = win.addPlot(
#     axisItems={'bottom': TimeAxisItem(orientation='bottom')},
#     title=f"Forehead — Threshold T2  |  🔵 normal  🔴 elevated (T2 = {STRESS_THRESHOLD_2}°C above baseline)"
# )
# p3.setLabel('left',   'Temp (°C)')
# p3.setLabel('bottom', 'Time')

# # blue = within normal range (T2)
# curve_forehead_normal_t2 = p3.plot(pen=pg.mkPen('b', width=2))
# # red = above T2 threshold
# curve_forehead_stress_t2 = p3.plot(pen=pg.mkPen('r', width=2))

# # dashed baseline reference line for T2
# baseline_line_t2 = pg.InfiniteLine(
#     angle=0, movable=False,
#     pen=pg.mkPen(color=(150, 150, 150), style=QtCore.Qt.DashLine)
# )
# p3.addItem(baseline_line_t2)

# # stress label T2
# stress_label_t2 = pg.TextItem(text="", color=(255, 80, 80), anchor=(0, 1))
# p3.addItem(stress_label_t2)

# # =========================================================
# # DATA BUFFERS
# # =========================================================
# x_data = []   # time in seconds
# y_nose = []   # raw nose temperatures
# y_head = []   # raw forehead temperatures
# frame_count = 0

# # =========================================================
# # MAIN UPDATE LOOP — called every 20 ms by QTimer
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

#     if not (ok1 and ok2):
#         cv2.imshow("Tracking", frame)
#         cv2.waitKey(1)
#         return

#     # ---- extract ROI pixel means → temperatures ----
#     x1, y1, w1, h1 = map(int, b1)
#     x2, y2, w2, h2 = map(int, b2)

#     temp_nose = get_temp_from_pixel(np.mean(gray[y1:y1+h1, x1:x1+w1]))
#     temp_head = get_temp_from_pixel(np.mean(gray[y2:y2+h2, x2:x2+w2]))

#     # ---- overlay temperatures on video frame ----
#     cv2.putText(frame, f"Nose:     {temp_nose:.2f} C", (50,  50),
#                 cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 255), 2)
#     cv2.putText(frame, f"Forehead: {temp_head:.2f} C", (50,  90),
#                 cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255,   0), 2)

#     # ---- append to rolling buffers ----
#     t = frame_count / fps
#     x_data.append(t)
#     y_nose.append(temp_nose)
#     y_head.append(temp_head)

#     # ---- smooth both signals ----
#     y_nose_smooth = moving_average(y_nose, SMOOTH_K_NOSE)
#     y_head_smooth = moving_average(y_head, SMOOTH_K_FOREHEAD)

#     # ---- trim to MAX_POINTS rolling window ----
#     if len(x_data) > MAX_POINTS:
#         x_data        = x_data[-MAX_POINTS:]
#         y_nose        = y_nose[-MAX_POINTS:]
#         y_head        = y_head[-MAX_POINTS:]
#         y_nose_smooth = y_nose_smooth[-MAX_POINTS:]
#         y_head_smooth = y_head_smooth[-MAX_POINTS:]

#     # =====================================================
#     # PLOT 1 — Nose Smooth + Breath Detection
#     # =====================================================
#     curve_nose_smooth.setData(x_data, y_nose_smooth)

#     peaks = detect_breath_peaks(x_data, y_nose_smooth)

#     if peaks:
#         px, py = zip(*peaks)
#         scatter_peaks.setData(list(px), list(py))
#     else:
#         scatter_peaks.setData([], [])

#     # ---- BPM calculation ----
#     if len(peaks) >= 2:
#         total_time = x_data[-1] - x_data[0]
#         bpm = round((len(peaks) / total_time) * 60 if total_time > 0 else 0)   # added ROUND() by Akash
#     else:
#         bpm = 0

#     bpm_text = f"BPM: {bpm:.1f}"
#     bpm_label.setText(bpm_text)
#     if x_data and y_nose_smooth:
#         bpm_label.setPos(x_data[0], min(y_nose_smooth))

#     cv2.putText(frame, bpm_text, (50, 130),
#                 cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 255), 2)

#     # =====================================================
#     # FIXED BASELINE (compute once only)
#     # =====================================================

#     # 🔥 FIXED BASELINE (compute once only) 
#     if not hasattr(update, "baseline_fixed"):
#         if len(y_head_smooth) >= STRESS_BASELINE_FRAMES:
#             update.baseline_fixed = np.mean(y_head_smooth[:STRESS_BASELINE_FRAMES])
#         else:
#             update.baseline_fixed = y_head_smooth[0] if y_head_smooth else temp_head

#     baseline = update.baseline_fixed

#     # =====================================================
#     # PLOT 2 — Forehead Smoothed (Threshold T1 = STRESS_THRESHOLD)
#     #
#     # baseline = mean of first STRESS_BASELINE_FRAMES smoothed values
#     # if smoothed temp > baseline + STRESS_THRESHOLD → red (elevated/stress)
#     # otherwise → blue (normal)
#     #
#     # To tune:
#     #   raise STRESS_THRESHOLD → only flag obvious spikes
#     #   lower STRESS_THRESHOLD → more sensitive to subtle rises
#     # =====================================================
#     baseline_line_t1.setValue(baseline + STRESS_THRESHOLD)

#     y_normal_t1 = []
#     y_stress_t1 = []
#     stress_now_t1 = False

#     for val in y_head_smooth:
#         if val >= baseline + STRESS_THRESHOLD:
#             # elevated — potential stress (T1)
#             y_stress_t1.append(val)
#             y_normal_t1.append(np.nan)
#             stress_now_t1 = True
#         else:
#             y_normal_t1.append(val)
#             y_stress_t1.append(np.nan)

#     curve_forehead_normal_t1.setData(x_data, y_normal_t1)
#     curve_forehead_stress_t1.setData(x_data, y_stress_t1)

#     # update stress label T1 and video overlay
#     if stress_now_t1:
#         stress_label_t1.setText(f"⚠ ELEVATED  (+{STRESS_THRESHOLD}°C above baseline {baseline:.2f}°C)")
#         if x_data and y_head_smooth:
#             stress_label_t1.setPos(x_data[0], min(y_head_smooth))
#         # cv2.putText(frame, "FOREHEAD: ELEVATED", (50, 170),
#                     # cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)
#     else:
#         stress_label_t1.setText("")

#     # =====================================================
#     # PLOT 3 — Forehead Smoothed (Threshold T2 = STRESS_THRESHOLD_2)
#     #
#     # baseline = same fixed baseline as T1
#     # if smoothed temp > baseline + STRESS_THRESHOLD_2 → red (elevated/stress)
#     # otherwise → blue (normal)
#     #
#     # To tune:
#     #   raise STRESS_THRESHOLD_2 → only flag obvious spikes
#     #   lower STRESS_THRESHOLD_2 → more sensitive to subtle rises
#     # =====================================================
#     baseline_line_t2.setValue(baseline + STRESS_THRESHOLD_2)

#     y_normal_t2 = []
#     y_stress_t2 = []
#     stress_now_t2 = False

#     for val in y_head_smooth:
#         if val >= baseline + STRESS_THRESHOLD_2:
#             # elevated — potential stress (T2)
#             y_stress_t2.append(val)
#             y_normal_t2.append(np.nan)
#             stress_now_t2 = True
#         else:
#             y_normal_t2.append(val)
#             y_stress_t2.append(np.nan)

#     curve_forehead_normal_t2.setData(x_data, y_normal_t2)
#     curve_forehead_stress_t2.setData(x_data, y_stress_t2)

#     # update stress label T2
#     if stress_now_t2:
#         stress_label_t2.setText(f"⚠ ELEVATED  (+{STRESS_THRESHOLD_2}°C above baseline {baseline:.2f}°C)")
#         if x_data and y_head_smooth:
#             stress_label_t2.setPos(x_data[0], min(y_head_smooth))
#     else:
#         stress_label_t2.setText("")

#     # =====================================================
#     # BREATH BAR — visual breath indicator on video frame
#     # =====================================================
#     if nose_min is None:
#         nose_min_v, nose_max_v = temp_nose, temp_nose
#     else:
#         nose_min_v = min(nose_min, temp_nose)
#         nose_max_v = max(nose_max, temp_nose)

#     globals()['nose_min'] = nose_min_v
#     globals()['nose_max'] = nose_max_v

#     level = 0.5 if (nose_max_v - nose_min_v) < 0.01 else \
#             1 - ((temp_nose - nose_min_v) / (nose_max_v - nose_min_v))
#     level = max(0.0, min(1.0, level))

#     cv2.rectangle(frame,
#                   (BAR_X, BAR_Y),
#                   (BAR_X + BAR_WIDTH, BAR_Y + BAR_HEIGHT),
#                   (200, 200, 200), 2)

#     fill_h = int(level * BAR_HEIGHT)
#     cv2.rectangle(frame,
#                   (BAR_X,          BAR_Y + BAR_HEIGHT - fill_h),
#                   (BAR_X + BAR_WIDTH, BAR_Y + BAR_HEIGHT),
#                   (255, int(255 * level), 0), -1)

#     cv2.putText(frame, "Breath", (BAR_X - 10, BAR_Y - 10),
#                 cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2)

#     # ---- draw ROI boxes ----
#     cv2.rectangle(frame, (x1, y1), (x1+w1, y1+h1), (255,   0, 0), 2)
#     cv2.rectangle(frame, (x2, y2), (x2+w2, y2+h2), (0,   255, 0), 2)

#     frame_count += 1

#     cv2.imshow("Tracking", frame)
#     if cv2.waitKey(1) & 0xFF == 27:   # ESC to quit
#         QtWidgets.QApplication.quit()

# # =========================================================
# # RUN
# # =========================================================
# timer = QtCore.QTimer()
# timer.timeout.connect(update)
# timer.start(20)   # ~50 fps UI refresh

# QtWidgets.QApplication.instance().exec_()

# cap.release()
# cv2.destroyAllWindows()

# #############################################



# Well working, but Shrinking of graph-3 is still there




# import cv2
# import numpy as np
# import pyqtgraph as pg
# from pyqtgraph.Qt import QtWidgets, QtCore

# # =========================================================
# # ⚙️  TUNING PARAMETERS — adjust these to calibrate
# # =========================================================

# # --- Smoothing ---
# SMOOTH_K_NOSE     = 7     # moving average window for NOSE signal (higher = smoother, more lag)
# SMOOTH_K_FOREHEAD = 5    # moving average window for FOREHEAD signal (higher = smoother, more lag)
#                           # tip: forehead benefits from more smoothing (more noise from skin)

# # --- Breath Detection ---
# MIN_PEAK_VALLEY_DIFF = 0.08   # 🔥 minimum temp drop (°C) after a peak to count as a real breath
#                                # raise → fewer dots (ignore small wiggles)
#                                # lower → more dots (catch shallow breaths)

# REFRACTORY_PERIOD    = 2.0    # minimum seconds between two counted breaths
#                                # raise → cap max detectable BPM (2.0s = 30 BPM max)
#                                # lower → allow faster breathing detection

# # --- Stress Detection (Forehead) ---
# STRESS_BASELINE_FRAMES = 50   # how many frames to average for the baseline temperature
#                                # more frames = more stable baseline, but slower to adapt

# STRESS_THRESHOLD = 0.1     # 🔥 temperature rise (°C) above baseline = stress/elevated state
#                                # raise → only flag strong temperature spikes as stress
#                                # lower → more sensitive, flags subtle rises

# # --- Second Forehead Threshold ---
# STRESS_THRESHOLD_2 = 0.3   # 🔥 UPDATE THIS VALUE — second forehead threshold (°C above baseline)
#                              # e.g. 0.3 = flag only stronger/more sustained temperature rises
#                              # raise → stricter detection, lower → more sensitive

# # --- Display ---
# MAX_POINTS   = 200            # number of data points shown on the rolling graph window
# BAR_X, BAR_Y = 550, 100
# BAR_WIDTH, BAR_HEIGHT = 40, 300

# # =========================================================
# # STATE — do not modify
# # =========================================================
# nose_min, nose_max = None, None

# # =========================================================
# # TIME AXIS — shows MM:SS on x-axis
# # =========================================================
# class TimeAxisItem(pg.AxisItem):
#     def tickStrings(self, values, scale, spacing):
#         return [f"{int(v//60):02d}:{int(v%60):02d}" for v in values]

# # =========================================================
# # UTILITY FUNCTIONS
# # =========================================================

# def get_temp_from_pixel(pixel_value):
#     """
#     Convert grayscale pixel intensity → temperature (°C).
#     Calibration formula: T = 0.05891454 * pixel + 30.07676744
#     Adjust these coefficients to match your thermal camera calibration.
#     """
#     return 0.05891454 * pixel_value + 30.07676744


# def moving_average(signal, k=7):
#     """
#     Smooth a signal using a centered moving average of window size k.
#     Edges are padded by repeating the first/last smoothed value.
#     Larger k = smoother curve but introduces more lag.
#     """
#     if len(signal) < k:
#         return signal
#     smooth    = np.convolve(signal, np.ones(k) / k, mode='valid')
#     pad_left  = [smooth[0]]  * (k // 2)
#     pad_right = [smooth[-1]] * (k // 2)
#     return list(np.concatenate([pad_left, smooth, pad_right]))


# # =========================================================
# # 🔥 BREATH DETECTION — peak + valley cycle method
# #
# #  A breath is counted ONLY when ALL 3 conditions are met:
# #    1. A local peak exists (temp rises then falls)
# #    2. A valley follows the peak with drop >= MIN_PEAK_VALLEY_DIFF
# #       → filters out small noise bumps
# #    3. At least REFRACTORY_PERIOD seconds since last counted breath
# #       → prevents double-counting one breath as two
# #
# #  Returns: list of (time, value) tuples for confirmed breath peaks
# # =========================================================
# def detect_breath_peaks(x, y_smooth):
#     if len(y_smooth) < 5:
#         return []

#     y  = np.array(y_smooth)
#     dy = np.diff(y)

#     raw_peaks   = []
#     raw_valleys = []

#     # find ALL local peaks (rise→fall) and valleys (fall→rise)
#     for i in range(1, len(dy)):
#         if dy[i-1] > 0 and dy[i] <= 0:
#             raw_peaks.append(i)
#         elif dy[i-1] < 0 and dy[i] >= 0:
#             raw_valleys.append(i)

#     if not raw_peaks or not raw_valleys:
#         return []

#     breath_markers  = []
#     last_cycle_time = -999
#     used_valleys    = set()

#     for pi in raw_peaks:
#         # find first unused valley after this peak
#         next_valleys = [vi for vi in raw_valleys if vi > pi and vi not in used_valleys]
#         if not next_valleys:
#             continue

#         vi = next_valleys[0]

#         peak_val   = y[pi]
#         valley_val = y[vi]

#         # condition 2: meaningful drop required
#         if peak_val - valley_val < MIN_PEAK_VALLEY_DIFF:
#             continue

#         # condition 3: refractory period
#         t_peak = x[pi]
#         if t_peak - last_cycle_time < REFRACTORY_PERIOD:
#             continue

#         breath_markers.append((t_peak, peak_val))
#         used_valleys.add(vi)
#         last_cycle_time = t_peak

#     return breath_markers


# # =========================================================
# # VIDEO — open and select ROIs
# # =========================================================
# # vid_path = r"D:\Lie Detection Data HTI\Lie_detection_ex2\Thermal_lie_detection_ex2\grey_manual\pratham_grey_manual.wmv"
# cap = cv2.VideoCapture(r"C:\Users\Akash Vishwakarma\Downloads\krishna_grey_manual1.mp4")
# # vid_path = r"D:\Lie Detection Data HTI\Lie_detection_ex2\Thermal_lie_detection_ex2\grey_manual\priyank_grey_manual.wmv"
# # cap = cv2.VideoCapture(vid_path)
# fps = cap.get(cv2.CAP_PROP_FPS)

# ret, frame = cap.read()
# if not ret:
#     print("ERROR: Could not read video file.")
#     exit()

# print("Draw a box around the NOSE, then press ENTER or SPACE")
# bbox_nose = cv2.selectROI("Nose ROI", frame, False)
# cv2.destroyWindow("Nose ROI")

# print("Draw a box around the FOREHEAD, then press ENTER or SPACE")
# bbox_head = cv2.selectROI("Forehead ROI", frame, False)
# cv2.destroyWindow("Forehead ROI")

# # CSRT tracker — accurate but slower; swap to KCF if lag is too high
# tracker_nose = cv2.TrackerCSRT_create()
# tracker_head = cv2.TrackerCSRT_create()
# tracker_nose.init(frame, bbox_nose)
# tracker_head.init(frame, bbox_head)

# # =========================================================
# # PYQTGRAPH UI — 3 rows of plots
# # =========================================================
# app = QtWidgets.QApplication([])
# win = pg.GraphicsLayoutWidget(show=True)
# win.resize(1000, 900)
# win.setWindowTitle("Breath & Stress Monitor")

# # --- Row 1: Nose Smoothed + breath peaks ---
# p1 = win.addPlot(
#     axisItems={'bottom': TimeAxisItem(orientation='bottom')},
#     title="Breath Signals  |  🔴 = confirmed breath (exhale peak)"
# )
# p1.setLabel('left',   'Temp (°C)')
# p1.setLabel('bottom', 'Time')
# curve_nose_smooth = p1.plot(pen=pg.mkPen('g', width=2))

# # red dots on confirmed breath peaks
# scatter_peaks = pg.ScatterPlotItem(
#     pen=pg.mkPen('r', width=2), brush='r', size=10
# )
# p1.addItem(scatter_peaks)

# # floating BPM label on the plot
# bpm_label = pg.TextItem(text="BPM: --", color=(255, 255, 0), anchor=(0, 1))
# p1.addItem(bpm_label)

# # --- Row 2: Forehead Smooth — blue=normal, red=elevated (Threshold T1) ---
# win.nextRow()
# p2 = win.addPlot(
#     axisItems={'bottom': TimeAxisItem(orientation='bottom')},
#     title=f"Forehead — Threshold T1  |  🔵 normal  🔴 elevated (T1 = {STRESS_THRESHOLD}°C above baseline)"
# )
# p2.setLabel('left',   'Temp (°C)')
# p2.setLabel('bottom', 'Time')

# # disable default auto-range on Y so our manual setYRange() takes full control
# # this prevents pyqtgraph from including InfiniteLine & nan arrays in its range calc
# p2.disableAutoRange(axis='y')

# # blue = within normal range (T1)
# curve_forehead_normal_t1 = p2.plot(pen=pg.mkPen('b', width=2))
# # red = above T1 threshold
# curve_forehead_stress_t1 = p2.plot(pen=pg.mkPen('r', width=2))

# # dashed baseline reference line for T1
# baseline_line_t1 = pg.InfiniteLine(
#     angle=0, movable=False,
#     pen=pg.mkPen(color=(150, 150, 150), style=QtCore.Qt.DashLine)
# )
# p2.addItem(baseline_line_t1)

# # stress label T1
# stress_label_t1 = pg.TextItem(text="", color=(255, 80, 80), anchor=(0, 1))
# p2.addItem(stress_label_t1)

# # --- Row 3: Forehead Smooth — blue=normal, red=elevated (Threshold T2) ---
# win.nextRow()
# p3 = win.addPlot(
#     axisItems={'bottom': TimeAxisItem(orientation='bottom')},
#     title=f"Forehead — Threshold T2  |  🔵 normal  🔴 elevated (T2 = {STRESS_THRESHOLD_2}°C above baseline)"
# )
# p3.setLabel('left',   'Temp (°C)')
# p3.setLabel('bottom', 'Time')

# # disable default auto-range on Y so our manual setYRange() takes full control
# # this prevents pyqtgraph from including InfiniteLine & nan arrays in its range calc
# p3.disableAutoRange(axis='y')

# # blue = within normal range (T2)
# curve_forehead_normal_t2 = p3.plot(pen=pg.mkPen('b', width=2))
# # red = above T2 threshold
# curve_forehead_stress_t2 = p3.plot(pen=pg.mkPen('r', width=2))

# # dashed baseline reference line for T2
# baseline_line_t2 = pg.InfiniteLine(
#     angle=0, movable=False,
#     pen=pg.mkPen(color=(150, 150, 150), style=QtCore.Qt.DashLine)
# )
# p3.addItem(baseline_line_t2)

# # stress label T2
# stress_label_t2 = pg.TextItem(text="", color=(255, 80, 80), anchor=(0, 1))
# p3.addItem(stress_label_t2)

# # =========================================================
# # DATA BUFFERS
# # =========================================================
# x_data = []   # time in seconds
# y_nose = []   # raw nose temperatures
# y_head = []   # raw forehead temperatures
# frame_count = 0

# # =========================================================
# # MAIN UPDATE LOOP — called every 20 ms by QTimer
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

#     if not (ok1 and ok2):
#         cv2.imshow("Tracking", frame)
#         cv2.waitKey(1)
#         return

#     # ---- extract ROI pixel means → temperatures ----
#     x1, y1, w1, h1 = map(int, b1)
#     x2, y2, w2, h2 = map(int, b2)

#     temp_nose = get_temp_from_pixel(np.mean(gray[y1:y1+h1, x1:x1+w1]))
#     temp_head = get_temp_from_pixel(np.mean(gray[y2:y2+h2, x2:x2+w2]))

#     # ---- overlay temperatures on video frame ----
#     cv2.putText(frame, f"Nose:     {temp_nose:.2f} C", (50,  50),
#                 cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 255), 2)
#     cv2.putText(frame, f"Forehead: {temp_head:.2f} C", (50,  90),
#                 cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255,   0), 2)

#     # ---- append to rolling buffers ----
#     t = frame_count / fps
#     x_data.append(t)
#     y_nose.append(temp_nose)
#     y_head.append(temp_head)

#     # ---- smooth both signals ----
#     y_nose_smooth = moving_average(y_nose, SMOOTH_K_NOSE)
#     y_head_smooth = moving_average(y_head, SMOOTH_K_FOREHEAD)

#     # ---- trim to MAX_POINTS rolling window ----
#     if len(x_data) > MAX_POINTS:
#         x_data        = x_data[-MAX_POINTS:]
#         y_nose        = y_nose[-MAX_POINTS:]
#         y_head        = y_head[-MAX_POINTS:]
#         y_nose_smooth = y_nose_smooth[-MAX_POINTS:]
#         y_head_smooth = y_head_smooth[-MAX_POINTS:]

#     # =====================================================
#     # PLOT 1 — Nose Smooth + Breath Detection
#     # =====================================================
#     curve_nose_smooth.setData(x_data, y_nose_smooth)

#     peaks = detect_breath_peaks(x_data, y_nose_smooth)

#     if peaks:
#         px, py = zip(*peaks)
#         scatter_peaks.setData(list(px), list(py))
#     else:
#         scatter_peaks.setData([], [])

#     # ---- BPM calculation ----
#     if len(peaks) >= 2:
#         total_time = x_data[-1] - x_data[0]
#         bpm = round((len(peaks) / total_time) * 60 if total_time > 0 else 0)   # added ROUND() by Akash
#     else:
#         bpm = 0

#     bpm_text = f"BPM: {bpm:.1f}"
#     bpm_label.setText(bpm_text)
#     if x_data and y_nose_smooth:
#         bpm_label.setPos(x_data[0], min(y_nose_smooth))

#     cv2.putText(frame, bpm_text, (50, 130),
#                 cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 255), 2)

#     # =====================================================
#     # FIXED BASELINE (compute once only)
#     # =====================================================

#     # 🔥 FIXED BASELINE (compute once only) 
#     if not hasattr(update, "baseline_fixed"):
#         if len(y_head_smooth) >= STRESS_BASELINE_FRAMES:
#             update.baseline_fixed = np.mean(y_head_smooth[:STRESS_BASELINE_FRAMES])
#         else:
#             update.baseline_fixed = y_head_smooth[0] if y_head_smooth else temp_head

#     baseline = update.baseline_fixed

#     # =====================================================
#     # PLOT 2 — Forehead Smoothed (Threshold T1 = STRESS_THRESHOLD)
#     #
#     # baseline = mean of first STRESS_BASELINE_FRAMES smoothed values
#     # if smoothed temp > baseline + STRESS_THRESHOLD → red (elevated/stress)
#     # otherwise → blue (normal)
#     #
#     # To tune:
#     #   raise STRESS_THRESHOLD → only flag obvious spikes
#     #   lower STRESS_THRESHOLD → more sensitive to subtle rises
#     # =====================================================
#     baseline_line_t1.setValue(baseline + STRESS_THRESHOLD)

#     y_normal_t1 = []
#     y_stress_t1 = []
#     stress_now_t1 = False

#     for val in y_head_smooth:
#         if val >= baseline + STRESS_THRESHOLD:
#             # elevated — potential stress (T1)
#             y_stress_t1.append(val)
#             y_normal_t1.append(np.nan)
#             stress_now_t1 = True
#         else:
#             y_normal_t1.append(val)
#             y_stress_t1.append(np.nan)

#     curve_forehead_normal_t1.setData(x_data, y_normal_t1)
#     curve_forehead_stress_t1.setData(x_data, y_stress_t1)

#     # update stress label T1 and video overlay
#     if stress_now_t1:
#         # stress_label_t1.setText(f"⚠ ELEVATED  (+{STRESS_THRESHOLD}°C above baseline {baseline:.2f}°C)")
#         if x_data and y_head_smooth:
#             stress_label_t1.setPos(x_data[0], min(y_head_smooth))
#         # cv2.putText(frame, "FOREHEAD: ELEVATED", (50, 170),
#                     # cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)
#     else:
#         stress_label_t1.setText("")

#     # =====================================================
#     # PLOT 3 — Forehead Smoothed (Threshold T2 = STRESS_THRESHOLD_2)
#     #
#     # baseline = same fixed baseline as T1
#     # if smoothed temp > baseline + STRESS_THRESHOLD_2 → red (elevated/stress)
#     # otherwise → blue (normal)
#     #
#     # To tune:
#     #   raise STRESS_THRESHOLD_2 → only flag obvious spikes
#     #   lower STRESS_THRESHOLD_2 → more sensitive to subtle rises
#     # =====================================================
#     baseline_line_t2.setValue(baseline + STRESS_THRESHOLD_2)

#     y_normal_t2 = []
#     y_stress_t2 = []
#     stress_now_t2 = False

#     for val in y_head_smooth:
#         if val >= baseline + STRESS_THRESHOLD_2:
#             # elevated — potential stress (T2)
#             y_stress_t2.append(val)
#             y_normal_t2.append(np.nan)
#             stress_now_t2 = True
#         else:
#             y_normal_t2.append(val)
#             y_stress_t2.append(np.nan)

#     curve_forehead_normal_t2.setData(x_data, y_normal_t2)
#     curve_forehead_stress_t2.setData(x_data, y_stress_t2)

#     # update stress label T2
#     if stress_now_t2:
#         stress_label_t2.setText(f"⚠ ELEVATED  (+{STRESS_THRESHOLD_2}°C above baseline {baseline:.2f}°C)")
#         if x_data and y_head_smooth:
#             stress_label_t2.setPos(x_data[0], min(y_head_smooth))
#     else:
#         stress_label_t2.setText("")

#     # ---- fix Y axis range to actual forehead temp range (prevents flat-line appearance) ----
#     # pyqtgraph inflates range to 0 when InfiniteLine + nan arrays are present
#     # so we manually clamp Y to actual signal range with small padding
#     if y_head_smooth:
#         valid_vals = [v for v in y_head_smooth if not np.isnan(v)]
#         if valid_vals:
#             y_min = min(valid_vals) - 0.2
#             y_max = max(valid_vals) + 0.2
#             p2.setYRange(y_min, y_max, padding=0)
#             p3.setYRange(y_min, y_max, padding=0)

#     # =====================================================
#     # BREATH BAR — visual breath indicator on video frame
#     # =====================================================
#     if nose_min is None:
#         nose_min_v, nose_max_v = temp_nose, temp_nose
#     else:
#         nose_min_v = min(nose_min, temp_nose)
#         nose_max_v = max(nose_max, temp_nose)

#     globals()['nose_min'] = nose_min_v
#     globals()['nose_max'] = nose_max_v

#     level = 0.5 if (nose_max_v - nose_min_v) < 0.01 else \
#             1 - ((temp_nose - nose_min_v) / (nose_max_v - nose_min_v))
#     level = max(0.0, min(1.0, level))

#     cv2.rectangle(frame,
#                   (BAR_X, BAR_Y),
#                   (BAR_X + BAR_WIDTH, BAR_Y + BAR_HEIGHT),
#                   (200, 200, 200), 2)

#     fill_h = int(level * BAR_HEIGHT)
#     cv2.rectangle(frame,
#                   (BAR_X,          BAR_Y + BAR_HEIGHT - fill_h),
#                   (BAR_X + BAR_WIDTH, BAR_Y + BAR_HEIGHT),
#                   (255, int(255 * level), 0), -1)

#     cv2.putText(frame, "Breath", (BAR_X - 10, BAR_Y - 10),
#                 cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2)

#     # ---- draw ROI boxes ----
#     cv2.rectangle(frame, (x1, y1), (x1+w1, y1+h1), (255,   0, 0), 2)
#     cv2.rectangle(frame, (x2, y2), (x2+w2, y2+h2), (0,   255, 0), 2)

#     frame_count += 1

#     cv2.imshow("Tracking", frame)
#     if cv2.waitKey(1) & 0xFF == 27:   # ESC to quit
#         QtWidgets.QApplication.quit()

# # =========================================================
# # RUN
# # =========================================================
# timer = QtCore.QTimer()
# timer.timeout.connect(update)
# timer.start(20)   # ~50 fps UI refresh

# QtWidgets.QApplication.instance().exec_()

# cap.release()
# cv2.destroyAllWindows()

#############################################


# Tried to imporve shrinking of graph-3



# import cv2
# import numpy as np
# import pyqtgraph as pg
# from pyqtgraph.Qt import QtWidgets, QtCore

# # =========================================================
# # ⚙️  TUNING PARAMETERS — adjust these to calibrate
# # =========================================================

# # --- Smoothing ---
# SMOOTH_K_NOSE     = 7     # moving average window for NOSE signal (higher = smoother, more lag)
# SMOOTH_K_FOREHEAD = 5    # moving average window for FOREHEAD signal (higher = smoother, more lag)
#                           # tip: forehead benefits from more smoothing (more noise from skin)

# # --- Breath Detection ---
# MIN_PEAK_VALLEY_DIFF = 0.08   # 🔥 minimum temp drop (°C) after a peak to count as a real breath
#                                # raise → fewer dots (ignore small wiggles)
#                                # lower → more dots (catch shallow breaths)

# REFRACTORY_PERIOD    = 2.0    # minimum seconds between two counted breaths
#                                # raise → cap max detectable BPM (2.0s = 30 BPM max)
#                                # lower → allow faster breathing detection

# # --- Stress Detection (Forehead) ---
# STRESS_BASELINE_FRAMES = 50   # how many frames to average for the baseline temperature
#                                # more frames = more stable baseline, but slower to adapt

# STRESS_THRESHOLD = 0.1     # 🔥 temperature rise (°C) above baseline = stress/elevated state
#                                # raise → only flag strong temperature spikes as stress
#                                # lower → more sensitive, flags subtle rises

# # --- Second Forehead Threshold ---
# STRESS_THRESHOLD_2 = 0.5   # 🔥 UPDATE THIS VALUE — second forehead threshold (°C above baseline)
#                              # e.g. 0.3 = flag only stronger/more sustained temperature rises
#                              # raise → stricter detection, lower → more sensitive

# # --- Display ---
# MAX_POINTS   = 200            # number of data points shown on the rolling graph window
# BAR_X, BAR_Y = 550, 100
# BAR_WIDTH, BAR_HEIGHT = 40, 300

# # =========================================================
# # STATE — do not modify
# # =========================================================
# nose_min, nose_max = None, None

# # =========================================================
# # TIME AXIS — shows MM:SS on x-axis
# # =========================================================
# class TimeAxisItem(pg.AxisItem):
#     def tickStrings(self, values, scale, spacing):
#         return [f"{int(v//60):02d}:{int(v%60):02d}" for v in values]

# # =========================================================
# # UTILITY FUNCTIONS
# # =========================================================

# def get_temp_from_pixel(pixel_value):
#     """
#     Convert grayscale pixel intensity → temperature (°C).
#     Calibration formula: T = 0.05891454 * pixel + 30.07676744
#     Adjust these coefficients to match your thermal camera calibration.
#     """
#     return 0.05891454 * pixel_value + 30.07676744


# def moving_average(signal, k=7):
#     """
#     Smooth a signal using a centered moving average of window size k.
#     Edges are padded by repeating the first/last smoothed value.
#     Larger k = smoother curve but introduces more lag.
#     """
#     if len(signal) < k:
#         return signal
#     smooth    = np.convolve(signal, np.ones(k) / k, mode='valid')
#     pad_left  = [smooth[0]]  * (k // 2)
#     pad_right = [smooth[-1]] * (k // 2)
#     return list(np.concatenate([pad_left, smooth, pad_right]))


# # =========================================================
# # 🔥 BREATH DETECTION — peak + valley cycle method
# #
# #  A breath is counted ONLY when ALL 3 conditions are met:
# #    1. A local peak exists (temp rises then falls)
# #    2. A valley follows the peak with drop >= MIN_PEAK_VALLEY_DIFF
# #       → filters out small noise bumps
# #    3. At least REFRACTORY_PERIOD seconds since last counted breath
# #       → prevents double-counting one breath as two
# #
# #  Returns: list of (time, value) tuples for confirmed breath peaks
# # =========================================================
# def detect_breath_peaks(x, y_smooth):
#     if len(y_smooth) < 5:
#         return []

#     y  = np.array(y_smooth)
#     dy = np.diff(y)

#     raw_peaks   = []
#     raw_valleys = []

#     # find ALL local peaks (rise→fall) and valleys (fall→rise)
#     for i in range(1, len(dy)):
#         if dy[i-1] > 0 and dy[i] <= 0:
#             raw_peaks.append(i)
#         elif dy[i-1] < 0 and dy[i] >= 0:
#             raw_valleys.append(i)

#     if not raw_peaks or not raw_valleys:
#         return []

#     breath_markers  = []
#     last_cycle_time = -999
#     used_valleys    = set()

#     for pi in raw_peaks:
#         # find first unused valley after this peak
#         next_valleys = [vi for vi in raw_valleys if vi > pi and vi not in used_valleys]
#         if not next_valleys:
#             continue

#         vi = next_valleys[0]

#         peak_val   = y[pi]
#         valley_val = y[vi]

#         # condition 2: meaningful drop required
#         if peak_val - valley_val < MIN_PEAK_VALLEY_DIFF:
#             continue

#         # condition 3: refractory period
#         t_peak = x[pi]
#         if t_peak - last_cycle_time < REFRACTORY_PERIOD:
#             continue

#         breath_markers.append((t_peak, peak_val))
#         used_valleys.add(vi)
#         last_cycle_time = t_peak

#     return breath_markers


# # =========================================================
# # VIDEO — open and select ROIs
# # =========================================================
# # vid_path = r"D:\Lie Detection Data HTI\Lie_detection_ex2\Thermal_lie_detection_ex2\grey_manual\pratham_grey_manual.wmv"
# cap = cv2.VideoCapture(r"C:\Users\Akash Vishwakarma\Downloads\krishna_grey_manual1.mp4")
# # vid_path = r"D:\Lie Detection Data HTI\Lie_detection_ex2\Thermal_lie_detection_ex2\grey_manual\priyank_grey_manual.wmv"
# # cap = cv2.VideoCapture(vid_path)
# fps = cap.get(cv2.CAP_PROP_FPS)

# ret, frame = cap.read()
# if not ret:
#     print("ERROR: Could not read video file.")
#     exit()

# print("Draw a box around the NOSE, then press ENTER or SPACE")
# bbox_nose = cv2.selectROI("Nose ROI", frame, False)
# cv2.destroyWindow("Nose ROI")

# print("Draw a box around the FOREHEAD, then press ENTER or SPACE")
# bbox_head = cv2.selectROI("Forehead ROI", frame, False)
# cv2.destroyWindow("Forehead ROI")

# # CSRT tracker — accurate but slower; swap to KCF if lag is too high
# tracker_nose = cv2.TrackerCSRT_create()
# tracker_head = cv2.TrackerCSRT_create()
# tracker_nose.init(frame, bbox_nose)
# tracker_head.init(frame, bbox_head)

# # =========================================================
# # PYQTGRAPH UI — 3 rows of plots
# # =========================================================
# app = QtWidgets.QApplication([])
# win = pg.GraphicsLayoutWidget(show=True)
# win.resize(1000, 900)
# win.setWindowTitle("Breath & Stress Monitor")

# # --- Row 1: Nose Smoothed + breath peaks ---
# p1 = win.addPlot(
#     axisItems={'bottom': TimeAxisItem(orientation='bottom')},
#     title="Breath Signals  |  🔴 = confirmed breath (exhale peak)"
# )
# p1.setLabel('left',   'Temp (°C)')
# p1.setLabel('bottom', 'Time')
# curve_nose_smooth = p1.plot(pen=pg.mkPen('g', width=2))

# # red dots on confirmed breath peaks
# scatter_peaks = pg.ScatterPlotItem(
#     pen=pg.mkPen('r', width=2), brush='r', size=10
# )
# p1.addItem(scatter_peaks)

# # floating BPM label on the plot
# bpm_label = pg.TextItem(text="BPM: --", color=(255, 255, 0), anchor=(0, 1))
# p1.addItem(bpm_label)

# # --- Row 2: Forehead Smooth — blue=normal, red=elevated (Threshold T1) ---
# win.nextRow()
# p2 = win.addPlot(
#     axisItems={'bottom': TimeAxisItem(orientation='bottom')},
#     title=f"Forehead — Threshold T1  |  🔵 normal  🔴 elevated (T1 = {STRESS_THRESHOLD}°C above baseline)"
# )
# p2.setLabel('left',   'Temp (°C)')
# p2.setLabel('bottom', 'Time')

# # disable default auto-range on Y so our manual setYRange() takes full control
# # this prevents pyqtgraph from including InfiniteLine & nan arrays in its range calc
# p2.disableAutoRange(axis='y')

# # blue = within normal range (T1)
# curve_forehead_normal_t1 = p2.plot(pen=pg.mkPen('b', width=2))
# # red = above T1 threshold
# curve_forehead_stress_t1 = p2.plot(pen=pg.mkPen('r', width=2))

# # dashed baseline reference line for T1
# baseline_line_t1 = pg.InfiniteLine(
#     angle=0, movable=False,
#     pen=pg.mkPen(color=(150, 150, 150), style=QtCore.Qt.DashLine)
# )
# p2.addItem(baseline_line_t1)

# # stress label T1
# stress_label_t1 = pg.TextItem(text="", color=(255, 80, 80), anchor=(0, 1))
# p2.addItem(stress_label_t1)

# # --- Row 3: Forehead Smooth — blue=normal, red=elevated (Threshold T2) ---
# win.nextRow()
# p3 = win.addPlot(
#     axisItems={'bottom': TimeAxisItem(orientation='bottom')},
#     title=f"Forehead — Threshold T2  |  🔵 normal  🔴 elevated (T2 = {STRESS_THRESHOLD_2}°C above baseline)"
# )
# p3.setLabel('left',   'Temp (°C)')
# p3.setLabel('bottom', 'Time')

# # disable default auto-range on Y so our manual setYRange() takes full control
# # this prevents pyqtgraph from including InfiniteLine & nan arrays in its range calc
# p3.disableAutoRange(axis='y')

# # blue = within normal range (T2)
# curve_forehead_normal_t2 = p3.plot(pen=pg.mkPen('b', width=2))
# # red = above T2 threshold
# curve_forehead_stress_t2 = p3.plot(pen=pg.mkPen('r', width=2))

# # dashed baseline reference line for T2
# baseline_line_t2 = pg.InfiniteLine(
#     angle=0, movable=False,
#     pen=pg.mkPen(color=(150, 150, 150), style=QtCore.Qt.DashLine)
# )
# p3.addItem(baseline_line_t2)

# # stress label T2
# stress_label_t2 = pg.TextItem(text="", color=(255, 80, 80), anchor=(0, 1))
# p3.addItem(stress_label_t2)

# # =========================================================
# # DATA BUFFERS
# # =========================================================
# x_data = []   # time in seconds
# y_nose = []   # raw nose temperatures
# y_head = []   # raw forehead temperatures
# frame_count = 0

# # =========================================================
# # MAIN UPDATE LOOP — called every 20 ms by QTimer
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

#     if not (ok1 and ok2):
#         cv2.imshow("Tracking", frame)
#         cv2.waitKey(1)
#         return

#     # ---- extract ROI pixel means → temperatures ----
#     x1, y1, w1, h1 = map(int, b1)
#     x2, y2, w2, h2 = map(int, b2)

#     temp_nose = get_temp_from_pixel(np.mean(gray[y1:y1+h1, x1:x1+w1]))
#     temp_head = get_temp_from_pixel(np.mean(gray[y2:y2+h2, x2:x2+w2]))

#     # ---- overlay temperatures on video frame ----
#     cv2.putText(frame, f"Nose:     {temp_nose:.2f} C", (50,  50),
#                 cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 255), 2)
#     cv2.putText(frame, f"Forehead: {temp_head:.2f} C", (50,  90),
#                 cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255,   0), 2)

#     # ---- append to rolling buffers ----
#     t = frame_count / fps
#     x_data.append(t)
#     y_nose.append(temp_nose)
#     y_head.append(temp_head)

#     # ---- trim to MAX_POINTS rolling window ----
#     # IMPORTANT: trim raw buffers FIRST, then smooth the trimmed data
#     # this ensures all 3 plots always show the same x-range window
#     if len(x_data) > MAX_POINTS:
#         x_data = x_data[-MAX_POINTS:]
#         y_nose = y_nose[-MAX_POINTS:]
#         y_head = y_head[-MAX_POINTS:]

#     # ---- smooth AFTER trimming so smoothed arrays match x_data length exactly ----
#     # previously smoothing was done before trimming which caused graph 3 x-axis mismatch
#     y_nose_smooth = moving_average(y_nose, SMOOTH_K_NOSE)
#     y_head_smooth = moving_average(y_head, SMOOTH_K_FOREHEAD)

#     # =====================================================
#     # PLOT 1 — Nose Smooth + Breath Detection
#     # =====================================================
#     curve_nose_smooth.setData(x_data, y_nose_smooth)

#     peaks = detect_breath_peaks(x_data, y_nose_smooth)

#     if peaks:
#         px, py = zip(*peaks)
#         scatter_peaks.setData(list(px), list(py))
#     else:
#         scatter_peaks.setData([], [])

#     # ---- BPM calculation ----
#     if len(peaks) >= 2:
#         total_time = x_data[-1] - x_data[0]
#         bpm = round((len(peaks) / total_time) * 60 if total_time > 0 else 0)   # added ROUND() by Akash
#     else:
#         bpm = 0

#     bpm_text = f"BPM: {bpm:.1f}"
#     bpm_label.setText(bpm_text)
#     if x_data and y_nose_smooth:
#         bpm_label.setPos(x_data[0], min(y_nose_smooth))

#     cv2.putText(frame, bpm_text, (50, 130),
#                 cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 255), 2)

#     # =====================================================
#     # FIXED BASELINE (compute once only)
#     # =====================================================

#     # 🔥 FIXED BASELINE (compute once only) 
#     if not hasattr(update, "baseline_fixed"):
#         if len(y_head_smooth) >= STRESS_BASELINE_FRAMES:
#             update.baseline_fixed = np.mean(y_head_smooth[:STRESS_BASELINE_FRAMES])
#         else:
#             update.baseline_fixed = y_head_smooth[0] if y_head_smooth else temp_head

#     baseline = update.baseline_fixed

#     # =====================================================
#     # PLOT 2 — Forehead Smoothed (Threshold T1 = STRESS_THRESHOLD)
#     #
#     # baseline = mean of first STRESS_BASELINE_FRAMES smoothed values
#     # if smoothed temp > baseline + STRESS_THRESHOLD → red (elevated/stress)
#     # otherwise → blue (normal)
#     #
#     # To tune:
#     #   raise STRESS_THRESHOLD → only flag obvious spikes
#     #   lower STRESS_THRESHOLD → more sensitive to subtle rises
#     # =====================================================
#     baseline_line_t1.setValue(baseline + STRESS_THRESHOLD)

#     y_normal_t1 = []
#     y_stress_t1 = []
#     stress_now_t1 = False

#     for val in y_head_smooth:
#         if val >= baseline + STRESS_THRESHOLD:
#             # elevated — potential stress (T1)
#             y_stress_t1.append(val)
#             y_normal_t1.append(np.nan)
#             stress_now_t1 = True
#         else:
#             y_normal_t1.append(val)
#             y_stress_t1.append(np.nan)

#     curve_forehead_normal_t1.setData(x_data, y_normal_t1)
#     curve_forehead_stress_t1.setData(x_data, y_stress_t1)

#     # update stress label T1 and video overlay
#     if stress_now_t1:
#         # stress_label_t1.setText(f"⚠ ELEVATED  (+{STRESS_THRESHOLD}°C above baseline {baseline:.2f}°C)")
#         if x_data and y_head_smooth:
#             stress_label_t1.setPos(x_data[0], min(y_head_smooth))
#         # cv2.putText(frame, "FOREHEAD: ELEVATED", (50, 170),
#                     # cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)
#     else:
#         stress_label_t1.setText("")

#     # =====================================================
#     # PLOT 3 — Forehead Smoothed (Threshold T2 = STRESS_THRESHOLD_2)
#     #
#     # baseline = same fixed baseline as T1
#     # if smoothed temp > baseline + STRESS_THRESHOLD_2 → red (elevated/stress)
#     # otherwise → blue (normal)
#     #
#     # To tune:
#     #   raise STRESS_THRESHOLD_2 → only flag obvious spikes
#     #   lower STRESS_THRESHOLD_2 → more sensitive to subtle rises
#     # =====================================================
#     baseline_line_t2.setValue(baseline + STRESS_THRESHOLD_2)

#     y_normal_t2 = []
#     y_stress_t2 = []
#     stress_now_t2 = False

#     for val in y_head_smooth:
#         if val >= baseline + STRESS_THRESHOLD_2:
#             # elevated — potential stress (T2)
#             y_stress_t2.append(val)
#             y_normal_t2.append(np.nan)
#             stress_now_t2 = True
#         else:
#             y_normal_t2.append(val)
#             y_stress_t2.append(np.nan)

#     curve_forehead_normal_t2.setData(x_data, y_normal_t2)
#     curve_forehead_stress_t2.setData(x_data, y_stress_t2)

#     # update stress label T2
#     if stress_now_t2:
#         stress_label_t2.setText(f"⚠ ELEVATED  (+{STRESS_THRESHOLD_2}°C above baseline {baseline:.2f}°C)")
#         if x_data and y_head_smooth:
#             stress_label_t2.setPos(x_data[0], min(y_head_smooth))
#     else:
#         stress_label_t2.setText("")

#     # ---- fix Y axis range to actual forehead temp range (prevents flat-line appearance) ----
#     # pyqtgraph inflates range to 0 when InfiniteLine + nan arrays are present
#     # so we manually clamp Y to actual signal range with small padding
#     if y_head_smooth:
#         valid_vals = [v for v in y_head_smooth if not np.isnan(v)]
#         if valid_vals:
#             y_min = min(valid_vals) - 0.2
#             y_max = max(valid_vals) + 0.2
#             p2.setYRange(y_min, y_max, padding=0)
#             p3.setYRange(y_min, y_max, padding=0)

#     # =====================================================
#     # BREATH BAR — visual breath indicator on video frame
#     # =====================================================
#     if nose_min is None:
#         nose_min_v, nose_max_v = temp_nose, temp_nose
#     else:
#         nose_min_v = min(nose_min, temp_nose)
#         nose_max_v = max(nose_max, temp_nose)

#     globals()['nose_min'] = nose_min_v
#     globals()['nose_max'] = nose_max_v

#     level = 0.5 if (nose_max_v - nose_min_v) < 0.01 else \
#             1 - ((temp_nose - nose_min_v) / (nose_max_v - nose_min_v))
#     level = max(0.0, min(1.0, level))

#     cv2.rectangle(frame,
#                   (BAR_X, BAR_Y),
#                   (BAR_X + BAR_WIDTH, BAR_Y + BAR_HEIGHT),
#                   (200, 200, 200), 2)

#     fill_h = int(level * BAR_HEIGHT)
#     cv2.rectangle(frame,
#                   (BAR_X,          BAR_Y + BAR_HEIGHT - fill_h),
#                   (BAR_X + BAR_WIDTH, BAR_Y + BAR_HEIGHT),
#                   (255, int(255 * level), 0), -1)

#     cv2.putText(frame, "Breath", (BAR_X - 10, BAR_Y - 10),
#                 cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2)

#     # ---- draw ROI boxes ----
#     cv2.rectangle(frame, (x1, y1), (x1+w1, y1+h1), (255,   0, 0), 2)
#     cv2.rectangle(frame, (x2, y2), (x2+w2, y2+h2), (0,   255, 0), 2)

#     frame_count += 1

#     cv2.imshow("Tracking", frame)
#     if cv2.waitKey(1) & 0xFF == 27:   # ESC to quit
#         QtWidgets.QApplication.quit()

# # =========================================================
# # RUN
# # =========================================================
# timer = QtCore.QTimer()
# timer.timeout.connect(update)
# timer.start(20)   # ~50 fps UI refresh

# QtWidgets.QApplication.instance().exec_()

# cap.release()
# cv2.destroyAllWindows()

#############################################






# Trial 2 to solve Shrinking Problem
# Perfect Code (Final Version) by Akash Vishwakarma


import cv2
import numpy as np
import pyqtgraph as pg
from pyqtgraph.Qt import QtWidgets, QtCore

# =========================================================
# ⚙️  TUNING PARAMETERS — adjust these to calibrate
# =========================================================

# --- Smoothing ---
SMOOTH_K_NOSE     = 7     # moving average window for NOSE signal (higher = smoother, more lag)
SMOOTH_K_FOREHEAD = 5    # moving average window for FOREHEAD signal (higher = smoother, more lag)
                          # tip: forehead benefits from more smoothing (more noise from skin)

# --- Breath Detection ---
MIN_PEAK_VALLEY_DIFF = 0.08   # 🔥 minimum temp drop (°C) after a peak to count as a real breath
                               # raise → fewer dots (ignore small wiggles)
                               # lower → more dots (catch shallow breaths)

REFRACTORY_PERIOD    = 2.0    # minimum seconds between two counted breaths
                               # raise → cap max detectable BPM (2.0s = 30 BPM max)
                               # lower → allow faster breathing detection

# --- Stress Detection (Forehead) ---
STRESS_BASELINE_FRAMES = 50   # how many frames to average for the baseline temperature
                               # more frames = more stable baseline, but slower to adapt

STRESS_THRESHOLD = 0.1     # 🔥 temperature rise (°C) above baseline = stress/elevated state
                               # raise → only flag strong temperature spikes as stress
                               # lower → more sensitive, flags subtle rises

# --- Second Forehead Threshold ---
STRESS_THRESHOLD_2 = 0.5   # 🔥 UPDATE THIS VALUE — second forehead threshold (°C above baseline)
                             # e.g. 0.3 = flag only stronger/more sustained temperature rises
                             # raise → stricter detection, lower → more sensitive

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
# vid_path = r"D:\Lie Detection Data HTI\Lie_detection_ex2\Thermal_lie_detection_ex2\grey_manual\pratham_grey_manual.wmv"
cap = cv2.VideoCapture(r"C:\Users\Akash Vishwakarma\Downloads\krishna_grey_manual1.mp4")
# vid_path = r"D:\Lie Detection Data HTI\Lie_detection_ex2\Thermal_lie_detection_ex2\grey_manual\priyank_grey_manual.wmv"
# cap = cv2.VideoCapture(vid_path)
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

# --- Row 1: Nose Smoothed + breath peaks ---
p1 = win.addPlot(
    axisItems={'bottom': TimeAxisItem(orientation='bottom')},
    title="Breath Signals  |  🔴 = confirmed breath (exhale peak)"
)
p1.setLabel('left',   'Temp (°C)')
p1.setLabel('bottom', 'Time')
curve_nose_smooth = p1.plot(pen=pg.mkPen('g', width=2))

# red dots on confirmed breath peaks
scatter_peaks = pg.ScatterPlotItem(
    pen=pg.mkPen('r', width=2), brush='r', size=10
)
p1.addItem(scatter_peaks)

# floating BPM label on the plot
bpm_label = pg.TextItem(text="BPM: --", color=(255, 255, 0), anchor=(0, 1))
p1.addItem(bpm_label)

# --- Row 2: Forehead Smooth — blue=normal, red=elevated (Threshold T1) ---
win.nextRow()
p2 = win.addPlot(
    axisItems={'bottom': TimeAxisItem(orientation='bottom')},
    title=f"Forehead — Threshold T1  |  🔵 normal  🔴 elevated (T1 = {STRESS_THRESHOLD}°C above baseline)"
)
p2.setLabel('left',   'Temp (°C)')
p2.setLabel('bottom', 'Time')

# disable default auto-range on Y so our manual setYRange() takes full control
# this prevents pyqtgraph from including InfiniteLine & nan arrays in its range calc
p2.disableAutoRange(axis='y')

# lock x-axis of p2 to p1 — both will always show the same time window
p2.setXLink(p1)
p2.showGrid(x=True, y=True, alpha=0.3)   # grid lines for forehead T1 plot

# blue = within normal range (T1)
curve_forehead_normal_t1 = p2.plot(pen=pg.mkPen('b', width=2))
# red = above T1 threshold
curve_forehead_stress_t1 = p2.plot(pen=pg.mkPen('r', width=2))

# dashed baseline reference line for T1
baseline_line_t1 = pg.InfiniteLine(
    angle=0, movable=False,
    pen=pg.mkPen(color=(150, 150, 150), style=QtCore.Qt.DashLine)
)
p2.addItem(baseline_line_t1)

# stress label T1
stress_label_t1 = pg.TextItem(text="", color=(255, 80, 80), anchor=(0, 1))
p2.addItem(stress_label_t1)

# --- Row 3: Forehead Smooth — blue=normal, red=elevated (Threshold T2) ---
win.nextRow()
p3 = win.addPlot(
    axisItems={'bottom': TimeAxisItem(orientation='bottom')},
    title=f"Forehead — Threshold T2  |  🔵 normal  🔴 elevated (T2 = {STRESS_THRESHOLD_2}°C above baseline)"
)
p3.setLabel('left',   'Temp (°C)')
p3.setLabel('bottom', 'Time')

# disable default auto-range on Y so our manual setYRange() takes full control
# this prevents pyqtgraph from including InfiniteLine & nan arrays in its range calc
p3.disableAutoRange(axis='y')

# lock x-axis of p3 to p1 — all 3 graphs will always show the same time window
p3.setXLink(p1)
p3.showGrid(x=True, y=True, alpha=0.3)   # grid lines for forehead T2 plot

# blue = within normal range (T2)
curve_forehead_normal_t2 = p3.plot(pen=pg.mkPen('b', width=2))
# red = above T2 threshold
curve_forehead_stress_t2 = p3.plot(pen=pg.mkPen('r', width=2))

# dashed baseline reference line for T2
baseline_line_t2 = pg.InfiniteLine(
    angle=0, movable=False,
    pen=pg.mkPen(color=(150, 150, 150), style=QtCore.Qt.DashLine)
)
p3.addItem(baseline_line_t2)

# stress label T2
stress_label_t2 = pg.TextItem(text="", color=(255, 80, 80), anchor=(0, 1))
p3.addItem(stress_label_t2)

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

    # ---- trim to MAX_POINTS rolling window FIRST ----
    # IMPORTANT: trim raw buffers before smoothing so smoothed arrays
    # always match x_data length exactly — prevents x-axis mismatch on all plots
    if len(x_data) > MAX_POINTS:
        x_data = x_data[-MAX_POINTS:]
        y_nose = y_nose[-MAX_POINTS:]
        y_head = y_head[-MAX_POINTS:]

    # ---- smooth AFTER trimming ----
    y_nose_smooth = moving_average(y_nose, SMOOTH_K_NOSE)
    y_head_smooth = moving_average(y_head, SMOOTH_K_FOREHEAD)

    # =====================================================
    # PLOT 1 — Nose Smooth + Breath Detection
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
        bpm = round((len(peaks) / total_time) * 60 if total_time > 0 else 0)   # added ROUND() by Akash
    else:
        bpm = 0

    bpm_text = f"BPM: {bpm:.1f}"
    bpm_label.setText(bpm_text)
    if x_data and y_nose_smooth:
        bpm_label.setPos(x_data[0], min(y_nose_smooth))

    cv2.putText(frame, bpm_text, (50, 130),
                cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 255), 2)

    # =====================================================
    # FIXED BASELINE (compute once only)
    # =====================================================

    # 🔥 FIXED BASELINE (compute once only) 
    if not hasattr(update, "baseline_fixed"):
        if len(y_head_smooth) >= STRESS_BASELINE_FRAMES:
            update.baseline_fixed = np.mean(y_head_smooth[:STRESS_BASELINE_FRAMES])
        else:
            update.baseline_fixed = y_head_smooth[0] if y_head_smooth else temp_head

    baseline = update.baseline_fixed

    # =====================================================
    # PLOT 2 — Forehead Smoothed (Threshold T1 = STRESS_THRESHOLD)
    #
    # baseline = mean of first STRESS_BASELINE_FRAMES smoothed values
    # if smoothed temp > baseline + STRESS_THRESHOLD → red (elevated/stress)
    # otherwise → blue (normal)
    #
    # To tune:
    #   raise STRESS_THRESHOLD → only flag obvious spikes
    #   lower STRESS_THRESHOLD → more sensitive to subtle rises
    # =====================================================
    baseline_line_t1.setValue(baseline + STRESS_THRESHOLD)

    y_normal_t1 = []
    y_stress_t1 = []
    stress_now_t1 = False

    for val in y_head_smooth:
        if val >= baseline + STRESS_THRESHOLD:
            # elevated — potential stress (T1)
            y_stress_t1.append(val)
            y_normal_t1.append(np.nan)
            stress_now_t1 = True
        else:
            y_normal_t1.append(val)
            y_stress_t1.append(np.nan)

    curve_forehead_normal_t1.setData(x_data, y_normal_t1)
    curve_forehead_stress_t1.setData(x_data, y_stress_t1)

    # update stress label T1 and video overlay
    if stress_now_t1:
        # stress_label_t1.setText(f"⚠ ELEVATED  (+{STRESS_THRESHOLD}°C above baseline {baseline:.2f}°C)")
        if x_data and y_head_smooth:
            stress_label_t1.setPos(x_data[0], min(y_head_smooth))
        # cv2.putText(frame, "FOREHEAD: ELEVATED", (50, 170),
                    # cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)
    else:
        stress_label_t1.setText("")

    # =====================================================
    # PLOT 3 — Forehead Smoothed (Threshold T2 = STRESS_THRESHOLD_2)
    #
    # baseline = same fixed baseline as T1
    # if smoothed temp > baseline + STRESS_THRESHOLD_2 → red (elevated/stress)
    # otherwise → blue (normal)
    #
    # To tune:
    #   raise STRESS_THRESHOLD_2 → only flag obvious spikes
    #   lower STRESS_THRESHOLD_2 → more sensitive to subtle rises
    # =====================================================
    baseline_line_t2.setValue(baseline + STRESS_THRESHOLD_2)

    y_normal_t2 = []
    y_stress_t2 = []
    stress_now_t2 = False

    for val in y_head_smooth:
        if val >= baseline + STRESS_THRESHOLD_2:
            # elevated — potential stress (T2)
            y_stress_t2.append(val)
            y_normal_t2.append(np.nan)
            stress_now_t2 = True
        else:
            y_normal_t2.append(val)
            y_stress_t2.append(np.nan)

    curve_forehead_normal_t2.setData(x_data, y_normal_t2)
    curve_forehead_stress_t2.setData(x_data, y_stress_t2)

    # update stress label T2
    if stress_now_t2:
        stress_label_t2.setText(f"⚠ ELEVATED  (+{STRESS_THRESHOLD_2}°C above baseline {baseline:.2f}°C)")
        if x_data and y_head_smooth:
            stress_label_t2.setPos(x_data[0], min(y_head_smooth))
    else:
        stress_label_t2.setText("")

    # ---- fix Y axis range to actual forehead temp range (prevents flat-line appearance) ----
    # pyqtgraph inflates range to 0 when InfiniteLine + nan arrays are present
    # so we manually clamp Y to actual signal range with small padding
    if y_head_smooth:
        valid_vals = [v for v in y_head_smooth if not np.isnan(v)]
        if valid_vals:
            y_min = min(valid_vals) - 0.2
            y_max = max(valid_vals) + 0.2
            p2.setYRange(y_min, y_max, padding=0)
            p3.setYRange(y_min, y_max, padding=0)

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

#############################################