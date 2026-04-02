import cv2
import numpy as np

cap = cv2.VideoCapture(r"C:\Users\Akash Vishwakarma\Desktop\Thermal_Analysis\linear_mapping\output.mp4")

frame_id = 0
while True and frame_id < 10:
    print("FRAME ID:", frame_id)  # Check only the first 10 frames for efficiency
    ret, frame = cap.read()
    cv2.imshow("Frame", frame)
    if cv2.waitKey(0) & 0xFF == ord('q'):
        break
    if not ret:
        break

    print(frame.shape)
    print("*"* 30)
    frame_id += 1