#include <Wire.h>

#define SLAVE_ADDRESS 0x12 // choix de l'adresse entre 0x03 et 0x77 en hexadecimal
#include <Servo.h>

// variables nécessaires pour faire fonctionner les moteurs du robot.
int speedPin_M1 = 5;     //Choix de la vitesse M1
int speedPin_M2 = 6;     //Choix de la vitesse M2
int directionPin_M1 = 4;     //Choix du sens de rotation (avant ou arrière) moteur M1
int directionPin_M2 = 7;     //Choix du sens de la rotation (avant ou arrière) pour le moteur M2
int servo_pin = 10;

bool arret_urgence = false; // variable booléenne d'arrêt d'urgence

int vitG = 0;
int vitD = 0;
int data = 0;
int vit = 110;
int data_max = 100;
int data_mil = data_max/2;

int cnt = 0;


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

int ADC_moyenne(int n)
{
  long somme = 0;
  for (int i = 0; i < n; i++)
  {
    somme = somme + analogRead(A0);
  }
  return ((int)(somme / n));
}


bool  arreturgence(){
  int ADC_SHARP = ADC_moyenne(20); 
  if (ADC_SHARP > 600)
  {return true ;}
  else
  {return false;}
}


int ecriture (int angle, int angle_prec){

    if (angle<angle_max && angle>angle_min){
      if (angle>angle_prec){
        angle_prec = angle;
        angle = angle + 10; 
        servo.write(angle);
      }
      else {
        angle_prec = angle;
        angle = angle - 10;
        servo.write(angle);
      }
    }
    
    else if (angle>=angle_max){
      angle_prec = angle_max;
      angle = angle_max - 10;
      servo.write(angle);
    }
    
    else if (angle<=angle_min){
      angle_prec = angle_min;
      angle = angle_min + 10;
      servo.write(angle);
    }
    return(angle, angle_prec);
}


void Direction(int vitgauche, int vitdroite) {
  analogWrite (speedPin_M2, vitgauche);
  analogWrite (speedPin_M1, vitdroite);
  digitalWrite(directionPin_M1, HIGH);
  digitalWrite(directionPin_M2, HIGH);
}


void receiveData(int bytecount) {
  
  if (arreturgence() == false) {

 cnt +=1;
  if (cnt >= 1000){
    cnt = 0;
    temp_angle,temp_angle_prec = ecriture(angle,angle_prec); //écrire le nouveau angle vers le servo en function du passé, DEPLACEMENT STATIQUE PAS DYNAMIQUE (balayage périodique qui ne dépend pas de l'environnement)
    angle = temp_angle;
    angle_prec = temp_angle_prec;
  }

    while (Wire.available()) {
      //cnt+=1;
      //t_prec = millis();
      //if (cnt >= 500){//t_prec - t_prec_servo > 15){
      //cnt = 0;
      //temp_angle,temp_angle_prec = ecriture(angle,angle_prec); //écrire le nouveau angle vers le servo en function du passé, DEPLACEMENT STATIQUE PAS DYNAMIQUE (balayage périodique qui ne dépend pas de l'environnement)
      //ecriture(angle,angle_prec);
      //angle = temp_angle;
      //angle_prec = temp_angle_prec;
      //t_prec_servo = millis();
      
      
      data = Wire.read();//varie de 0 à 255 avec donc le milieu de l'image à 127. Cela revient à prendre en compte un pixel sur 3 dans l'image de départ
      
      if (data < data_mil) {
        
          
            //data est la valeur comprise entre 0 et 255 représentant l'éloignement par rapport à l'origine en pixel ramené sur un octet...
            vitG = vit - data;
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
          vitD = vit - data;
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
  pinMode (speedPin_M1, OUTPUT);
  pinMode (speedPin_M2, OUTPUT);
  pinMode (directionPin_M1, OUTPUT);
  pinMode (directionPin_M2, OUTPUT);
  //pinMode (servo_pin,OUTPUT);
  servo.attach(10); //on choisit arbitrairement le pin PMW 10 pour écrire le signal de commande
  servo.write(angle); //centrer 
}

void loop() {
  receiveData(0);
}
