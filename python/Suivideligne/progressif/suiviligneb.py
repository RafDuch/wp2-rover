import numpy as np
import cv2
import smbus
import time


bus = smbus.SMBus(1)
address = 0x12
video_capture = cv2.VideoCapture(0)
video_capture.set(3, 750)
video_capture.set(4, 300)

while(True):
    # Prises des frames
    ret, img = video_capture.read()
    frame = img[150:350, 0:750]
    
    # Passage en niveaux de gris
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    # Filtre Gaussien
    blur = cv2.GaussianBlur(gray,(5,5),0)

    # Passage en noir et blanc par sueil
    ret,thresh1 = cv2.threshold(blur,60,255,cv2.THRESH_BINARY_INV)

    # Enleve les detections de ligne accidentelles
    mask = cv2.erode(thresh1, None, iterations=2)
    mask = cv2.dilate(mask, None, iterations=2)
    
    # Determine les contours des "taches noires"
    _,contours,hierarchy = cv2.findContours(mask.copy(), 1, cv2.CHAIN_APPROX_NONE)
    
    # Trouver les plus gros contours (s'il y en a)
    
    if len(contours) > 0:
        c = max(contours, key=cv2.contourArea)
        M = cv2.moments(c)
        cx = int(M['m10']/M['m00'])
        cy = int(M['m01']/M['m00'])
        cv2.line(frame,(cx,0),(cx,400),(255,0,0),1)
        cv2.line(frame,(0,cy),(750,cy),(255,0,0),1)
        cv2.drawContours(frame, contours, -1, (0,255,0), 1)
        data = round(255*cx/656)
        bus.write_byte(address, data)
        #bus.write_byte(address, pos_mil)
        print(bus.read_byte(address))
        #print(bus.read_byte(address))

        #Display the resulting frame
        cv2.imshow('frame',frame)
        cv2.waitKey(10)

    else:
        bus.write_byte(address, -1)
        #Display the resulting frame
        cv2.imshow('frame',frame)
        cv2.waitKey(10)
        
        
        
 
