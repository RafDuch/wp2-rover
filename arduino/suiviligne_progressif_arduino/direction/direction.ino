#include <Wire.h>

#define SLAVE_ADDRESS 0x12 // choix de l'adresse entre 0x03 et 0x77 en hexadecimal
int dataReceived = 0;
float x = 0.0;


// variables nécessaires pour faire fonctionner les moteurs du robot.
int speedPin_M1 = 5;     //Choix de la vitesse M1
int speedPin_M2 = 6;     //Choix de la vitesse M2
int directionPin_M1 = 4;     //Choix du sens de rotation (avant ou arrière) moteur M1
int directionPin_M2 = 7;     //Choix du sens de la rotation (avant ou arrière) pour le moteur M2

bool arret_urgence = false; // variable booléenne d'arrêt d'urgence

int vitG = 0;
int vitD = 0;
int data = 0;
int vit= 100;
int data_max = 180;
int data_mil = data_max/2;




void sendData() {
  int envoi =  dataReceived ;
  Wire.write(envoi);
}

int ADC_moyenne(int n)
{
  long somme = 0;
  for (int i = 0; i < n; i++)
  {
    somme = somme + analogRead(A0);
  }
  return ((int)(somme / n));
}


bool arreturgence(){
  int ADC_SHARP = ADC_moyenne(20); 
  if (ADC_SHARP > 600)
  {arret_urgence = true;}
  else
  {arret_urgence = false;}
  return(arret_urgence);}


void Direction(int vitgauche, int vitdroite) {
  analogWrite (speedPin_M2, vitgauche);
  analogWrite (speedPin_M1, vitdroite);
  digitalWrite(directionPin_M1, HIGH);
  digitalWrite(directionPin_M2, HIGH);
}


void receiveData(int bytecount) {
  arret_urgence = arreturgence();
  if (arret_urgence == false) {

    while (Wire.available()) {
      data = Wire.read();//varie de 0 à 255 avec donc le milieu de l'image à 127. Cela revient à prendre en compte un pixel sur 3 dans l'image de départ
      
      if (data < data_mil) {
          
            //data est la valeur comprise entre 0 et 255 représentant l'éloignement par rapport à l'origine en pixel ramené sur un octet...
            vitG = abs (vit - data);
            vitD = vit + data;
            if (vitD > 255) {
              vitD = 255;
              vitD = 0;
            }

            Direction(vitG, vitD);
         }
         else {
          data = data - data_mil;
          vitG = vit + data;
          vitD = abs (vit - data);
            if (vitG > 255) {
              vitG = 255;
              vitD = 0;
            }

            Direction(vitG, vitD);
         }
     }
  }
         
      else {
        Direction (0, 0);
      }
}


//configuration de la communication I2C entre les deux cartes
void setup() {
  Serial.begin(9600);// fréquence de communication
  Wire.begin(SLAVE_ADDRESS); // l'arduino est ici définie comme escalve et ne fait que recevoir des ordres de la raspberry configurée comme maître
  Wire.onReceive(receiveData);
  Wire.onRequest(sendData);
  pinMode (speedPin_M1, OUTPUT);
  pinMode (speedPin_M2, OUTPUT);
  pinMode (directionPin_M1, OUTPUT);
  pinMode (directionPin_M2, OUTPUT);
}

void loop() {receiveData(0);}
