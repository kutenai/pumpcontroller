
#include <Stream.h>
#include <stdio.h>
#include "PumpCmdProcessor.h"

PumpControl pctrl = PumpControl();
PumpCmdProcessor cmdProc = PumpCmdProcessor(&pctrl);

int statusLed = 13;
int errorLed = 13;
int loopCtr = 0;

void flashLed(int pin, int times, int wait) {

  for (int i = 0; i < times; i++) {
    digitalWrite(pin, HIGH);
    delay(wait);
    digitalWrite(pin, LOW);

    if (i + 1 < times) {
      delay(wait);
    }
  }
}

// ------------------ S E T U P ----------------------------------------------

void setup() {
    Serial.begin(9600);

    //Serial.setTimeout(1000);
    cmdProc.setSerial(Serial);
}

// ------------------ M A I N ( ) --------------------------------------------

void loop()
{
    char buffer[128];

    cmdProc.Loop();

    pctrl.readSensors();

    if (loopCtr % 10 == 0) {
        pctrl.Loop();
    }

    delay(100);

    loopCtr++;

}



