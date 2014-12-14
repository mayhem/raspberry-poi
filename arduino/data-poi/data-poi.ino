#include <FreeSixIMU.h>
#include <FIMU_ADXL345.h>
#include <FIMU_ITG3200.h>
#include <Wire.h>
#include "sin.h"

uint8_t red_pin = 10;
uint8_t blue_pin = 9;
uint8_t green_pin = 11;

const float TWOPI = M_PI * 2.0;

// Set the FreeSixIMU object
FreeSixIMU sixDOF = FreeSixIMU();

void led_color(uint8_t r, uint8_t g, uint8_t b)
{
    analogWrite(red_pin, r);
    analogWrite(green_pin, g);
    analogWrite(blue_pin, b);    
}

void startup(void)
{
    uint8_t i;
    uint8_t col1[3] = { 128, 70, 0 };
    uint8_t col2[3] = { 128, 0, 128 };
    
    for(i = 0; i < 10; i++)
    {
        led_color(128, 70, 0);
        delay(100);
        led_color(128, 0, 128);
        delay(100);
    }    
    led_color(0, 0, 0);    
}

float sin(float value)
{
    float rad_value;
    uint8_t index;
    
    rad_value = value / TWO_PI;
    index = (int)(rad_value / sin_table_entries);
    return pgm_read_float(&(sin_table[index]));
}

float cos(float value)
{
    float rad_value;
    uint8_t index;
    
    rad_value = value / TWO_PI;
    index = (int)(rad_value / sin_table_entries);
    return pgm_read_float(&(cos_table[index]));
}

void setup() 
{ 
    startup();
    
    Serial.begin(38400);
    Wire.begin();

    delay(5);
    sixDOF.init();
    delay(5);
}

void loop() 
{ 
    uint8_t i,red, blue; 
    float x, y, z;
    float angles[3]; // yaw pitch roll
    float theta, phi;

    sixDOF.getEuler(angles);
    
    theta = angles[2] / TWO_PI;
    phi = angles[1] / TWO_PI;
    
    x = sin(theta) * cos(phi);
    y = sin(theta) * sin(phi);
    z = cos(theta);
    
    red = int((z + 1) * 128)
    blue = 255 - int((z + 1) * 128)
    led_color(red, 0, blue);
    
    Serial.print(micros());
    Serial.print(","); 
    Serial.print(int(angles[0]));
    Serial.print(",");  
    Serial.print(int(angles[1]));
    Serial.print(",");
    Serial.println(int(angles[2]));    
}
