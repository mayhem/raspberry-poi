void setup() 
{ 
    Serial.begin(38400);
}

void loop() 
{ 
    uint8_t ch;
    
    if (Serial.available() > 0) 
    {
        ch = Serial.read();
        Serial.write(ch);
    }
}
