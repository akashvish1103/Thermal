import cv2
import mediapipe as mp

# Initialize MediaPipe
mp_face_mesh = mp.solutions.face_mesh
face_mesh = mp_face_mesh.FaceMesh(
    static_image_mode=False,
    max_num_faces=1,
    refine_landmarks=True
)

# Nose landmark indices
# NOSE_LANDMARKS = [
#     # # Tip
#     1,

#     # # Bridge (top → down)
#     168, 6, 197, 195, 5, 4,

#     # Upper nose spread
#     # 2,
#     2, 98, 327,

#     # # Left side

#     94, 97, 2, 98,

#     # # Right side
#     326, 327,

#     # # Left nostril (fuller)
#     48, 49, 64, 60,

#     # # Right nostril (fuller)
#     278, 279, 309, 290,
#     # # Lower nose contour (often missed!)
#     19, 20, 44, 274
# ]
# NOSE_LANDMARKS =[193, 168, 417, 122, 351, 196, 419, 3, 248, 236, 456, 198, 420, 131, 360, 49, 279, 48,
#                                278, 219, 439, 59, 289, 218, 438, 237, 457, 44, 19, 274] 
NOSE_LANDMARKS =[219, 98, 360, 327, 326, 19]
# vid_path = r"D:\akashvProfile-TESTO-recorded-InCDAC-Lab\thermal-data\girish-gray-manual-range-testo.wmv"
# vid_path = r"D:\HTI_Recorded_data\output_clips\question_60.mp4"
# vid_path = r"D:\Lie Detection Data HTI\Lie_detection_ex2\Thermal_lie_detection_ex2\krishna_grey_manual1.wmv"
vid_path = r"d:\Lie Detection Data HTI\Lie_detection_ex2\Thermal_lie_detection_ex2\sneha_grey_manual.wmv"

# Open video (0 for webcam or give video path)
cap = cv2.VideoCapture(vid_path)
while cap.isOpened():
    ret, frame = cap.read()
    if not ret:
        break

    # Convert to RGB
    rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

    # Process
    results = face_mesh.process(rgb)

    if results.multi_face_landmarks:
        for face_landmarks in results.multi_face_landmarks:

            h, w, _ = frame.shape

            for idx in NOSE_LANDMARKS:
                lm = face_landmarks.landmark[idx]

                x = int(lm.x * w)
                y = int(lm.y * h)

                # Draw red dot
                if idx == 2:
                    cv2.circle(frame, (x, y), 1, (0, 0, 255), -1)
                    cv2.putText(frame, str(idx), (x + 2, y), cv2.FONT_HERSHEY_SIMPLEX, 0.2, (0, 0, 255), 1)
                else:   
                    cv2.circle(frame, (x, y), 1, (0, 150,0 ), -1)
                    cv2.putText(frame, str(idx), (x +2, y), cv2.FONT_HERSHEY_SIMPLEX, 0.2, (0, 0, 255), 1)
    cv2.imshow("Nose Landmarks", frame)

    if cv2.waitKey(100) & 0xFF == 27:
        break

cap.release()
cv2.destroyAllWindows()