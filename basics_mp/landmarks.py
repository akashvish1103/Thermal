import cv2
import mediapipe as mp

mp_face_mesh = mp.solutions.face_mesh
face_mesh = mp_face_mesh.FaceMesh()

# vid_path = r"D:\akashvProfile-TESTO-recorded-InCDAC-Lab\thermal-data\girish-demo.wmv"
# vid_path = r"D:\Lie Detection Data HTI\Lie_detection_ex2\Thermal_lie_detection_ex2\krishna_grey_manual1.wmv"
vid_path = r"d:\Lie Detection Data HTI\Lie_detection_ex2\Thermal_lie_detection_ex2\sneha_grey_manual.wmv"


cap = cv2.VideoCapture(vid_path)

while True:
    ret, frame = cap.read()
    if not ret:
        break

    h, w, _ = frame.shape

    rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    result = face_mesh.process(rgb_frame)

    if result.multi_face_landmarks:
        for face_landmarks in result.multi_face_landmarks:

            # Nose tip landmark (index 1)
            nose = face_landmarks.landmark[1]

            # Convert normalized coords → pixel coords
            x = int(nose.x * w)
            y = int(nose.y * h)

            # Draw red dot
            cv2.circle(frame, (x, y), 2, (0, 0, 255), -1)

            # Above Nose tip landmark (index 4)
            nose_a = face_landmarks.landmark[4]

            # Convert normalized coords → pixel coords
            x = int(nose_a.x * w)
            y = int(nose_a.y * h)

            # Draw red dot
            cv2.circle(frame, (x, y), 2, (0, 0, 255), -1)

    cv2.imshow("Nose Tip Detection", frame)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()

# import mediapipe as mp
# print(mp.__file__)
# print(dir(mp))