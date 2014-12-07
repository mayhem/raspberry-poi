#include <FreeSixIMU.h>
#include <FIMU_ADXL345.h>
#include <FIMU_ITG3200.h>

#include <Wire.h>

uint8_t red_pin = 10;
uint8_t blue_pin = 9;
uint8_t green_pin = 11;

float angles[3]; // yaw pitch roll
float eu_angles[3];

// Set the FreeSixIMU object
FreeSixIMU sixDOF = FreeSixIMU();

void setup() 
{ 
    Serial.begin(38400);
    Wire.begin();

    delay(5);
    sixDOF.init(); //begin the IMU
    delay(5);
}

void loop() 
{ 
    uint8_t i; 

    sixDOF.getEuler(eu_angles);

    Serial.print(int(eu_angles[0]));
    Serial.print(",");  
    Serial.print(int(eu_angles[1]));
    Serial.print(",");
    Serial.println(int(eu_angles[2]));    
}
