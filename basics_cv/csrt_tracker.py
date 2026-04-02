import cv2
from matplotlib.pyplot import box

# ---------------------------
# 1. Read video
# ---------------------------
# vid_path = r"D:\Lie Detection Data HTI\Lie_detection_ex2\Audio_video_lie_detection_ex2\Krishan_lie_detection_ex2.mp4"
vid_path = r"C:\Users\Akash Vishwakarma\Downloads\krishna_grey_manual1.mp4"

cap = cv2.VideoCapture(vid_path)  # 0 for webcam

# ---------------------------
# 2. Read first frame
# ---------------------------
ret, frame = cap.read()

# ---------------------------
# 3. Select ROI manually
# ---------------------------
bbox = cv2.selectROI("Select Object", frame, False)  # (x, y) = where box starts (top-left corner)
                                                     #  (w, h) = how big the box is
cv2.destroyWindow("Select Object")

# ---------------------------
# 4. Create CSRT tracker
# ---------------------------
tracker = cv2.TrackerCSRT_create()

# ---------------------------
# 5. Initialize tracker
# ---------------------------
tracker.init(frame, bbox)

# ---------------------------
# 6. Tracking loop
# ---------------------------
while True:
    ret, frame = cap.read()
    if not ret:
        break

    # Update tracker
    success, bbox = tracker.update(frame)

    if success:
        x, y, w, h = [int(v) for v in bbox]

        # Draw rectangle
        cv2.rectangle(frame, (x,y), (x+w, y+h), (0,255,0), 2)

    else:
        cv2.putText(frame, "Tracking Lost", (50,50),
                    cv2.FONT_HERSHEY_SIMPLEX, 1, (0,0,255), 2)

    cv2.imshow("Tracking", frame)

    if cv2.waitKey(1) & 0xFF == 27:
        break

cap.release()
cv2.destroyAllWindows()