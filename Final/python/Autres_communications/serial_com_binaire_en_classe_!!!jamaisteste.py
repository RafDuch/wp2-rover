
##pour le suivi de ligne
import numpy as np
import cv2
import serial
import time

## pour la communication 
import types
import socket
import sys
import selectors
from _thread import start_new_thread
import subprocess



class TestMerge: #todo : l appeler du nom du fichier et donc modifier les autres fichiers en consequence

    def __init__(self, main_rover_merge ):
        self.port_serial = "/dev/ttyACM0"
        self.rate = 9600

        self.instruction = ''
        self.numero_cas=0
        #les set pour la partie communication client
        self.sel = selectors.DefaultSelector()
        self.msgOut = {}
        self.msgOutBox = []
        self.ip_server = '192.168.43.160'
        self.port = 65432
        self.msg = ''
        self.msgSent = True
        self.msgKeys = ['roverID','msgType','dataSize','data']
        self.main_rove_rmerge = main_rover_merge
        
    def fill_box(self):
        #while True:
            #subprocess.run(["fswebcam", "-r", "1280x720", "--no-banner", "img.jpg"])
            #f1 000= open('img.jpg', 'rb')
            f2 = open('data.txt', 'rb')
            #data1 = f1.read()
            data1 = b'e'
            data2 = f2.read()
            dataSize1 = str(len(data1))
            dataSize2 = str(len(data2))
            while len(dataSize1) < 9:
                dataSize1 = '0' + dataSize1
            while len(dataSize2) < 9:
                dataSize2 = '0' + dataSize2
            self.msgOutBox = [
                {'roverID': b'000000004', 'msgType': b'000000001', 'dataSize': dataSize1.encode('utf-8'), 'data': data1},
                {'roverID': b'000000004', 'msgType': b'000000000', 'dataSize': dataSize2.encode('utf-8'), 'data': data2}]
            #f1.close()
            f2.close()
            with open('test.txt','wb') as f3:
                f3.write(data1)
            time.sleep(5)
            
    def connect(self, serverIP, serverPort):
        server_addr = (serverIP, serverPort)
        print('Connecting to', server_addr)
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.setblocking(False)
        s.connect_ex(server_addr)
        events = selectors.EVENT_READ | selectors.EVENT_WRITE
        self.sel.register(s, events, self.msgOutBox)
        print('Connected', server_addr)



    def start_connection(self):
        #start_new_thread(self.fill_box, ())
        # self.fill_box() on le met à la main avant 
        self.connect(self.ip_server, self.port)
        #while True:
        events = self.sel.select(timeout=None)
        for key, mask in events:
            s = key.fileobj
            if len(self.msgOut) == 0 and len(self.msgOutBox) > 0:
                self.msgOut = self.msgOutBox.pop()
                i = 0
                self.msgSent = True
            if mask & selectors.EVENT_READ:
                instruction = s.recv(2048).decode("utf-8")
                self.main_rover.sendInstruction(instruction)

            if mask & selectors.EVENT_WRITE:
                if len(self.msgOut) > 0:
                    if self.msgSent == True:
                        self.msg = self.msgOut[self.msgKeys[i]]
                        i += 1
                    try:      
                        sent = s.send(self.msg)
                        self.msg = self.msg[sent:]
                        if len(self.msg) == 0:
                            self.msgSent = True
                        else:
                            self.msgSent = False
                    except socket.error:
                        print('Disconnected')
                        connected = False
                        s = socket.socket()
                        #while not connected:
                        if not connected :
                            try:
                                self.connect(self.ip_server, self.port)
                                connected = True
                                # time.sleep(5)
                            except socket.error:
                                G=0# juste pour avoir une instruction apres except
                                #time.sleep(1)
                            #fin du while not connected
                    if i == 4 and self.msgSent == True:
                        self.msgOut = {}
                        i = 0
        #Fin du while True normalement
#suivi de ligne par la suite 
    def get_numeoro_cas(self):
        return (self.numero_cas)
        
    def set_instruction(self, instruction):
        self.instruction = instruction

    
    def passage_noir(self):
        # Prises de frames
        video_capture = cv2.VideoCapture(0)
        video_capture.set(3, 750)
        video_capture.set(4, 300)
        ret, img = video_capture.read()
        frame = img[150:350, 0:750]
        #TODO cv2.imwrite('img.jpg', frame)
        # Passage en niveau de gris
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        # Filtre gaussien
        blur = cv2.GaussianBlur(gray,(5,5),0)
        # Passage en noir et blanc par seuillage
        ret,thresh1 = cv2.threshold(blur,60,255,cv2.THRESH_BINARY_INV)
        return(img, thresh1)
    
    
    def contours_filtrage(self, img, thresh1) :
        # Enleve les accidentelles detections de ligne
        mask = cv2.erode(thresh1, None, iterations=2)
        mask = cv2.dilate(mask, None, iterations=2)
        # Trouver les contours
        _,contours,hierarchy = cv2.findContours(mask.copy(), 1, cv2.CHAIN_APPROX_NONE)
        return(contours)
      
            
    def lignes(self, contours) :
        # Trouver les plus gros contours
        if len(contours) > 0:
            c = max(contours, area=cv2.contourArea)
            M = cv2.moments(c)
            cx = int(M['m10']/M['m00'])
            cy = int(M['m01']/M['m00'])
            cv2.line(frame,(cx,0),(cx,400),(255,0,0),1)
            cv2.line(frame,(0,cy),(750,cy),(255,0,0),1)
            cv2.drawContours(frame, contours, -1, (0,255,0), 1)
            return(cx)
        else :
            return (-1)


    def ordre(self, contours) :
        cx = self.lignes(contours)
        s1 = serial.Serial(self.port, self.rate)
        s1.flushInput()
        if cx != (-1) :
        
            if self.instruction == "arreter":
                self.numero_cas=4
                s1.write(4)

            else:
                if cx >= 380 and self.instruction == "ralentir":
                    self.numero_cas=7
                    s1.write(7)
                elif cx >= 380 :
                    self.numero_cas=2
                    s1.write(2)
                if cx < 380 and cx > 256 and self.instruction == "ralentir" :
                    self.numero_cas=6
                    s1.write(6)
                elif cx < 380 and cx > 256 :
                    self.numero_cas=0
                    s1.write(0)

                if cx <= 256 and self.instruction == "ralentir":
                    self.numero_cas=8
                    s1.write(8)
                elif cx <= 256 :
                    self.numero_cas=1
                    s1.write(1)
        else:
            self.numero_cas=6
            s1.write(6)
            
        # Affichage a l ecran
        cv2.imshow('frame',frame)
        cv2.waitKey(10)

    def start_rover_connexion (self):
        tpstot = 2 # valeur sup à 5 pour que la première fois on rentre dans la boucle avec la connexion
        while True:
            tt = time.time()
            (img, thresh1) = self.passage_noir()
            contours = self.contours_filtrage(img, thresh1)
            self.ordre(contours)
            if tpstot >= 2 :#temps de traitement de l'image
                self.fillbox()
                #tt = time.time()
                self.start_connection()
                tpstot = 0
            else :
                self.start_connexion()
        tps = time.time()-tt
        tpstot+=tps


l = TestMerge()
l.start_rover_connexion()