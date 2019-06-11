// 4 parametres vit, delay serveur, delay rasp, marge


int dataReceived = 0;



// variables nécessaires pour faire fonctionner les moteurs du robot.
int speedPin_M1 = 5;     //Choix de la vitesse M1
int speedPin_M2 = 6;     //Choix de la vitesse M2
int directionPin_M1 = 4;     //Choix du sens de rotation (avant ou arrière) moteur M1
int directionPin_M2 = 7;     //Choix du sens de la rotation (avant ou arrière) pour le moteur M2

bool arreturgence = false; // variable booleene d arret d urgence 

int VG = 200;
int VD = 200;

int speed = 105;


void sendData(){
    int envoi = dataReceived ;
    Serial.write(envoi);
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


bool arreturgence(){
  int ADC_SHARP = ADC_moyenne(20);
  
  if (ADC_SHARP > 900)
  {arreturgence = true;}

  else
  {arreturgence = false;}
  
  return(arreturgence);
}

void receiveData(){
  arreturgence = arreturgence();
  if (arreturgence == false) { 
  
    while(Serial.available()) {
        dataReceived = Serial.read();
              
        if (dataReceived == 0) {  
        Direction(speed,speed);
        }

        else if (dataReceived == 1) {
        Direction(0,speed); 
        }

        else if (dataReceived == 2) {
        Direction(speed,0);
        }

        else if (dataReceived == 4) {// ordre s arrete
        Direction(0,0);  
        }

        else if (dataReceived == 5) {//instruction d arret par le  serveur
        Direction(0,0);
        } 
        
        else if (dataReceived == 6) {// ordre ralentrir, on met min vit
        Direction(70,70);  
        }
        else if (dataReceived == 7) {// ordre ralentrir, mais on tourne a droite
        Direction(70,0);  
        }
        else if (dataReceived == 8) {// ordre ralentrir, mais on tourne a gauche
        Direction(0,70);  
        }
    }
  }
  else {
    Direction (0,0);}

}

//configuration de la communication I2C entre les deux cartes
void setup() {
    Serial.begin(9600);// fréquence de communication
    pinMode (speedPin_M1, OUTPUT);
    pinMode (speedPin_M2, OUTPUT);
    pinMode (directionPin_M1, OUTPUT);
    pinMode (directionPin_M2, OUTPUT);
}


void loop() {
receiveData();
}
