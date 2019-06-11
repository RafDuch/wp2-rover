
#include <Arduino.h>
#include <math.h>
#include <Wire.h>
#include <Wire.cpp>

#ifdef MODEL
#include "i2c_buffer.h"
#else
#define BUFFER_SIZE 12
#endif

#define SLAVE_ADDR 0x12

unsigned char rbuf[BUFFER_SIZE];

extern "C" void receiveData(int bytes){
    
    int i;
    
    if(bytes<=BUFFER_SIZE)
    {
        for(i=0;i<BUFFER_SIZE;i++) {
            if(Wire.available()) {
                rbuf[i] = Wire.read();
            }
        }
    }
    else // FOR DEBUG purpose
    {
        rbuf[0] = (unsigned char)bytes;
        for(i=1;i<bytes;i++) {
            rbuf[i] = 0;
        }
    }
    
    
}

extern "C" void initI2C(){
    
    Wire.begin(SLAVE_ADDR); //join i2c bus as slave
    Wire.onReceive(receiveData);
    
}

extern "C" void readFromI2C(unsigned char *Receive){
    
    for(int i=0;i<BUFFER_SIZE;i++){
        Receive[i] = rbuf[i];
    }
    
}
