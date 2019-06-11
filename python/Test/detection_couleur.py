from collections import OrderedDict
import numpy as np
import cv2
import imutils
import os       #si besoin de parcourir les fichiers
import statistics
from time import time     #si besoin afficher temps
 
# Fonction distance euclidienne
distance_eucli = lambda v1,v2 : (v1[0]-v2[0])**2+(v1[1]-v2[1])**2


# Dictionnaire avec les couleurs des pastilles (espace rgb)
colors = OrderedDict({
                      "noir": (0, 0, 0),
                      "bois": (104,81,49),
                      "jaune": (153,158,136),
                      "orange": (176,97,41),
                      "bleu": (58,102,115),
                      "vert": (117,134,98),
                      "rouge": (158,40,28),
                      "rose": (180,146,173),
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
colors = {          "noir": 0,
                    "bois": 1,
                    "jaune": 2,
                    "orange": 3,
                    "bleu": 4,
                    "vert": 5,
                    "rouge": 6,
                    "rose": 7                               
          }


# Pour chacune des images
for files in os.walk("C:\\Users\\Utilisateur\\Desktop\\test open cv 3 - Copie"):
    f = files[2]
    t = time()   #si besoin afficher temps
    nbim=0       #si besoin afficher temps
    for filename in f:
        if filename[-4:]=='.jpg':
            
            # Charger l'image
            image = cv2.imread(filename)

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
            f = open(filename[:-4]+'.txt','w')
            for i in range(len(colors)):
                f.write(str(xColors[i])+'\n')
                f.write(str(yColors[i])+'\n')
                f.write(str(nbColors[i])+'\n')
            f.close()
            nbim+=1

    #si besoin afficher temps    
    t=time()-t
    print(str(nbim)+' images traitées en '+str(t)+' secondes : '+str(t/nbim)+' s/im')
