#include <Wire.h>

#define SLAVE_ADDRESS 0x12 // choix de l'adresse entre 0x03 et 0x77 en hexadecimal
int dataReceived = 0;

void sendData(){Wire.write(dataReceived);}


//configuration de la communication I2C entre les deux cartes
void setup() {
    Serial.begin(9600);// fréquence de communication
    Wire.begin(SLAVE_ADDRESS); // l'arduino est ici définie comme escalve et ne fait que recevoir des ordres de la raspberry configurée comme maître 
    Wire.onReceive(receiveData);
    Wire.onRequest(sendData);
}


void loop() {
    while(Wire.available()) {
        dataReceived = Wire.read();
        sendData(); // c'est ici que l'on retourne à la raspberry la valeur lue par l'arduino qui est tout juste la valeur dataReceived 
}
