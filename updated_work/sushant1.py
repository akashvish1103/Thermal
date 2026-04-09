# To Share it with Sushant for HTI Web Interface

import cv2
import numpy as np


# =========================================================
# SETTINGS
# =========================================================
SMOOTH_K_NOSE = 7
SMOOTH_K_FOREHEAD = 5

MIN_PEAK_VALLEY_DIFF = 0.08
REFRACTORY_PERIOD = 2.0

STRESS_BASELINE_FRAMES = 50
STRESS_THRESHOLD = 0.1


# =========================================================
# HELPERS
# =========================================================
def create_tracker():
    try:
        return cv2.TrackerCSRT_create()
    except:
        return cv2.legacy.TrackerCSRT_create()


def moving_average(signal, k=7):
    return np.convolve(signal, np.ones(k)/k, mode='same')


def get_temp_from_pixel(pixel):
    return 0.05891454 * pixel + 30.07676744


# =========================================================
# PEAK-BASED BREATH DETECTION (same style as demo)
# =========================================================
def compute_bpm(signal, fps):
    peaks = []

    for i in range(1, len(signal)-1):
        if signal[i] > signal[i-1] and signal[i] > signal[i+1]:
            peaks.append(i)

    if len(peaks) > 1:
        intervals = np.diff(peaks) / fps
        avg_time = np.mean(intervals)
        if avg_time > 0:
            return float(60 / avg_time)

    return 0


# =========================================================
# MAIN STREAM FUNCTION
# =========================================================
def stream_thermal_data(video_path, bbox_nose, bbox_head):

    cap = cv2.VideoCapture(video_path)

    if not cap.isOpened():
        raise ValueError("Error opening video")

    fps = cap.get(cv2.CAP_PROP_FPS)

    tracker_nose = create_tracker()
    tracker_head = create_tracker()

    ret, frame = cap.read()
    if not ret:
        raise ValueError("Error reading first frame")

    tracker_nose.init(frame, bbox_nose)
    tracker_head.init(frame, bbox_head)

    nose_values = []
    head_values = []

    frame_id = 0
    bpm = 0
    baseline_fixed = None

    # META
    yield {
        "type": "meta",
        "fps": fps,
        "threshold": STRESS_THRESHOLD
    }

    # =====================================================
    # LOOP
    # =====================================================
    while True:
        ret, frame = cap.read()
        if not ret:
            break

        ok1, b1 = tracker_nose.update(frame)
        ok2, b2 = tracker_head.update(frame)

        nose_temp = None
        head_temp = None
        nose_smooth = None
        head_smooth = None
        phase = None

        if ok1 and ok2:

            x1,y1,w1,h1 = map(int, b1)
            x2,y2,w2,h2 = map(int, b2)

            roi_nose = frame[y1:y1+h1, x1:x1+w1]
            roi_head = frame[y2:y2+h2, x2:x2+w2]

            if roi_nose.size != 0 and roi_head.size != 0:

                gray_nose = cv2.cvtColor(roi_nose, cv2.COLOR_BGR2GRAY)
                gray_head = cv2.cvtColor(roi_head, cv2.COLOR_BGR2GRAY)

                nose_temp = float(get_temp_from_pixel(np.mean(gray_nose)))
                head_temp = float(get_temp_from_pixel(np.mean(gray_head)))

                nose_values.append(nose_temp)
                head_values.append(head_temp)

                # Phase detection (same as demo)
                if len(nose_values) > 1:
                    if nose_values[-1] > nose_values[-2]:
                        phase = "Exhale"
                    else:
                        phase = "Inhale"

        # =================================================
        # SIGNAL PROCESSING
        # =================================================
        if len(nose_values) > SMOOTH_K_NOSE:
            smooth_series = moving_average(nose_values, SMOOTH_K_NOSE)
            nose_smooth = float(smooth_series[-1])

            bpm = compute_bpm(smooth_series, fps)

        if len(head_values) > SMOOTH_K_FOREHEAD:
            smooth_series = moving_average(head_values, SMOOTH_K_FOREHEAD)
            head_smooth = float(smooth_series[-1])

            # FIXED BASELINE
            if baseline_fixed is None:
                if len(smooth_series) >= STRESS_BASELINE_FRAMES:
                    baseline_fixed = float(np.mean(smooth_series[:STRESS_BASELINE_FRAMES]))
                else:
                    baseline_fixed = float(smooth_series[0])

        # =================================================
        # TIME
        # =================================================
        time_sec = frame_id / fps if fps > 0 else 0

        # =================================================
        # RED / BLUE LOGIC (EXPLICIT FOR UI)
        # =================================================
        temp_diff = None
        state = None

        if head_smooth is not None and baseline_fixed is not None:
            temp_diff = head_smooth - baseline_fixed

            if temp_diff >= STRESS_THRESHOLD:
                state = "elevated"   # 🔴
            else:
                state = "normal"     # 🔵

        # =================================================
        # BBOX FORMAT
        # =================================================
        bbox_nose_data = {
            "x": int(b1[0]), "y": int(b1[1]),
            "w": int(b1[2]), "h": int(b1[3])
        } if ok1 else None

        bbox_head_data = {
            "x": int(b2[0]), "y": int(b2[1]),
            "w": int(b2[2]), "h": int(b2[3])
        } if ok2 else None

        # =================================================
        # OUTPUT
        # =================================================
        yield {
            "type": "frame",
            "frame": frame_id,
            "time": time_sec,

            "nose_temp": nose_temp,
            "head_temp": head_temp,

            "nose_smooth": nose_smooth,
            "head_smooth": head_smooth,

            "bpm": bpm,
            "phase": phase,

            "baseline": baseline_fixed,
            "temp_diff": temp_diff,
            "state": state,

            "bbox_nose": bbox_nose_data,
            "bbox_head": bbox_head_data,

            "success": ok1 and ok2
        }

        frame_id += 1

    cap.release()