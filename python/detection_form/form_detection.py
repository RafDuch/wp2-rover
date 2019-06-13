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
    _,contours,hierarchy = cv2.findContours(mask.copy(), 1, cv2.CHAIN_APPROX_NONE)
    
    
    cv2.drawContours(mask, contours, -1, (0,0,255),5)
    
    
    cv2.imshow('Resultat', mask)
    cv2.waitKey(10)



