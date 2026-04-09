import cv2
import numpy as np

# =========================================================
# ⚙️  TUNING PARAMETERS
# =========================================================
SMOOTH_K_NOSE     = 7
SMOOTH_K_FOREHEAD = 5

# --- Breath Detection ---
MIN_PEAK_VALLEY_DIFF = 0.08
REFRACTORY_PERIOD    = 2.0

# --- Stress Detection (Forehead) ---
STRESS_BASELINE_FRAMES = 50
STRESS_THRESHOLD = 0.1
STRESS_THRESHOLD_2 = 0.5


# =========================================================
# HELPERS
# =========================================================
def create_tracker():
    try:
        return cv2.TrackerCSRT_create()
    except:
        return cv2.legacy.TrackerCSRT_create()

def get_temp_from_pixel(pixel_value):
    return 0.05891454 * pixel_value + 30.07676744

def moving_average(signal, k=7):
    if len(signal) < k:
        return signal
    smooth    = np.convolve(signal, np.ones(k) / k, mode='valid')
    pad_left  = [smooth[0]]  * (k // 2)
    pad_right = [smooth[-1]] * (k // 2)
    return list(np.concatenate([pad_left, smooth, pad_right]))


# =========================================================
# 🔥 BREATH DETECTION
# =========================================================
def detect_breath_peaks(x, y_smooth):
    if len(y_smooth) < 5:
        return []

    y  = np.array(y_smooth)
    dy = np.diff(y)

    raw_peaks   = []
    raw_valleys = []

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
        next_valleys = [vi for vi in raw_valleys if vi > pi and vi not in used_valleys]
        if not next_valleys:
            continue

        vi = next_valleys[0]
        peak_val   = y[pi]
        valley_val = y[vi]

        if peak_val - valley_val < MIN_PEAK_VALLEY_DIFF:
            continue

        t_peak = x[pi]
        if t_peak - last_cycle_time < REFRACTORY_PERIOD:
            continue

        breath_markers.append((t_peak, peak_val))
        used_valleys.add(vi)
        last_cycle_time = t_peak

    return breath_markers


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

    # Rolling buffers
    x_data = []
    y_nose = []
    y_head = []

    frame_count = 0
    baseline_fixed = None

    # Meta
    yield {
        "type": "meta",
        "fps": fps,
        "threshold_1": STRESS_THRESHOLD,
        "threshold_2": STRESS_THRESHOLD_2
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
        bpm = 0

        time_sec = frame_count / fps if fps > 0 else 0

        if ok1 and ok2:
            x1, y1, w1, h1 = map(int, b1)
            x2, y2, w2, h2 = map(int, b2)

            roi_nose = frame[y1:y1+h1, x1:x1+w1]
            roi_head = frame[y2:y2+h2, x2:x2+w2]

            if roi_nose.size != 0 and roi_head.size != 0:
                gray_nose = cv2.cvtColor(roi_nose, cv2.COLOR_BGR2GRAY)
                gray_head = cv2.cvtColor(roi_head, cv2.COLOR_BGR2GRAY)

                nose_temp = float(get_temp_from_pixel(np.mean(gray_nose)))
                head_temp = float(get_temp_from_pixel(np.mean(gray_head)))

                x_data.append(time_sec)
                y_nose.append(nose_temp)
                y_head.append(head_temp)

                # Keep buffers manageable if frontend doesn't need infinite history?
                # The generator yields current point, but detect_breath_peaks needs some history.
                # Here we just keep everything or limit to recent window (e.g. 5000 frames)
                if len(x_data) > 5000:
                    x_data = x_data[-5000:]
                    y_nose = y_nose[-5000:]
                    y_head = y_head[-5000:]

        # =================================================
        # SIGNAL PROCESSING
        # =================================================
        if len(y_nose) > 0 and len(y_head) > 0:
            y_nose_smooth_arr = moving_average(y_nose, SMOOTH_K_NOSE)
            y_head_smooth_arr = moving_average(y_head, SMOOTH_K_FOREHEAD)

            nose_smooth = float(y_nose_smooth_arr[-1])
            head_smooth = float(y_head_smooth_arr[-1])

            # Breath detection using the better custom method
            peaks = detect_breath_peaks(x_data, y_nose_smooth_arr)
            if len(peaks) >= 2:
                total_time = x_data[-1] - x_data[0]
                bpm = round((len(peaks) / total_time) * 60) if total_time > 0 else 0

            # Fixed Baseline
            if baseline_fixed is None:
                if len(y_head_smooth_arr) >= STRESS_BASELINE_FRAMES:
                    baseline_fixed = float(np.mean(y_head_smooth_arr[:STRESS_BASELINE_FRAMES]))
                else:
                    baseline_fixed = float(y_head_smooth_arr[0])

        # =================================================
        # RED / BLUE LOGIC (Stress Alerts)
        # =================================================
        temp_diff = None
        stress_1_alert = False
        stress_2_alert = False

        if head_smooth is not None and baseline_fixed is not None:
            temp_diff = head_smooth - baseline_fixed
            stress_1_alert = (temp_diff >= STRESS_THRESHOLD)
            stress_2_alert = (temp_diff >= STRESS_THRESHOLD_2)

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
            "frame": frame_count,
            "time": time_sec,

            "nose_raw": nose_temp,
            "head_raw": head_temp,

            "nose_smooth": nose_smooth,
            "head_smooth": head_smooth,

            "bpm": bpm,

            "baseline": baseline_fixed,
            "temp_diff": temp_diff,
            
            "stress_1_alert": stress_1_alert,
            "stress_2_alert": stress_2_alert,

            "bbox_nose": bbox_nose_data,
            "bbox_head": bbox_head_data,

            "success": ok1 and ok2
        }

        frame_count += 1

    cap.release()
