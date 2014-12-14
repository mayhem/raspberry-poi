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

// Smoothing
#define NUM_READINGS 3
float readings[NUM_READINGS][3];
uint8_t reading_index = 0;
float total[3];

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
    
    for(i = 0; i < 5; i++)
    {
        led_color(128, 70, 0);
        delay(100);
        led_color(128, 0, 128);
        delay(100);
    }    
    led_color(0, 0, 0);    
}

float sin_lookup(uint16_t index)
{
    return pgm_read_float(&(sin_table[index]));
}

float cos_lookup(uint16_t index)
{
    return pgm_read_float(&(cos_table[index]));
}

void setup() 
{ 
    uint16_t i;
    
    Serial.begin(38400);
    Wire.begin();

    delay(5);
    sixDOF.init();
    delay(5);   
    
    startup();
    
    memset(readings, 0, sizeof(readings));
    memset(total, 0, sizeof(total));
}

void loop() 
{ 
    uint8_t i, j, red, blue; 
    float x, y, z;
    float angles[3]; // yaw pitch roll
    float st;

    for(j = 0; j < NUM_READINGS; j++)
    {
        // subtract the last reading:
        for(i = 0; i < 3; i++)
            total[i] -= readings[reading_index][i];
           
        sixDOF.getEuler(angles);    
        for(i = 0; i < 3; i++)
            readings[reading_index][i] = angles[i];
            
        for(i = 0; i < 3; i++)
            total[i] += readings[reading_index][i];    
    
        reading_index = (reading_index + 1) % NUM_READINGS;  
    }  
    
    for(i = 0; i < 3; i++)
        angles[i] = total[i] / NUM_READINGS; 
        
    st = sin_lookup((int)angles[2]);
    x = st * cos_lookup((int)angles[1]);
    y = st * sin_lookup((int)angles[1]);
    z = cos_lookup((int)angles[2]);
    
    //red = int((z + 1.0) * 128.0);
    //blue = 255 - int((z + 1.0) * 128.0);
    //led_color(red, 0, blue);
    
    Serial.print(micros());
    Serial.print(","); 
    Serial.print(int(angles[0]));
    Serial.print(",");  
    Serial.print(int(angles[1]));
    Serial.print(",");
    Serial.println(int(angles[2]));      
}
