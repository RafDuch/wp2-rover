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

# Fonction distance euclidienne
distance_eucli = lambda v1,v2 : (v1[0]-v2[0])**2+(v1[1]-v2[1])**2


# Dictionnaire avec les couleurs des pastilles (espace rgb)
colors = OrderedDict({
                      "noir": (0, 0, 0),
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
lab_colors = np.zeros((len(colors), 1, 3), dtype="uint8")
colorNames = []
 
# Convertir la couleur des pastilles de rgb en L*a*b* 
for (i, (name, rgb)) in enumerate(colors.items()):
    lab_colors[i] = rgb
    colorNames.append(name)
lab_colors = cv2.cvtColor(lab_colors, cv2.COLOR_RGB2LAB)

# Dictionnaire avec l'indice des couleurs des pastilles
colors = {            "noir": 0,
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

t0 = time.time()
old_t=t0
counter =0
periode = 2

while(True):
    # Prises de frames
    counter +=1
    counter = counter%periode
    ret, img = video_capture.read()
    frame = img[150:350, 0:750]
    image = img.copy()
    t1= time.time()
    delta = t1- old_t
    t=str(t1-t0).split('.')
    t[0]='0'*(4-len(t[0]))+t[0]
    t[1]=t[1][:6]+'0'*(6-len(t[1][:6]))
    date = t[0] + t[1]
    
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
        
    if counter == 0 :
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
        xColors = [ [] for _ in range(len(colors)) ]
        yColors = [ [] for _ in range(len(colors)) ]
        nbColors = [ 0 for _ in range(len(colors)) ]
        
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
                # On prend la distance euclidienne dans le plan a*b
                minDist = (np.inf, None)
                for (i, lab_color_pastille) in enumerate(lab_colors):
                    d = distance_eucli(lab_color_pastille[0][1:], mean[1:])
                    if d < minDist[0]:
                        minDist = (d, i)
                color = colorNames[minDist[1]]
                
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
                xColors[colors[color]].append(cX)
                yColors[colors[color]].append(cY)
                nbColors[colors[color]] += nb
                
            
        # Une fois tous les contours analysés, procéder à
        # un moyennage si la même couleur a été détectée
        # plusieurs fois
        for n in range(len(colors)) :
            if nbColors[n]>0 :
                xColors[n] = statistics.mean(xColors[n])
                yColors[n] = statistics.mean(yColors[n])
            else :
                xColors[n] = 0
                yColors[n] = 0

        # Enregistrer l'image traitée dans un fichier
        # Sinon, communiquer
        f = open("im" + date+'.txt','w')
        for i in range(len(colors)):
            f.write(str(xColors[i])+'\n')
            f.write(str(yColors[i])+'\n')
            f.write(str(nbColors[i])+'\n')
        f.close()
    if delta > 0.1 :
        old_t =t1
        f2 = open("tx" + date+'.txt','w')
        f2.write(str(num_cas))
        f2.close()
    #Affichage a l ecran

    #cv2.imshow('frame',frame)
    #cv2.waitKey(10)
    