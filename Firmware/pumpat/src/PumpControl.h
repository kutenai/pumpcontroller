#ifndef PUMPCTRL_H
#define PUMPCTRL_H

class PumpControl
{
public:

    static const int pumpPin = 2;
    // Need to swap these pins
    // The north and south are backwards
    static const int northPin = 3;
    static const int southPin = 4;

    // Analog inputs.
    static const int ditchPin = 2;
    static const int sumpPin = 5;

    // Set the pump call on when we want the pump to go..
    // we might turn it off if the levels are too low.
    bool pumpCall;

    // Set these to true when we want the valve on. The actual state of
    // the valve will be off unless the pump is on..
    bool northCall;
    bool southCall;

    int ditchCurr;
    long ditchSum;
    int ditchCount;

    int sumpCurr;
    long sumpSum;
    int sumpCount;

    // Trigger levels.. to turn off the pump if the levels are reached
    int sumpLowTrigger;
    bool enableSumpTrigger;


public:
    PumpControl();
    ~PumpControl();

    void Loop(); // Call periodically, about once a second

    bool isPumpOn();
    bool isNorthOn();
    bool isSouthOn();
    void setPump(bool bOn);
    void setNorthCall(bool bOn);
    void setNorthValve(bool bOn);
    void setSouthCall(bool bOn);
    void setSouthValve(bool bOn);
    void setSumpTrigger(int trig);
    void setSumpTriggerEnable(bool bOn);
    void levelChecks();
    void updateValves();
    void readSensors();

};

#endif
