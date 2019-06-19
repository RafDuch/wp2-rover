from collections import OrderedDict
import imutils
import statistics
import numpy as np
import cv2
import smbus
import time

class Suiviligne_prog_en_classe :
    
    def _init_(self):
        self.num_cas = 1
        self.bus = smbus.SMBus(1)
        self.address = 0x12
        self.video_capture = cv2.VideoCapture(0)
        self.video_capture.set(3, 750)
        self.video_capture.set(4, 300)
        self.video_capture.set(cv2.CAP_PROP_AUTOFOCUS, 0) # turn the autofocus off
        self.counter = 0
        self.periode = 2
        self.instruction =''
        self.mesure_pastilles = ''
    
    
        # Fonction distance euclidienne
        self.distance_eucli = lambda v1,v2 : (v1[0]-v2[0])**2+(v1[1]-v2[1])**2+(v1[2]-v2[2])**2
        
        
        # Dictionnaire avec les couleurs des pastilles (espace rgb)
        self.colors = OrderedDict({
                            "noir": (47,47,47),
                            "blanc": (155,155,155),
                            "calcaire": (129,125,113),
                            "bois": (104,81,49),
                            "bleu": (58,102,115),
                            "vert": (117,134,98),
                            "rouge": (158,40,28),
                            "rose": (180,146,173),
                            "jaune": (147,163,90),
                            "vertfonce": (43,46,37),
                            "orangefluo":(204,109,55),
                            "orange": (176,97,41),
                            "bleuciel":(123,128,134),
                            "violet": (42,26,65),
                            "marron": (95,68,49)   
                            
                            })
        
        # Allouer de la mémoire pour la conversion de la couleur
        # des pastilles de rgb en L*a*b* 
        self.lab_colors = np.zeros((len(colors), 1, 3), dtype="uint8")
        self.colorNames = []
        
        # Convertir la couleur des pastilles de rgb en L*a*b*         
        for (i, (name, rgb)) in enumerate(colors.items()):
            self.lab_colors[i] = rgb
            self.colorNames.append(name)
            self.lab_colors = cv2.cvtColor(lab_colors, cv2.COLOR_RGB2LAB)
    
        # Dictionnaire avec l'indice des couleurs des pastilles
        self.colors = {     "noir": 0,
                            "blanc": 0,
                            "calcaire": 0,
                            "bois": 1,
                            "bleu": 2,
                            "vert": 3,
                            "rouge": 4,
                            "rose": 5,
                            "jaune": 6,
                            "vertfonce": 7,
                            "orangefluo": 8,
                            "orange": 9,
                            "bleuciel": 10,
                            "violet": 11,
                            "marron": 12
                            
                            }
                            

    
        
    def set_instruction(self, instruction):
        self.instruction = instruction
    

    def start_rover(self) :
        while(True):
            
            # Prises de frames
            self.counter +=1
            self.counter = counter%periode
            ret, img = video_capture.read()
            frame = img[100:350, 0:750]
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
                data = round(255*cx/656)
                bus.write_byte(address, data)


            if self.counter == 0 :
                #Reduire l'image pour mieux detecter les contours
                resized = image #imutils.resize(image, width=640)
                ratio = image.shape[0] / float(resized.shape[0])
        
                # Floute l'image pour mieux detecter les contours
                blurred = cv2.GaussianBlur(resized, (5, 5), 0)
        
                # Convertir en niveau de gris
                gray = cv2.cvtColor(blurred, cv2.COLOR_BGR2GRAY)
        
                # Convertir en L*a*b* 
                lab = cv2.cvtColor(blurred, cv2.COLOR_BGR2LAB)
        
                # Appliquer un seuillage à l'image en niveau de gris
                # pour detecter les contours
                thresh = cv2.threshold(gray, 120, 255, cv2.THRESH_BINARY_INV)[1]
                cnts = cv2.findContours(thresh.copy(), cv2.RETR_EXTERNAL,
                                        cv2.CHAIN_APPROX_SIMPLE)
                cnts = imutils.grab_contours(cnts)
        
                
                # Intitialiser les tableaux donnant l'abscisse, l'ordonnée
                # et le nombre de pixels pour chacune des couleurs de
                # pastilles
                xColors = [ [] for _ in range(len(self.colors)) ]
                yColors = [ [] for _ in range(len(self.colors)) ]
                nbColors = [ 0 for _ in range(len(self.colors)) ]
                
                # Pour chaque contour détecté
                for c in cnts:
                    
                    # Centre du contour et nombre de pixels
                    M = cv2.moments(c)
                    cX = int((M["m10"] / (M["m00"]+0.1) ) * ratio)
                    cY = int((M["m01"] / (M["m00"]+0.1) ) * ratio)
                    nb = M["m00"]
        
                    # Si le nombre de pixels ne correspond pas à une
                    # pastille, on passe au contour suivant
                    if nb>300 and nb<20000 :
                        
                        # Calculer les valeurs L*a*b moyennes du contours
                        mask = np.zeros(lab.shape[:2], dtype="uint8")
                        cv2.drawContours(mask, [c], -1, 255, -1)
                        mask = cv2.erode(mask, None, iterations=2)
                        mean = cv2.mean(lab, mask=mask)[:3]
                    
                        # Calculer la couleur de la pastille la plus proche
                        # de ces valeurs moyennes
                        # On prend la distance euclidienne dans l'espace L*a*b
                        minDist = (np.inf, None)
                        for (i, self.lab_color_pastille) in enumerate(self.lab_colors):
                            d = self.distance_eucli(self.lab_color_pastille[0], mean)
                            if d < minDist[0]:
                                minDist = (d, i)
                        color = self.colorNames[minDist[1]]
                        
                        # Reconverir en coordonnées vraies si l'image a été
                        # réduite
                        c = c.astype("float")
                        c *= ratio
                        c = c.astype("int")
                        cv2.drawContours(image, [c], -1, (0,255,0),2)
                        cv2.putText(image, color + str(nb), (cX, cY), cv2.FONT_HERSHEY_SIMPLEX,0.5,(255,255,255),2)
                        cv2.imshow("image", image)
                        cv2.waitKey(10)
        
                        # Mettre à jour les tableaux donnant l'abscisse,
                        # l'ordonnée et le nombre de pixels pour chacune 
                        # des couleurs de pastilles
                        xColors[self.colors[color]].append(cX)
                        yColors[self.colors[color]].append(cY)
                        nbColors[self.colors[color]] += nb
                        
                    
                # Une fois tous les contours analysés, procéder à
                # un moyennage si la même couleur a été détectée
                # plusieurs fois
                for n in range(len(self.colors)) :
                    if nbColors[n]>0 :
                        xColors[n] = statistics.mean(xColors[n])
                        yColors[n] = statistics.mean(yColors[n])
                    else :
                        xColors[n] = 0
                        yColors[n] = 0
        
                # Enregistrer l'image traitée dans un fichier
                # Sinon, communiquer
                self.mesure_pastilles = ''
                for i in range(len(self.colors)):
                    self.mesure_pastilles += str(xColors[i])+'\r\n'
                    self.mesure_pastilles += str(yColors[i])+'|r\n'
                    self.mesure_pastilles += str(nbColors[i])+'\r\n'

            #Affichage a l ecran
        
            cv2.imshow('frame',frame)
            cv2.waitKey(10)
            
l = Suiviligne_prog_en_classe()
l.start_rover()
