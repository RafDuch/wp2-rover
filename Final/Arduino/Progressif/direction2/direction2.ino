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

int  vitG = 0;
int  vitD = 0;
int data = 0;
int  vit = 110;
int data_max = 180;
int data_mil = data_max/2;
int timer = 0;


//Variable pour stocker l'angle du servomoteur par rapport à son horizontal

int angle = 85;  //initialisation à 21 pour que angle_prec soit au minimum et pas en dessous
int flag = 0;
int angle_max = 140;//angle maximal pour le trajet du servomoteur (45 degré de plus que la ref)
int angle_min = 40;//angle minimal pour le trajet du servomoteur 

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
  if (ADC_SHARP > 900)
  {return true ;}
  else
  {return false;}
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


void Direction(int vitgauche, int vitdroite) {
  analogWrite (speedPin_M2, vitgauche);
  analogWrite (speedPin_M1, vitdroite);
  digitalWrite(directionPin_M1, HIGH);
  digitalWrite(directionPin_M2, HIGH);
}


void receiveData(int bytecount) {


    if (arreturgence() == false) {
      timer+=1;
      if (timer >= 500){
      timer = 0;
      ecriture();} 



    while (Wire.available()) {  
      
      data = Wire.read();//varie de 0 à 255 avec donc le milieu de l'image à 127. Cela revient à prendre en compte un pixel sur 3 dans l'image de départ 
      
      if (data < data_mil) {
        
            data  = data ;
            //data est la valeur comprise entre 0 et 255 représentant l'éloignement par rapport à l'origine en pixel ramené sur un octet...
            vitG = vit - data;
            vitD = vit + data;

            if (vitD >= 255 or data >= vit) {
              vitD = 255;
              vitD = 0;
            }

            Direction(vitG, vitD);
         }
         
         else {
          data = data - data_mil;
          vitG = vit + data;
          vitD = vit - data;

            if (vitG >= 255 or data>= vit ) {
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
  //servo.attach(10); //on choisit arbitrairement le pin PMW 10 pour écrire le signal de commande
  //servo.write(angle); //centrer 
}

void loop() {
  receiveData(0);
}
