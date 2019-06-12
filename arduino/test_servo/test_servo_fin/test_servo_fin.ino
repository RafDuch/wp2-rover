
#include <Servo.h>

//Variable pour stocker l'angle du servomoteur par rapport à son horizontal
int angle = 85;  //initialisation
int angle_base = 0; //offset pour centre la référence de l'angle du servomoteur par rapport à la vertical du rover

// on crée un objet de la librairie servo
Servo servo;


void ecriture (int angle){

  //centrer le offset sur la vertical du rover
  angle = angle - angle_base;

  servo.write(angle);
  }
  


void setup() {

    servo.attach(7); //on choisit arbitrairement le pin PMW 7 pour écrire le signal de commande
    servo.write(angle); //centrer 
    delay(15);
}


void loop() {
ecriture(angle);
}
