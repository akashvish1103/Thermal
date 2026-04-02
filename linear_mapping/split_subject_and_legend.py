import cv2
import numpy as np

# vid_path = r"D:\Lie Detection Data HTI\Lie_detection_ex2\Thermal_lie_detection_ex2\grey_manual\krishna_grey_manual1.wmv"
vid_path = r"C:\Users\Akash Vishwakarma\Desktop\Thermal_Analysis\linear_mapping\output.mp4"

cap =  cv2.VideoCapture(vid_path) 
frame_number = 0
while True and frame_number == 0:
    
    ret, frame = cap.read()
    if not ret:
        break

    grey_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    grey_frame_legend = grey_frame[::,640:]   # adjust this based on your legend's position and width

    # Display the frame
    cv2.imshow("Frame", frame)
    cv2.imshow("Grey Frame", grey_frame)
    cv2.imshow("Grey Frame Legend", grey_frame_legend)
    print(f"Frame {frame_number}: {frame.shape}")
    print(f"Grey Frame {frame_number}: {grey_frame.shape}")
    print(f"Grey Frame Legend {frame_number}: {grey_frame_legend.shape}")

    cv2.imwrite("linear_mapping/grey_frame_legend_30_45_celcius_mp4.png", grey_frame_legend)

    frame_number = frame_number + 1

    # Exit on 'q' key press
    if cv2.waitKey(0) & 0xFF == ord('q'):
        break

    

##################################################################################################
# import cv2
# import numpy as np

# legend_path = r"D:\akashvProfile-TESTO-recorded-InCDAC-Lab\thermal-data\cropped_and_saved\legend\frame_000000_legend.png"

# img = cv2.imread(legend_path)
# print("Legend shape:", img.shape)
# cv2.imshow("Legend", img)
# cv2.waitKey(0)
# cv2.destroyAllWindows()

# print(img.shape)
# print("ndim:", img.ndim)

# grey_img = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
# print("Grey Legend shape:", grey_img.shape)
# cv2.imshow("Grey Legend", grey_img)
# cv2.waitKey(0)
# cv2.destroyAllWindows()

# print("Grey Legend shape:", grey_img.shape)
# print("ndim:", grey_img.ndim)
