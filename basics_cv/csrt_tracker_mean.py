# This file is for testing the CSRT tracker and extracting mean intensity values from the tracked region.
#  It allows you to select an ROI, tracks it, and computes the mean intensity of the tracked region in each frame, 
# which can be used as a breathing signal.

# import cv2
# import numpy as np
# import matplotlib.pyplot as plt 
# # 1. Read video
# # ---------------------------
# # vid_path = r"D:\Lie Detection Data HTI\Lie_detection_ex2\Thermal_lie_detection_ex2\grey_manual\sneha_grey_manual.wmv"
# vid_path = r"D:\Lie Detection Data HTI\Lie_detection_ex2\Thermal_lie_detection_ex2\grey_manual\krishna_grey_manual1.wmv"

# cap = cv2.VideoCapture(vid_path) 

# # 2. Read first frame
# # ---------------------------
# ret, frame = cap.read()

# # 3. Select ROI manually
# # ---------------------------
# bbox = cv2.selectROI("Select Object", frame, False)   # (x, y) = where box starts (top-left corner) # (w, h) = how big the box is
# cv2.destroyWindow("Select Object")

# print("Selected ROI:", bbox)
# print(bbox)
# print(type(bbox))

# print("Type of frame:", type(frame))

# # ---------------------------
# # 4. Create CSRT tracker
# # ---------------------------
# tracker = cv2.TrackerCSRT_create()

# # ---------------------------
# # 5. Initialize tracker
# # ---------------------------
# tracker.init(frame, bbox)

# means = []

# # ---------------------------
# # 6. Tracking loop
# # ---------------------------
# while True:
#     ret, frame = cap.read()
#     if not ret:
#         break

#     # Update tracker
#     success, bbox = tracker.update(frame)

#     if success:
#         x, y, w, h = [int(v) for v in bbox]
#         gray_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)    

#         arr = gray_frame[y:y+h, x:x+w]
#         print(type(arr))
#         print(arr.shape)

#         means.append(np.mean(arr))


#         # Draw rectangle
#         cv2.rectangle(frame, (x,y), (x+w, y+h), (0,255,0), 2)


#     else:
#         cv2.putText(frame, "Tracking Lost", (50,50),
#                     cv2.FONT_HERSHEY_SIMPLEX, 1, (0,0,255), 2)

#     cv2.imshow("Tracking", frame)

#     if cv2.waitKey(1) & 0xFF == 27:
#         break

# cap.release()
# cv2.destroyAllWindows()

# print("Mean values:", means)


# # ✅ NOW plot
# plt.plot(means)
# plt.title("Breathing Signal")
# plt.xlabel("Frame")
# plt.ylabel("Mean Intensity")
# plt.grid()
# plt.show()

############################################################################

# This file is for testing multi-object tracking with CSRT tracker. It allows you to select multiple ROIs and tracks them simultaneously.
import cv2

vid_path = r"D:\Lie Detection Data HTI\Lie_detection_ex2\Thermal_lie_detection_ex2\grey_manual\krishna_grey_manual1.wmv"

cap = cv2.VideoCapture(vid_path) 
# cap = cv2.VideoCapture(0)

ret, frame = cap.read()

# Select multiple ROIs
bboxes = cv2.selectROIs("Select Objects", frame, False)
cv2.destroyWindow("Select Objects")

trackers = []

# Create tracker for each ROI
for bbox in bboxes:
    tracker = cv2.TrackerCSRT_create()
    tracker.init(frame, bbox)
    trackers.append(tracker)

# Loop
while True:
    ret, frame = cap.read()
    if not ret:
        break

    for tracker in trackers:
        success, bbox = tracker.update(frame)

        if success:
            x, y, w, h = [int(v) for v in bbox]
            cv2.rectangle(frame, (x,y), (x+w, y+h), (0,255,0), 2)

    cv2.imshow("Multi Tracking", frame)

    if cv2.waitKey(1) & 0xFF == 27:
        break

cap.release()
cv2.destroyAllWindows()

print(len(trackers))