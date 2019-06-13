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

bool arret_urgence = false; // variable booleene d arret d urgence 

int speed = 80;             //vitesse de base

//Variable pour stocker l'angle du servomoteur par rapport à son horizontal
long t_servo = 0;
int t_prec = 0;
long t_prec_servo = 0;
int angle = 21;  //initialisation à 21 pour que angle_prec soit au minimum et pas en dessous
int angle_prec = angle - 1;  //connaitre la direction d'avancement du balayage
int temp_angle;
int temp_angle_prec;
int angle_max = 170;//angle maximal pour le trajet du servomoteur (45 degré de plus que la ref)
int angle_min = 20;//angle minimal pour le trajet du servomoteur 

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

int ecriture (int angle, int angle_prec, long t_prec_servo, long t_servo){

    if (angle<angle_max && angle>angle_min){
      if (angle>angle_prec){
        angle_prec = angle;
        angle = angle + 1; 
        servo.write(angle);
      }
      else {
        angle_prec = angle;
        angle = angle - 1;
        servo.write(angle);
      }
    }
    
    else if (angle=angle_max){
      angle_prec = angle_max;
      angle = angle - 1;
      servo.write(angle);
    }
    
    else if (angle=angle_min){
      angle_prec = angle_min;
      angle = angle + 1;
      servo.write(angle);
    }
    return(angle, angle_prec);
}

void receiveData(int byteCount){
  arret_urgence = arreturgence();
  
  if (arret_urgence == false) { 
  
    while(Wire.available()) {
        dataReceived = Wire.read();
        t_prec = millis();
        if (t_prec - t_prec_servo > 15){
        temp_angle,temp_angle_prec = ecriture(angle,angle_prec, t_prec_servo, t_servo); //écrire le nouveau angle vers le servo en function du passé, DEPLACEMENT STATIQUE PAS DYNAMIQUE (balayage périodique qui ne dépend pas de l'environnement)
        angle = temp_angle;
        angle_prec = temp_angle_prec;
        t_prec_servo = millis();
        }
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
    Serial.begin(9600); // fréquence de communication
    Wire.begin(SLAVE_ADDRESS); // l'arduino est ici définie comme escalve et ne fait que recevoir des ordres de la raspberry configurée comme maître 
    Wire.onReceive(receiveData);
    Wire.onRequest(sendData);
    pinMode (speedPin_M1, OUTPUT);
    pinMode (speedPin_M2, OUTPUT);
    pinMode (directionPin_M1, OUTPUT);
    pinMode (directionPin_M2, OUTPUT);
    servo.attach(7); //on choisit arbitrairement le pin PMW 7 pour écrire le signal de commande
    servo.write(angle); //centrer 
    delay(15);
}


void loop() {
  receiveData(0);
}
