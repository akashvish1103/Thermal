import cv2
import numpy as np

# -----------------------------
# HELPERS
# -----------------------------
def create_tracker():
    try:
        return cv2.TrackerCSRT_create()
    except:
        return cv2.legacy.TrackerCSRT_create()


def moving_average(signal, k=15):  # stronger smoothing
    return np.convolve(signal, np.ones(k)/k, mode='same')


# -----------------------------
# 🔥 IMPROVED BREATH DETECTION
# -----------------------------
def detect_breathing(signal, fps):
    inhale_idx = []
    exhale_idx = []

    min_distance = int(1.5 * fps)

    std_val = np.std(signal)
    amplitude_threshold = std_val * 0.6

    last_peak = -min_distance
    last_valley = None

    for i in range(1, len(signal)-1):

        # VALLEY (Inhale)
        if signal[i] < signal[i-1] and signal[i] < signal[i+1]:
            last_valley = i
            inhale_idx.append(i)

        # PEAK (Exhale)
        if signal[i] > signal[i-1] and signal[i] > signal[i+1]:

            if last_valley is not None:
                amplitude = signal[i] - signal[last_valley]

                if amplitude > amplitude_threshold:
                    if (i - last_peak) > min_distance:
                        exhale_idx.append(i)
                        last_peak = i

    return inhale_idx, exhale_idx


def calculate_bpm(exhale_idx, fps):
    if len(exhale_idx) > 1:
        intervals = np.diff(exhale_idx)
        avg_interval = np.mean(intervals)

        breathing_rate_hz = fps / avg_interval
        return float(breathing_rate_hz * 60)

    return 0.0


# -----------------------------
# MAIN STREAM FUNCTION
# -----------------------------
def stream_breathing_data(video_path, bbox):
    cap = cv2.VideoCapture(video_path)

    if not cap.isOpened():
        raise ValueError("Error opening video")

    fps = cap.get(cv2.CAP_PROP_FPS)
    if fps == 0:
        fps = 10

    tracker = create_tracker()

    ret, frame = cap.read()
    if not ret:
        raise ValueError("Error reading first frame")

    tracker.init(frame, bbox)

    intensity_values = []
    frame_id = 0
    bpm = 0

    # 👉 send meta once
    yield {
        "type": "meta",
        "fps": fps
    }

    # -----------------------------
    # LOOP
    # -----------------------------
    while True:
        ret, frame = cap.read()
        if not ret:
            break

        success, bbox = tracker.update(frame)

        mean_intensity = None
        phase = None
        smooth_value = None

        if success:
            x, y, w, h = map(int, bbox)

            x = max(0, x)
            y = max(0, y)

            roi = frame[y:y+h, x:x+w]

            if roi.size != 0:
                gray = cv2.cvtColor(roi, cv2.COLOR_BGR2GRAY)

                mean_intensity = float(np.mean(gray))
                intensity_values.append(mean_intensity)

                # simple phase (for UI)
                if len(intensity_values) > 1:
                    if intensity_values[-1] > intensity_values[-2]:
                        phase = "Exhale"
                    else:
                        phase = "Inhale"

        # -----------------------------
        # 🔥 SIGNAL PROCESSING (UPDATED)
        # -----------------------------
        if len(intensity_values) > 30:

            data = intensity_values[-200:]  # window
            smooth_data = moving_average(data)

            # latest smoothed value
            smooth_value = float(smooth_data[-1])

            # 🔥 NEW detection
            inhale_idx, exhale_idx = detect_breathing(smooth_data, fps)

            bpm = calculate_bpm(exhale_idx, fps)

        # -----------------------------
        # TIME
        # -----------------------------
        time_sec = frame_id / fps if fps > 0 else 0

        # -----------------------------
        # BBOX FORMAT
        # -----------------------------
        x, y, w, h = [int(v) for v in bbox]

        bbox_data = {
            "x": x,
            "y": y,
            "w": w,
            "h": h,
            "x2": x + w,
            "y2": y + h
        }

        # -----------------------------
        # OUTPUT PER FRAME
        # -----------------------------
        yield {
            "type": "frame",
            "frame": frame_id,
            "time": time_sec,
            "mean_intensity": mean_intensity,
            "smooth_value": smooth_value,
            "bpm": bpm,
            "phase": phase,
            "bbox": bbox_data,
            "success": success
        }

        frame_id += 1

    cap.release()