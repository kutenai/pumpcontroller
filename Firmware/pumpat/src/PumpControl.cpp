#include "Arduino.h"
#include "PumpControl.h"

PumpControl::PumpControl() {
    pumpCall = false;
    northCall = false;
    southCall = false;

    ditchCurr = 0;
    ditchSum = 0;
    ditchCount = 0;

    sumpCurr = 0;
    sumpSum = 0;
    sumpCount = 0;

    sumpLowTrigger = 0;
    enableSumpTrigger = false;
}

PumpControl::~PumpControl() {}

void PumpControl::setSumpTrigger(int lvl) {
    sumpLowTrigger = lvl;
}

void PumpControl::setSumpTriggerEnable(bool bOn) {
    enableSumpTrigger = bOn;
}

bool PumpControl::isPumpOn() {
  int pin = digitalRead(PumpControl::pumpPin);
  if (pin == LOW) {
    return true;
  }
  return false;
}

bool PumpControl::isNorthOn() {
  int pin = digitalRead(PumpControl::northPin);
  if (pin == LOW) {
    return true;
  }
  return false;
}

bool PumpControl::isSouthOn() {
  int pin = digitalRead(PumpControl::southPin);
  if (pin == LOW) {
    return true;
  }
  return false;
}

void PumpControl::setPump(bool bOn) {
  if (bOn) {
    pumpCall = true;
    digitalWrite(PumpControl::pumpPin,LOW);
  } else {
    pumpCall = false;
    digitalWrite(PumpControl::pumpPin,HIGH);
  }
}

void PumpControl::setNorthCall(bool bOn) {
  northCall = bOn;
}

void PumpControl::setNorthValve(bool bOn) {
  if (bOn) {
    digitalWrite(PumpControl::northPin,LOW);
  } else {
    digitalWrite(PumpControl::northPin,HIGH);
  }
}

void PumpControl::setSouthCall(bool bOn) {
  southCall = bOn;
}

void PumpControl::setSouthValve(bool bOn) {
  if (bOn) {
    digitalWrite(PumpControl::southPin,LOW);
  } else {
    digitalWrite(PumpControl::southPin,HIGH);
  }
}

void PumpControl::Loop() {
    levelChecks();
    updateValves();
}

void PumpControl::levelChecks() {
    if (enableSumpTrigger && sumpCurr < sumpLowTrigger) {
      setPump(false);
    } else {
      setPump(pumpCall);
    }
}

/*
  Called once a second.
  If the pump is off, then force both valves off.
*/
void PumpControl::updateValves() {
  if (isPumpOn() ) {
    setNorthValve(northCall);
    setSouthValve(southCall);
  } else {
    // Always turn valves off if the pump
    // is off.
    setNorthValve(false);
    setSouthValve(false);
  }
}

/*
  Called often.. reads sensors and applies hardware
  averaging.
*/
void PumpControl::readSensors() {
  int ditch = analogRead(PumpControl::ditchPin);
  int sump = analogRead(PumpControl::sumpPin);

  ditchSum += ditch;
  ditchCount++;
  if (ditchCount >= 1000) {
    double ditchD = ditchSum;
    ditchD /= (double)ditchCount;
    ditchCurr = (int)ditchD;
    ditchCount = 0;
    ditchSum = 0;
  }

  sumpSum += sump;
  sumpCount++;
  if (sumpCount >= 1000) {
    double sumpD = sumpSum;
    sumpD /= (double)sumpCount;
    sumpCurr = (int)sumpD;
    sumpCount = 0;
    sumpSum = 0;
  }
}

