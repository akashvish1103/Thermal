import cv2
import numpy as np

cap_wmv = cv2.VideoCapture(r"D:\Lie Detection Data HTI\Lie_detection_ex2\Thermal_lie_detection_ex2\grey_manual\krishna_grey_manual1.wmv")
cap_mp4 = cv2.VideoCapture(r"C:\Users\Akash Vishwakarma\Downloads\krishna_grey_manual1.mp4")

frame_id = 0

while True and frame_id < 10:
    print("FRAME ID:", frame_id)  # Check only the first 10 frames for efficiency
    ret1, f1 = cap_wmv.read()
    ret2, f2 = cap_mp4.read()

    print(f1.shape)
    print(f2.shape )
    is_equal = np.array_equal(cap_wmv, cap_mp4)        
    print("Checking Equality : ", is_equal)              
    print("*"* 30)
    frame_id += 1

cap_wmv.release()
cap_mp4.release()