import cv2
import numpy as np

video_capture = cv2.VideoCapture(0)
video_capture.set(3, 750)
video_capture.set(4, 300)

    
while True :
    ret, frame = video_capture.read()
    # Passage en niveau de gris
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

    # Filtre gaussien
    blur = cv2.GaussianBlur(gray,(5,5),0)

    # Passage en noir et blanc par seuillage
    ret,thresh1 = cv2.threshold(blur,60,255,cv2.THRESH_BINARY)

    # Enleve les accidentelles detections de ligne
    mask = cv2.erode(thresh1, None, iterations=2)
    mask = cv2.dilate(mask, None, iterations=2)

    # Trouver les contours
    _,contours,hierarchy = cv2.findContours(mask, 1, cv2.CHAIN_APPROX_NONE)
    
    for cnt in contours :
        approx = cv2.approxPolyDP(cnt,0.001*cv2.arcLength(cnt,True),True)
        cv2.drawContours(frame, [approx], -1, (0,255,0),4)
        if len(approx) == 4 :
            print("carre")
        else :
            print("autre")
    
    #print(len(contours))
    #print(contours)
    cv2.imshow('Resultat', frame)
    cv2.waitKey(10)



