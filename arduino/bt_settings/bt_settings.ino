void setup() 
{ 
    Serial.begin(38400);
    pinMode(9, OUTPUT);
    digitalWrite(9, HIGH);
    
    delay(1000);
    Serial.print("$$$");
    delay(1000);
        
    Serial.println("SN,Poi_Two");
    delay(1000);
    
    Serial.println("SP,0000");
    delay(1000);
    
    // Low latency, fast reconnect
    //Serial.println("SQ,144");
    
    // Low latency
    //Serial.println("SQ,16");
    
    // no special options
    Serial.println("SQ,0");
    delay(1000);
    
    Serial.println("R,1");
    delay(500);
    digitalWrite(9, LOW);
}

void loop() 
{ 
}
