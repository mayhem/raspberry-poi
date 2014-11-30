#include <FreeSixIMU.h>
#include <FIMU_ADXL345.h>
#include <FIMU_ITG3200.h>
#include <Wire.h>

uint8_t red_pin = 10;
uint8_t blue_pin = 9;
uint8_t green_pin = 11;

float angles[3]; // yaw pitch roll

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

    sixDOF.getEuler(angles);

    for(i = 0; i < 3; i++)
    {
        angles[i] /= 360;
        angles[i] += .5;
        angles[i] *= 255;
    }

    analogWrite(red_pin, int(angles[0]));
    analogWrite(green_pin, int(angles[1]));
    analogWrite(blue_pin, int(angles[2]));

    Serial.print(angles[0]);
    Serial.print(",");  
    Serial.print(angles[1]);
    Serial.print(",");
    Serial.println(angles[2]);

    delay(50); 
}
