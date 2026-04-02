import cv2

# vid_path = r"D:\Lie Detection Data HTI\Lie_detection_ex2\Thermal_lie_detection_ex2\grey_manual\krishna_grey_manual1.wmv"
vid_path = r"C:\Users\Akash Vishwakarma\Downloads\krishna_grey_manual1.mp4"
cap = cv2.VideoCapture(vid_path)

ret, frame = cap.read()

# STEP 1: Select multiple ROIs
bboxes = cv2.selectROIs("Select Objects", frame, fromCenter=False, showCrosshair=True)

trackers = []

# STEP 2: Create tracker for each ROI
for bbox in bboxes:
    tracker = cv2.TrackerCSRT_create()
    tracker.init(frame, bbox)
    trackers.append(tracker)

while True:
    ret, frame = cap.read()
    if not ret:
        break

    # STEP 3: Update all trackers
    for tracker in trackers:
        success, bbox = tracker.update(frame)

        if success:
            x, y, w, h = map(int, bbox)
            cv2.rectangle(frame, (x, y), (x+w, y+h), (0,255,0), 2)

    cv2.imshow("Tracking", frame)

    if cv2.waitKey(1) & 0xFF == 27:
        break

cap.release()
cv2.destroyAllWindows()