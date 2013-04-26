#include <CmdMessenger.h>
#include <stdio.h>


//#include <Streaming.h>

// Mustnt conflict / collide with our message payload data. Fine if we use base64 library ^^ above
char field_separator = ',';
char command_separator = ';';

int pumpPin = 2;
// Need to swap these pins
// The north and south are backwards
int northPin = 3;
int southPin = 4;

// Analog inputs.
int ditchPin = 2;
int sumpPin = 5;

// Set the pump call on when we want the pump to go..
// we might turn it off if the levels are too low.
bool pumpCall = false;

// Set these to true when we want the valve on. The actual state of
// the valve will be off unless the pump is on.. 
bool northCall = false;
bool southCall = false;

int ditchCurr = 0;
long ditchSum = 0;
int ditchCount = 0;

int sumpCurr = 0;
long sumpSum = 0;
int sumpCount = 0;

// Trigger levels.. to turn off the pump if the levels are reached
int sumpLowTrigger = 0;
bool enableSumpTrigger = false;

// Attach a new CmdMessenger object to the default Serial port
CmdMessenger cmdMessenger = CmdMessenger(Serial, field_separator, command_separator);

#include "PumpController.h"

void enablepump_msg();
void north_msg();
void south_msg();
void status_msg();
void sumptrigger_msg();
void sumptrigger_en_msg();
void setAnalogPins_msg();

// Commands we send from the PC and want to recieve on the Arduino.
// We must define a callback function in our Arduino program for each entry in the list below vv.
// They start at the address kSEND_CMDS_END defined ^^ above as 004
messengerCallbackFunction messengerCallbacks[] =
{
  enablepump_msg,            // 004 in this example
  north_msg,
  south_msg,
  status_msg,
  sumptrigger_msg,
  sumptrigger_en_msg,
  setAnalogPins_msg,
  NULL
};

bool isPumpOn() {
  int pin = digitalRead(pumpPin);
  if (pin == LOW) {
    return true;
  }
  return false;
}
bool isNorthOn() {
  int pin = digitalRead(northPin);
  if (pin == LOW) {
    return true;
  }
  return false;
}
bool isSouthOn() {
  int pin = digitalRead(southPin);
  if (pin == LOW) {
    return true;
  }
  return false;
}

void setPump(bool bOn) {
  if (bOn) {
    digitalWrite(pumpPin,LOW);
  } else {
    digitalWrite(pumpPin,HIGH);
  }
}

void setNorthCall(bool bOn) {
  northCall = bOn;
}

void setNorthValve(bool bOn) {
  if (bOn) {
    digitalWrite(northPin,LOW);
  } else {
    digitalWrite(northPin,HIGH);
  }
}

void setSouthCall(bool bOn) {
  southCall = bOn;
}

void setSouthValve(bool bOn) {
  if (bOn) {
    digitalWrite(southPin,LOW);
  } else {
    digitalWrite(southPin,HIGH);
  }
}

// ------------------ C A L L B A C K  M E T H O D S -------------------------

void enablepump_msg()
{
  // Message data is any ASCII bytes (0-255 value). But can't contain the field
  // separator, command separator chars you decide (eg ',' and ';')
  //cmdMessenger.sendCmd(kACK,"enable pump recieved");
  //setFlash(6);

  while ( cmdMessenger.available() )
  {
    char buf[350] = { '\0' };
    cmdMessenger.copyString(buf, 350);
    if(buf[0]) {
      if (strcmp(buf,"on") == 0) {
        cmdMessenger.sendCmd(kACK, "Ok:PumpOn");
        pumpCall = true;
      } else if (strcmp(buf,"off") == 0) {
        cmdMessenger.sendCmd(kACK, "Ok:PumpOff");
        pumpCall = false;
      } else {
        char msg[30];
        sprintf(msg,"Fail:invalid command:%s",buf);
        cmdMessenger.sendCmd(kERR, msg);
      }
    }
  }
}

void north_msg() {
  // Message data is any ASCII bytes (0-255 value). But can't contain the field
  // separator, command separator chars you decide (eg ',' and ';')
  //setFlash(5);
  cmdMessenger.sendCmd(kACK,"north valve msg received");
  while ( cmdMessenger.available() )
  {
    char buf[350] = { '\0' };
    cmdMessenger.copyString(buf, 350);
    if(buf[0]) {
      //cmdMessenger.sendCmd(kACK, buf);
      if (strcmp(buf,"on") == 0) {
        setNorthCall(true);
        cmdMessenger.sendCmd(kACK,"Ok");
      } else {
        setNorthCall(false);
        cmdMessenger.sendCmd(kACK,"Ok");
      }
    }
  }
}

void south_msg() {
  // Message data is any ASCII bytes (0-255 value). But can't contain the field
  // separator, command separator chars you decide (eg ',' and ';')
  //setFlash(4);
  cmdMessenger.sendCmd(kACK,"south valve msg received");
  while ( cmdMessenger.available() ) {
    char buf[350] = { '\0' };
    cmdMessenger.copyString(buf, 350);
    if(buf[0]) {
      cmdMessenger.sendCmd(kACK, buf);
      if (strcmp(buf,"on") == 0) {
        setSouthCall(true);
      } else {
        setSouthCall(false);
      }
    }
  }
}

void status_msg() {
  char buf[350] = { '\0' };
  
  // Read sensors.
  sprintf(buf,"Ok:Ditch:%d Sump:%d PC:%d P:%d NC:%d N:%d SC:%d S:%d ST:%d STen:%d",
    ditchCurr,
    sumpCurr,
    pumpCall,
    isPumpOn(),
    northCall, isNorthOn(),
    southCall, isSouthOn(),
    sumpLowTrigger,
    enableSumpTrigger
    );
  cmdMessenger.sendCmd(kACK,buf);

  //setFlash(3);
}

void sumptrigger_msg() {
  while ( cmdMessenger.available() )
  {
    char buf[350] = { '\0' };
    cmdMessenger.copyString(buf, 350);
    if(buf[0]) {
      int triggerLevel = atoi(buf);

      if (triggerLevel == 0 || triggerLevel > 1023) {
        // Probably a bad value
        char msg[30];
        sprintf(msg,"Fail:bad trigger level(%s), enter a number between 1 and 1023",buf);
        cmdMessenger.sendCmd(kERR, msg);
      } else {
        sumpLowTrigger = triggerLevel;
        char msg[30];
        sprintf(msg,"Ok:sump trigger to set %d",sumpLowTrigger);
        cmdMessenger.sendCmd(kACK, msg);
      }
    }
  }
}

void sumptrigger_en_msg() {
  while ( cmdMessenger.available() )
  {
    char buf[350] = { '\0' };
    cmdMessenger.copyString(buf, 350);
    if(buf[0]) {
      if (strcmp(buf,"en") == 0) {
        enableSumpTrigger = true;
        cmdMessenger.sendCmd(kACK, "Ok:Sump Trigger Enabled.");
      } else if (strcmp(buf,"disable") == 0)  {
        enableSumpTrigger = false;
        cmdMessenger.sendCmd(kACK, "Ok:Sump Trigger Disabled.");
      } else {
        char msg[30];
        sprintf(msg,"Fail:invalid command:%s use one of en,disable",buf);
        cmdMessenger.sendCmd(kERR, msg);
      }
    }
  }
}

// Pass 2 values, pin for ditch, and pin for sump.
// The defaults are 2 and 5.. but you can swap these to
// 5 and 2.. 
void setAnalogPins_msg() {
  if ( cmdMessenger.available() )
  {
    // First is the ditch number..
    char buf[350] = { '\0' };
    cmdMessenger.copyString(buf, 350);
    if(buf[0]) {
      int pinNum = atoi(buf);

      if (pinNum == 2 || pinNum == 5) {
        if (pinNum == 2) {
          ditchPin = 2;
          sumpPin = 5;
        } else {
          ditchPin = 5;
          sumpPin = 2;
        }
        char msg[30];
        sprintf(msg,"Ok:ditchPin:%d sumpPin:%d",ditchPin,sumpPin);
        cmdMessenger.sendCmd(kERR, msg);
      } else {
        char msg[30];
        sprintf(msg,"Fail:please specify the ditch pin as 2 or 5");
        cmdMessenger.sendCmd(kERR, msg);
      }
    }
    while (cmdMessenger.available()) ;
  }
}

void levelChecks() {
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
void updateValves() {
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
void readSensors() {
  int ditch = analogRead(ditchPin);
  int sump = analogRead(sumpPin);
  
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

void arduino_ready()
{
  // In response to ping. We just send a throw-away Acknowledgement to say "im alive"
  cmdMessenger.sendCmd(kACK,"Arduino ready");
}

void unknownCmd()
{
  // Default response for unknown commands and corrupt messages
  cmdMessenger.sendCmd(kERR,"Unknown command");
}

// ------------------ S E T U P ----------------------------------------------

void setup() {
  // Listen on serial connection for messages from the pc
  // Serial.begin(57600);  // Arduino Duemilanove, FTDI Serial
  Serial.begin(9600); // Arduino Uno, Mega, with AT8u2 USB

  cmdMessenger.discard_LF_CR(); // Useful if your terminal appends CR/LF, and you wish to remove them
  cmdMessenger.print_LF_CR();   // Make output more readable whilst debugging in Arduino Serial Monitor
  
  // Attach default / generic callback methods
  cmdMessenger.attach(kARDUINO_READY, arduino_ready);
  cmdMessenger.attach(unknownCmd);

  // Attach my application's user-defined callback methods
  attach_callbacks(messengerCallbacks);

  arduino_ready();

  // blink
  pinMode(13, OUTPUT);
  
  // Pump and Valve controls
  // High is off, low is on.
  digitalWrite(2,HIGH);
  pinMode(2,OUTPUT);
  digitalWrite(3,HIGH);
  pinMode(3,OUTPUT);
  digitalWrite(4,HIGH);
  pinMode(4,OUTPUT);
}

// ------------------ M A I N ( ) --------------------------------------------

// Timeout handling
long oneSecondInterval = 1000;
long oneSecondCounter = 0;

int counter = 0;

void timeout()
{
  // blink
  if (counter % 2) {
    digitalWrite(13, HIGH);
  } else {
    digitalWrite(13, LOW);
  }
  counter++;
}  

void loop() 
{
  // Process incoming serial data, if any
  cmdMessenger.feedinSerialData();

  // Things to do all the time.
  readSensors();

  if ( millis() - oneSecondCounter > oneSecondInterval) {
    oneSecondCounter = millis();
    // Things to do at a one-second interval. 
    timeout();
    levelChecks();
    updateValves();
  }

}



