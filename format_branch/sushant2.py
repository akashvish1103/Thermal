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


def moving_average(signal, k=7):
    return np.convolve(signal, np.ones(k)/k, mode='same')


# -----------------------------
# MAIN STREAM FUNCTION
# -----------------------------
def stream_breathing_data(video_path, bbox):
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

            # safe bbox
            x = max(0, x)
            y = max(0, y)

            roi = frame[y:y+h, x:x+w]

            if roi.size != 0:
                gray = cv2.cvtColor(roi, cv2.COLOR_BGR2GRAY)
                mean_intensity = float(np.mean(gray))

                intensity_values.append(mean_intensity)

                # -----------------------------
                # Phase detection (simple)
                # -----------------------------
                if len(intensity_values) > 1:
                    if intensity_values[-1] > intensity_values[-2]:
                        phase = "Exhale"
                    else:
                        phase = "Inhale"

        # -----------------------------
        # SIGNAL PROCESSING
        # -----------------------------
        if len(intensity_values) > 7:
            smooth_data = moving_average(intensity_values)

            # latest smoothed value only
            smooth_value = float(smooth_data[-1])

            # BPM calculation using peaks
            peaks = []
            for i in range(1, len(smooth_data)-1):
                if smooth_data[i] > smooth_data[i-1] and smooth_data[i] > smooth_data[i+1]:
                    peaks.append(i)

            if len(peaks) > 1:
                intervals = np.diff(peaks) / fps
                avg_time = np.mean(intervals)
                if avg_time > 0:
                    bpm = float(60 / avg_time)

        # -----------------------------
        # TIME
        # -----------------------------
        time_sec = frame_id / fps if fps > 0 else 0

        # -----------------------------
        # BBOX FORMAT (frontend-friendly)
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

        # ==============================
        # 🔥 YIELD PER FRAME
        # ==============================
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