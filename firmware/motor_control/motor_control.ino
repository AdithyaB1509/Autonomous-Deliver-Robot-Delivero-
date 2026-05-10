#include <ESP32Encoder.h>

// Cytron MD20A Pins
const int M1_PWM = 25;  const int M1_DIR = 26;
const int M2_PWM = 27;  const int M2_DIR = 14;

ESP32Encoder enc1;
ESP32Encoder enc2;
unsigned long last_time = 0;

// ✅ Add these two lines here (global scope, outside any function)
long prev1 = 0, prev2 = 0;

void setup() {
  Serial.begin(115200);
  
  pinMode(M1_PWM, OUTPUT); pinMode(M1_DIR, OUTPUT);
  pinMode(M2_PWM, OUTPUT); pinMode(M2_DIR, OUTPUT);

  ESP32Encoder::useInternalWeakPullResistors = puType::up;
  enc1.attachFullQuad(32, 33);
  enc2.attachFullQuad(34, 35);
}

void loop() {
  // Motor command reception (unchanged)
  if (Serial.available() > 0) {
    char startChar = Serial.read();
    if (startChar == 'v') {
      int speed1 = Serial.parseInt(); 
      int speed2 = Serial.parseInt();
      
      digitalWrite(M1_DIR, speed1 >= 0 ? HIGH : LOW);
      analogWrite(M1_PWM, abs(speed1));
      
      digitalWrite(M2_DIR, speed2 >= 0 ? HIGH : LOW);
      analogWrite(M2_PWM, abs(speed2));
    }
  }

  // ✅ Replace your old encoder block entirely with this
  if (millis() - last_time > 50) {
    long dt_ms = millis() - last_time;
    long curr1 = enc1.getCount();
    long curr2 = enc2.getCount();

    float vel1 = (curr1 - prev1) * (1000.0 / dt_ms); // ticks/sec
    float vel2 = (curr2 - prev2) * (1000.0 / dt_ms);

    prev1 = curr1;
    prev2 = curr2;
    last_time = millis();

    Serial.print("e ");
    Serial.print(vel1);
    Serial.print(" ");
    Serial.println(vel2);
  }
}