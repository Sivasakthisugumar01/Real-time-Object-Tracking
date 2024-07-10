#include <Servo.h>

Servo panServo;
Servo tiltServo;

void setup() {
  Serial.begin(9600);
  panServo.attach(9);  // Attach the pan servo to pin 9
  tiltServo.attach(10);  // Attach the tilt servo to pin 10

  panServo.write(90);  // Initialize pan servo to center position
  tiltServo.write(90);  // Initialize tilt servo to center position
}

void loop() {
  if (Serial.available() > 0) {
    String input = Serial.readStringUntil('\n');
    int commaIndex = input.indexOf(',');
    if (commaIndex > 0) {
      int panAngle = input.substring(0, commaIndex).toInt();
      int tiltAngle = input.substring(commaIndex + 1).toInt();

      panServo.write(panAngle);
      tiltServo.write(tiltAngle);
    }
  }
}
