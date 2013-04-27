
#include <Stream.h>
#include <stdio.h>
#include "PumpCmdProcessor.h"

PumpControl pctrl = PumpControl();
PumpCmdProcessor cmdProc = PumpCmdProcessor(&pctrl);

int statusLed = 13;
int errorLed = 13;
int loopCtr = 0;

// Timeout handling
long oneSecondInterval = 1000;
long oneSecondCounter = 0;
int ledCounter = 0;

int counter = 0;

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
    
	pinMode(statusLed,OUTPUT);
}

void toggleLed()
{
  // blink
  if (ledCounter % 2) {
    digitalWrite(statusLed, HIGH);
  } else {
    digitalWrite(statusLed, LOW);
  }
  ledCounter++;
}  


// ------------------ M A I N ( ) --------------------------------------------

void loop()
{
    char buffer[128];

    cmdProc.Loop();

    pctrl.readSensors();

	if ( millis() - oneSecondCounter > oneSecondInterval) {
		oneSecondCounter = millis();
		// Things to do at a one-second interval. 
		toggleLed();
        pctrl.Loop();
	}

    delay(1);

    loopCtr++;

}



