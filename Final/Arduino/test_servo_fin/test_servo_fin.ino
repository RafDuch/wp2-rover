#include <Servo.h>

int servo_pin = 10;

bool arret_urgence = false; // variable booléenne d'arrêt d'urgence

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


void balayage() {

    if (arreturgence() == false) {
      timer+=1;
      if (timer >= 500){
        timer = 0;
        ecriture();} 
    }
}


void setup() {
  servo.attach(10); //on choisit arbitrairement le pin PMW 10 pour écrire le signal de commande
  servo.write(angle); //centrer 
}

void loop() {
  balayage();
}
