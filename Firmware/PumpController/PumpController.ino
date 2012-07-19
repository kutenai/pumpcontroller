#include <CmdMessenger.h>
#include <stdio.h>

#include <Streaming.h>

// Mustnt conflict / collide with our message payload data. Fine if we use base64 library ^^ above
char field_separator = ',';
char command_separator = ';';

int sensor1Curr = 0;
long sensor1Sum = 0;
int sensor1Count = 0;

int sensor2Curr = 0;
long sensor2Sum = 0;
int sensor2Count = 0;

// Attach a new CmdMessenger object to the default Serial port
CmdMessenger cmdMessenger = CmdMessenger(Serial, field_separator, command_separator);

// ------------------ C M D  L I S T I N G ( T X / R X ) ---------------------

// We can define up to a default of 50 cmds total, including both directions (send + recieve)
// and including also the first 4 default command codes for the generic error handling.
// If you run out of message slots, then just increase the value of MAXCALLBACKS in CmdMessenger.h

// Commands we send from the Arduino to be received on the PC
enum
{
  kCOMM_ERROR    = 000, // Lets Arduino report serial port comm error back to the PC (only works for some comm errors)
  kACK           = 001, // Arduino acknowledges cmd was received
  kARDUINO_READY = 002, // After opening the comm port, send this cmd 02 from PC to check arduino is ready
  kERR           = 003, // Arduino reports badly formatted cmd, or cmd not recognised

  // Now we can define many more 'send' commands, coming from the arduino -> the PC, eg
  // kICE_CREAM_READY,
  // kICE_CREAM_PRICE,
  // For the above commands, we just call cmdMessenger.sendCmd() anywhere we want in our Arduino program.

  kSEND_CMDS_END, // Mustnt delete this line
};

// Commands we send from the PC and want to recieve on the Arduino.
// We must define a callback function in our Arduino program for each entry in the list below vv.
// They start at the address kSEND_CMDS_END defined ^^ above as 004
messengerCallbackFunction messengerCallbacks[] = 
{
  enablepump_msg,            // 004 in this example
  valve1_msg,
  valve2_msg,
  sensordata_msg,  
  NULL
};

void setPump(bool bOn) {
  if (bOn) {
    digitalWrite(2,LOW);
  } else {
    digitalWrite(2,HIGH);
  }
}

void setNorthValve(bool bOn) {
  if (bOn) {
    digitalWrite(3,LOW);
  } else {
    digitalWrite(3,HIGH);
  }
}

void setSouthValve(bool bOn) {
  if (bOn) {
    digitalWrite(4,LOW);
  } else {
    digitalWrite(4,HIGH);
  }
}

// ------------------ C A L L B A C K  M E T H O D S -------------------------

void enablepump_msg()
{
  // Message data is any ASCII bytes (0-255 value). But can't contain the field
  // separator, command separator chars you decide (eg ',' and ';')
  cmdMessenger.sendCmd(kACK,"enable pump recieved");
  setFlash(6);

  while ( cmdMessenger.available() )
  {
    char buf[350] = { '\0' };
    cmdMessenger.copyString(buf, 350);
    if(buf[0]) {
      cmdMessenger.sendCmd(kACK, buf);
      if (strcmp(buf,"on") == 0) {
        cmdMessenger.sendCmd(kACK, "PumpOn");
        setPump(true);
      } else {
        cmdMessenger.sendCmd(kACK, "PumpOff");
        setPump(false);
      }
    }
  }
}

void valve1_msg() {
  // Message data is any ASCII bytes (0-255 value). But can't contain the field
  // separator, command separator chars you decide (eg ',' and ';')
  setFlash(5);
  cmdMessenger.sendCmd(kACK,"valve1 msg received");
  while ( cmdMessenger.available() )
  {
    char buf[350] = { '\0' };
    cmdMessenger.copyString(buf, 350);
    if(buf[0]) {
      cmdMessenger.sendCmd(kACK, buf);
      if (strcmp(buf,"on") == 0) {
        setNorthValve(true);
      } else {
        setNorthValve(false);
      }
    }
  }
}

void valve2_msg() {
  // Message data is any ASCII bytes (0-255 value). But can't contain the field
  // separator, command separator chars you decide (eg ',' and ';')
  setFlash(4);
  cmdMessenger.sendCmd(kACK,"valve2 msg received");
  while ( cmdMessenger.available() )
  {
    char buf[350] = { '\0' };
    cmdMessenger.copyString(buf, 350);
    if(buf[0]) {
      cmdMessenger.sendCmd(kACK, buf);
      if (strcmp(buf,"on") == 0) {
        setSouthValve(true);
      } else {
        setSouthValve(false);
      }
    }
  }
}

void sensordata_msg() {
  char buf[350] = { '\0' };
  
  // Read sensors.
  sprintf(buf,"%d,%d",sensor1Curr,sensor2Curr);
  cmdMessenger.sendCmd(kACK,buf);

  setFlash(3);
}

/*
  Called periodically..
*/
void readSensors() {
  int sensor1 = analogRead(2);
  int sensor2 = analogRead(5);
  
  sensor1Sum += sensor1;
  sensor1Count++;
  if (sensor1Count > 100) {
    double sensor1D = sensor1Sum;
    sensor1D /= sensor1Count;
    sensor1Curr = (int)sensor1D;
    sensor1Count = 0;
    sensor1Sum = 0;
  }

  sensor2Sum += sensor2;
  sensor2Count++;
  if (sensor1Count > 100) {
    double sensor2D = sensor2Sum;
    sensor2D /= sensor2Count;
    sensor2Curr = (int)sensor2D;
    sensor2Count = 0;
    sensor2Sum = 0;
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

void attach_callbacks(messengerCallbackFunction* callbacks)
{
  int i = 0;
  int offset = kSEND_CMDS_END;
  while(callbacks[i])
  {
    cmdMessenger.attach(offset+i, callbacks[i]);
    i++;
  }
}


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
long timeoutInterval = 2000; // 2 seconds
long previousMillis = 0;
int counter = 0;
int flashCount = 0;
long flashInterval = 200;
long previousFlashMillis = 0;

void timeout()
{
  // blink
  if (counter % 2) {
    digitalWrite(13, HIGH);
  } else {
    digitalWrite(13, LOW);
  }
  counter ++;
}  

void setFlash(int n) {
  counter = 0;
  digitalWrite(13, LOW);
  previousFlashMillis = millis();
  flashCount = n;
}

void loop() 
{
  // Process incoming serial data, if any
  cmdMessenger.feedinSerialData();

  if (flashCount) {
    previousMillis = millis();
    // handle timeout function, if any
    if (  millis() - previousFlashMillis > flashInterval )
    {
      timeout();
      previousFlashMillis = millis();
      if (counter % 2 == 1) {
        flashCount--;
      }
    }
  } else {
    
    // handle timeout function, if any
    if (  millis() - previousMillis > timeoutInterval )
    {
      timeout();
      previousMillis = millis();
    }
  }

  // Loop.
}



