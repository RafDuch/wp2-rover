// 4 parametres vit, delay serveur, delay rasp, marge


#include <Wire.h>

#define SLAVE_ADDRESS 0x12 // choix de l'adresse entre 0x03 et 0x77 en hexadecimal
int dataReceived = 0;



// variables nécessaires pour faire fonctionner les moteurs du robot.
int speedPin_M1 = 5;     //Choix de la vitesse M1
int speedPin_M2 = 6;     //Choix de la vitesse M2
int directionPin_M1 = 4;     //Choix du sens de rotation (avant ou arrière) moteur M1
int directionPin_M2 = 7;     //Choix du sens de la rotation (avant ou arrière) pour le moteur M2

bool arret_urgence = false; // variable booleene d arret d urgence 

int VG = 200;
int VD = 200;

int speed = 80;


void sendData(){
    int envoi = dataReceived ;
    Wire.write(envoi);
}


void Direction(int vitgauche,int vitdroite){   

  VG = vitgauche;
  VD = vitdroite;     
  analogWrite (speedPin_M2,VG);
  digitalWrite(directionPin_M2,HIGH);           
  analogWrite (speedPin_M1,VD);
  digitalWrite(directionPin_M1,HIGH);        
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

void receiveData(int byteCount){
  arret_urgence= arreturgence();
  if (arret_urgence == false) { 
  
    while(Wire.available()) {
        dataReceived = Wire.read();
        Serial.println(dataReceived);

        
        if (dataReceived == 0) {  
        Direction(speed-10,speed-10);
        }


        else if (dataReceived == 1) {
        Direction(50,speed); 
        }

        else if (dataReceived == 2) {
        Direction(speed,50);
        }

        else if (dataReceived == 4) {// ordre d arret
        Direction(0,0);  
        }

        else if (dataReceived == 5) {//instruction d arret par le  serveur
        Direction(0,0);
        } 
        
        else if (dataReceived == 6) {// ordre ralentir, on met min vit
        Direction(70,70);  
        }
        else if (dataReceived == 7) {// ordre ralentir, mais on tourne a droite
        Direction(70,0);  
        }
        else if (dataReceived == 8) {// ordre ralentir, mais on tourne a gauche
        Direction(0,70);  
        }

    }
  }
  else {Direction (0,0);}
    
 }
bool arreturgence(){
    int ADC_SHARP = ADC_moyenne(20);
  if (ADC_SHARP > 900)
  {arret_urgence = true;}

  else {arret_urgence = false;}
  
return(arret_urgence);
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


void loop() {
receiveData(0);
}
