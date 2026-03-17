import cv2

vid_path = r"D:\akashvProfile-TESTO-recorded-InCDAC-Lab\thermal-data\girish-demo.wmv"

cap = cv2.VideoCapture(vid_path)

fps = cap.get(cv2.CAP_PROP_FPS)
print("FPS:", fps)
delay = round(fps)

while True:
    ret, frame = cap.read()

    if not ret:
        break

    cv2.imshow("My Video Window", frame)

    if cv2.waitKey(100) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()