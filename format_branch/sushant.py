import cv2
import numpy as np


def create_tracker():
    try:
        return cv2.TrackerCSRT_create()
    except:
        return cv2.legacy.TrackerCSRT_create()


def moving_average(signal, k=7):
    return np.convolve(signal, np.ones(k)/k, mode='same')


def detect_breathing(signal):
    inhale_idx = []
    exhale_idx = []

    for i in range(1, len(signal)-1):
        if signal[i] > signal[i-1] and signal[i] > signal[i+1]:
            exhale_idx.append(i)

        if signal[i] < signal[i-1] and signal[i] < signal[i+1]:
            inhale_idx.append(i)

    return inhale_idx, exhale_idx


# ================================
# MAIN STREAM FUNCTION
# ================================
def stream_breathing_data(video_path, bbox, window_size=200):
    cap = cv2.VideoCapture(video_path)

    if not cap.isOpened():
        raise ValueError("Error opening video")

    fps = cap.get(cv2.CAP_PROP_FPS)

    tracker = create_tracker()

    ret, frame = cap.read()
    if not ret:
        raise ValueError("Error reading first frame")

    tracker.init(frame, bbox)

    intensity_values = []
    frame_id = 0
    bpm = 0

    # 👉 Send meta first (VERY useful for frontend)
    yield {
        "type": "meta",
        "fps": fps,
        "window_size": window_size
    }

    while True:
        ret, frame = cap.read()
        if not ret:
            break

        success, bbox = tracker.update(frame)

        mean_intensity = None
        phase = None

        if success:
            x, y, w, h = map(int, bbox)

            x = max(0, x)
            y = max(0, y)

            roi = frame[y:y+h, x:x+w]

            if roi.size != 0:
                gray = cv2.cvtColor(roi, cv2.COLOR_BGR2GRAY)
                mean_intensity = float(np.mean(gray))

                intensity_values.append(mean_intensity)

                # -----------------------------
                # Phase detection
                # -----------------------------
                if len(intensity_values) > 1:
                    if intensity_values[-1] > intensity_values[-2]:
                        phase = "Exhale"
                    else:
                        phase = "Inhale"

        # -----------------------------
        # SIGNAL PROCESSING
        # -----------------------------
        smooth_data = []
        inhale_idx = []
        exhale_idx = []

        if len(intensity_values) > 5:
            data = intensity_values[-window_size:]
            smooth_data = moving_average(data)

            inhale_idx, exhale_idx = detect_breathing(smooth_data)

            # -----------------------------
            # BPM
            # -----------------------------
            if len(exhale_idx) > 1:
                peak_intervals = np.diff(exhale_idx) / fps
                avg_time = np.mean(peak_intervals)
                if avg_time > 0:
                    bpm = float(60 / avg_time)

        # -----------------------------
        # TIME
        # -----------------------------
        time_sec = frame_id / fps if fps > 0 else 0

        # ================================
        # 🔥 YIELD DATA PER FRAME
        # ================================
        yield {
            "type": "frame",
            "frame": frame_id,
            "time": time_sec,
            "mean_intensity": mean_intensity,
            "bbox": [int(v) for v in bbox],
            "success": success,
            "phase": phase,
            "bpm": bpm,
            "raw_signal": intensity_values[-window_size:],   # for plotting
            "smooth_signal": smooth_data.tolist() if len(smooth_data) > 0 else [],
            "inhale_idx": inhale_idx,
            "exhale_idx": exhale_idx
        }

        frame_id += 1

    cap.release()