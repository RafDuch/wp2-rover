from collections import OrderedDict
import imutils
import statistics
import numpy as np
import cv2
import smbus
import time

num_cas = 1
bus = smbus.SMBus(1)
address = 0x12
video_capture = cv2.VideoCapture(0)
video_capture.set(3, 750)
video_capture.set(4, 300)
video_capture.set(cv2.CAP_PROP_AUTOFOCUS, 0) # turn the autofocus off


while(True):
    # Prises de frames
    ret, img = video_capture.read()
    frame = img[150:350, 0:750]
    image = img.copy()    
    # Passage en niveau de gris
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

    # Filtre gaussien
    blur = cv2.GaussianBlur(gray,(5,5),0)
    
    # Passage en noir et blanc par seuillage
    ret,thresh1 = cv2.threshold(blur,60,255,cv2.THRESH_BINARY_INV)
    
    # Enleve les accidentelles detections de ligne   
    mask = cv2.erode(thresh1, None, iterations=2)
    mask = cv2.dilate(mask, None, iterations=2)

    # Trouver les contours
    _,contours,hierarchy = cv2.findContours(mask.copy(), 1, cv2.CHAIN_APPROX_NONE)

    # Trouver les plus gros contours
    if len(contours) > 0:
        c = max(contours, key=cv2.contourArea)
        M = cv2.moments(c)
        cx = int(M['m10']/M['m00'])
        cy = int(M['m01']/M['m00'])
        cv2.line(frame,(cx,0),(cx,400),(255,0,0),1)
        cv2.line(frame,(0,cy),(750,cy),(255,0,0),1)
        cv2.drawContours(frame, contours, -1, (0,255,0), 1)

        if cx >= 380 :
            bus.write_byte(address, 2)
            num_cas = 2
        elif cx < 380 and cx > 256:
            bus.write_byte(address, 0)
            num_cas = 0

        elif cx <= 256 :
            bus.write_byte(address, 1)
            num_cas = 1

    else:
        bus.write_byte(address, 3)
        num_cas = 3

    #Affichage a l ecran

    cv2.imshow('frame',frame)
    cv2.waitKey(10)
    

