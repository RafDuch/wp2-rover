import numpy as np
import cv2
import smbus
import time


class SuiviLigne:

    def __init__(self):
        self.bus = smbus.SMBus(1)
        self.address = 0x12
        self.video_capture = cv2.VideoCapture(0)
        self.video_capture.set(3, 750)
        self.video_capture.set(4, 300)
        self.instruction = ''
        self.numero_cas=0
        self.form = ""

    def get_numeoro_cas(self):
        return (self.numero_cas)

    def get_form(self):
        return (self.form)
        
    def set_instruction(self, instruction):
        self.instruction = instruction


    def start_rover(self):
        while True:
            # Prises de frames
            ret, img = self.video_capture.read()
            frame = img[150:350, 0:750]
            #TODO cv2.imwrite('img.jpg', frame)

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
            
            # Trouver la forme du contour
            
            for cnt in contours :
                approx = cv2.approxPolyDP(cnt, 0.1*cv2.arcLength(cnt,True), True)
                if len(approx) == 3 :
                    self.form = "triangle"
                elif len(approx)==5 :
                    self.form = "pentagon"
                elif len(approx) == 6 :
                    self.form = "hexagon"
                else :
                    self.form = "other"
                
                print(form)
                
                    
            # Trouver les plus gros contours
            if len(contours) > 0:

                c = max(contours, key=cv2.contourArea)

                M = cv2.moments(c)

                cx = int(M['m10']/M['m00'])

                cy = int(M['m01']/M['m00'])

                cv2.line(frame,(cx,0),(cx,400),(255,0,0),1)

                cv2.line(frame,(0,cy),(750,cy),(255,0,0),1)

                cv2.drawContours(frame, contours, -1, (0,255,0), 1)

                if self.instruction == "arreter":
                    self.numero_cas=4
                    self.bus.write_byte(self.address, 4)

                else:
                    if cx >= 380 and self.instruction == "ralentir":
                        self.numero_cas=7
                        self.bus.write_byte(self.address, 7)
                    elif cx >= 380 :
                        self.numero_cas=2
                        self.bus.write_byte(self.address, 2)
                    if cx < 380 and cx > 256 and self.instruction == "ralentir" :
                        self.numero_cas=6
                        self.bus.write_byte(self.address, 6)
                    elif cx < 380 and cx > 256 :
                        self.numero_cas=0
                        self.bus.write_byte(self.address, 0)

                    if cx <= 256 and self.instruction == "ralentir":
                        self.numero_cas=8
                        self.bus.write_byte(self.address, 7)
                    elif cx <= 256 :
                        self.numero_cas=1
                        self.bus.write_byte(self.address, 1)
            else:
                self.numero_cas=6
                self.bus.write_byte(self.address, 6)
            
                
                #     #Affichage a l ecran
            cv2.imshow('frame',frame)
            cv2.waitKey(10)

l = SuiviligneBinaire()
l.start_rover()
