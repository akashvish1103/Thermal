import cv2
import numpy as np
import pyqtgraph as pg
from pyqtgraph.Qt import QtWidgets, QtCore

# =========================================================
# ⚙️ SETTINGS
# =========================================================
SMOOTH_K_NOSE     = 7
SMOOTH_K_FOREHEAD = 5

MIN_PEAK_VALLEY_DIFF = 0.08
REFRACTORY_PERIOD    = 2.0

STRESS_BASELINE_FRAMES = 20
STRESS_THRESHOLD       = 0.05

MAX_POINTS = 200

BAR_X, BAR_Y = 550, 100
BAR_WIDTH, BAR_HEIGHT = 40, 300

# =========================================================
# STATE
# =========================================================
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

def moving_average(signal, k=7):
    if len(signal) < k:
        return signal
    smooth = np.convolve(signal, np.ones(k)/k, mode='valid')
    pad_left = [smooth[0]]*(k//2)
    pad_right = [smooth[-1]]*(k//2)
    return list(np.concatenate([pad_left, smooth, pad_right]))

# =========================================================
# 🔥 FFT FUNCTION
# =========================================================
def compute_bpm_fft(signal, fps):
    if len(signal) < 30:
        return 0

    y = np.array(signal)
    y = y - np.mean(y)

    fft_vals = np.fft.fft(y)
    freqs = np.fft.fftfreq(len(y), d=1/fps)

    mask = freqs > 0
    freqs = freqs[mask]
    fft_vals = np.abs(fft_vals[mask])

    valid = (freqs >= 0.1) & (freqs <= 0.5)

    if not np.any(valid):
        return 0

    freqs = freqs[valid]
    fft_vals = fft_vals[valid]

    dominant_freq = freqs[np.argmax(fft_vals)]
    return dominant_freq * 60

# =========================================================
# (OPTIONAL) PEAK FUNCTION KEPT FOR VISUALIZATION
# =========================================================
def detect_breath_peaks(x, y_smooth):
    return []

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
win.resize(1000, 900)

p1 = win.addPlot(axisItems={'bottom': TimeAxisItem(orientation='bottom')})
curve_nose_raw = p1.plot(pen='y')

win.nextRow()
p2 = win.addPlot(axisItems={'bottom': TimeAxisItem(orientation='bottom')})
curve_nose_smooth = p2.plot(pen='g')

scatter_peaks = pg.ScatterPlotItem(pen='r', brush='r', size=10)
p2.addItem(scatter_peaks)

bpm_label = pg.TextItem(text="BPM: --", color=(255,255,0), anchor=(0,1))
p2.addItem(bpm_label)

win.nextRow()
p3 = win.addPlot(axisItems={'bottom': TimeAxisItem(orientation='bottom')})
curve_blue = p3.plot(pen='b')
curve_red = p3.plot(pen='r')

baseline_line = pg.InfiniteLine(angle=0, movable=False,
                               pen=pg.mkPen((150,150,150), style=QtCore.Qt.DashLine))
p3.addItem(baseline_line)

stress_label = pg.TextItem(text="", color=(255,80,80), anchor=(0,1))
p3.addItem(stress_label)

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

    if not (ok1 and ok2):
        cv2.imshow("Tracking", frame)
        cv2.waitKey(1)
        return

    x1,y1,w1,h1 = map(int, b1)
    x2,y2,w2,h2 = map(int, b2)

    temp_nose = get_temp_from_pixel(np.mean(gray[y1:y1+h1, x1:x1+w1]))
    temp_head = get_temp_from_pixel(np.mean(gray[y2:y2+h2, x2:x2+w2]))

    cv2.putText(frame, f"Nose: {temp_nose:.2f}", (50,50),
                cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0,255,255), 2)

    cv2.putText(frame, f"Forehead: {temp_head:.2f}", (50,90),
                cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0,255,0), 2)

    t = frame_count / fps
    x_data.append(t)
    y_nose.append(temp_nose)
    y_head.append(temp_head)

    y_nose_smooth = moving_average(y_nose, SMOOTH_K_NOSE)
    y_head_smooth = moving_average(y_head, SMOOTH_K_FOREHEAD)

    if len(x_data) > MAX_POINTS:
        x_data = x_data[-MAX_POINTS:]
        y_nose = y_nose[-MAX_POINTS:]
        y_head = y_head[-MAX_POINTS:]
        y_nose_smooth = y_nose_smooth[-MAX_POINTS:]
        y_head_smooth = y_head_smooth[-MAX_POINTS:]

    curve_nose_raw.setData(x_data, y_nose)
    curve_nose_smooth.setData(x_data, y_nose_smooth)

    # 🔥 FFT BPM
    bpm = compute_bpm_fft(y_nose_smooth, fps)

    bpm_label.setText(f"BPM: {bpm:.1f}")
    cv2.putText(frame, f"BPM: {bpm:.1f}", (50,130),
                cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0,255,255), 2)

    # 🔥 FIXED BASELINE
    if not hasattr(update, "baseline_fixed"):
        if len(y_head_smooth) >= STRESS_BASELINE_FRAMES:
            update.baseline_fixed = np.mean(y_head_smooth[:STRESS_BASELINE_FRAMES])
        else:
            update.baseline_fixed = y_head_smooth[0]

    baseline = update.baseline_fixed
    baseline_line.setValue(baseline + STRESS_THRESHOLD)

    y_blue, y_red = [], []
    for val in y_head_smooth:
        if val >= baseline + STRESS_THRESHOLD:
            y_red.append(val)
            y_blue.append(np.nan)
        else:
            y_blue.append(val)
            y_red.append(np.nan)

    curve_blue.setData(x_data, y_blue)
    curve_red.setData(x_data, y_red)

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