import cv2

# -----------------------------
# Load video
# -----------------------------
video_path = r"D:\Lie Detection Data HTI\Lie_detection_ex2\Thermal_lie_detection_ex2\grey_manual\krishna_grey_manual1.wmv"   # change this
cap = cv2.VideoCapture(video_path)

# Read first frame
ret, frame = cap.read()
if not ret:
    print("Error reading video")
    exit()

# -----------------------------
# Select ROI (bounding box)
# -----------------------------
bbox = cv2.selectROI("Select Object", frame, False)
cv2.destroyWindow("Select Object")

print()

# -----------------------------
# Initialize CSRT tracker
# -----------------------------
tracker = cv2.TrackerCSRT_create()
tracker.init(frame, bbox)

# -----------------------------
# Tracking loop
# -----------------------------
while True:
    ret, frame = cap.read()
    if not ret:
        break

    # Update tracker
    success, bbox = tracker.update(frame)

    if success:
        # Draw bounding box
        x, y, w, h = [int(v) for v in bbox]
        cv2.rectangle(frame, (x, y), (x+w, y+h), (0, 255, 0), 2)

        cv2.putText(frame, "Tracking", (20, 40),
                    cv2.FONT_HERSHEY_SIMPLEX, 1, (0,255,0), 2)
    else:
        cv2.putText(frame, "Lost", (20, 40),
                    cv2.FONT_HERSHEY_SIMPLEX, 1, (0,0,255), 2)

    cv2.imshow("CSRT Tracking", frame)

    # Exit on ESC
    if cv2.waitKey(30) & 0xFF == 27:
        break

cap.release()
cv2.destroyAllWindows()