// 4 parametres vit, delay serveur, delay rasp, marge


#include <Wire.h>
#include <Servo.h>

#define SLAVE_ADDRESS 0x12 // choix de l'adresse entre 0x03 et 0x77 en hexadecimal

int dataReceived = 10;  //variable qui porte la commade déplacement de la Raspberry 

// variables nécessaires pour faire fonctionner les moteurs du robot.
int speedPin_M1 = 5;     //Choix de la vitesse M1
int speedPin_M2 = 6;     //Choix de la vitesse M2
int directionPin_M1 = 4;     //Choix du sens de rotation (avant ou arrière) moteur M1
int directionPin_M2 = 7;     //Choix du sens de la rotation (avant ou arrière) pour le moteur M2

int servo_pin = 10;

bool arret_urgence = false; // variable booleene d arret d urgence 

int speed = 80;             //vitesse de base

//Variable pour stocker l'angle du servomoteur par rapport à son horizontal
int angle = 85;  //initialisation à 21 pour que angle_prec soit au minimum et pas en dessous
int flag = 0;
int angle_max = 140;//angle maximal pour le trajet du servomoteur (45 degré de plus que la ref)
int angle_min = 40;//angle minimal pour le trajet du servomoteur 

int timer = 0;

// on crée un objet de la librairie servo
Servo servo;

void sendData(){    //fonction pour écrire vers la Raspberry
    int envoi = dataReceived ;
    Wire.write(envoi);
}


void Direction(int vitgauche,int vitdroite){   //écriture définitive de la consigne des roues 

  analogWrite (speedPin_M2,vitgauche);
  digitalWrite(directionPin_M2,HIGH);           
  analogWrite (speedPin_M1,vitdroite);
  digitalWrite(directionPin_M1,HIGH);        
} 

int ADC_moyenne(int n)  //calcul de la moyenne des valeurs regitrés par le capteur IR
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
  if (ADC_SHARP > 900)
  {arret_urgence = true;}

  else {arret_urgence = false;}
  
return(arret_urgence);
}


void ecriture (){

    if (angle<angle_max and angle>angle_min){
      if (flag == 0){
        angle = angle + 10; 
        servo.write(angle);
      }
      else {
        angle = angle - 10;
        servo.write(angle);
      }
    }
    
    else if (angle>=angle_max){
      flag = 1;
      angle = angle_max - 10;
      servo.write(angle);
    }
    
    else if (angle<=angle_min){
      flag =0;
      angle = angle_min + 10;
      servo.write(angle);
    }
}


void receiveData(int byteCount){

    if (arreturgence() == false) {
      timer+=1;
      if (timer >= 500){
      timer = 0;
      ecriture();} 
  
    while(Wire.available()) {
        dataReceived = Wire.read();
        
        if (dataReceived == 0) {  
        Direction(speed-10,speed-10);
        }


        else if (dataReceived == 1) {
        Direction(55,speed); 
        }

        else if (dataReceived == 2) {
        Direction(speed,55);
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
      Direction (0,0);
    }
  
  else {Direction (0,0);}
    
 }
 


//configuration de la communication I2C entre les deux cartes
void setup() {
    Serial.begin(9600); // fréquence de communication
    Wire.begin(SLAVE_ADDRESS); // l'arduino est ici définie comme escalve et ne fait que recevoir des ordres de la raspberry configurée comme maître 
    Wire.onReceive(receiveData);
    Wire.onRequest(sendData);
    pinMode (speedPin_M1, OUTPUT);
    pinMode (speedPin_M2, OUTPUT);
    pinMode (directionPin_M1, OUTPUT);
    pinMode (directionPin_M2, OUTPUT);
    servo.attach(10); //on choisit arbitrairement le pin PMW 7 pour écrire le signal de commande
    servo.write(angle); //centrer 
}



void loop() {
  receiveData(0);
}
