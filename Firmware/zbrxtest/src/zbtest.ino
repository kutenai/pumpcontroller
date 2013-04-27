
#define SERIES_2
#include <XBee.h>

XBee xbee = XBee();
XBeeAddress64 addr64 = XBeeAddress64(0x0013a200, 0x409e0e94);

uint8_t payload[] = { 0,1 };

// SH + SL Address of receiving XBee
ZBTxRequest zbTx = ZBTxRequest(addr64, payload, sizeof(payload));
ZBTxStatusResponse txStatus = ZBTxStatusResponse();

int statusLed = 13;
int errorLed = 13;

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
    xbee.setSerial(Serial);
}

// ------------------ M A I N ( ) --------------------------------------------

void loop()
{
  // Process incoming serial data, if any

    payload[0]++;
    payload[1]--;
    xbee.send(zbTx);

    if (xbee.readPacket(500)) {
        // got a response!

        // should be a znet tx status
        if (xbee.getResponse().getApiId() == ZB_TX_STATUS_RESPONSE) {
          xbee.getResponse().getZBTxStatusResponse(txStatus);

          // get the delivery status, the fifth byte
          if (txStatus.getDeliveryStatus() == SUCCESS) {
            // success.  time to celebrate
            flashLed(statusLed, 5, 100);
          } else {
            // the remote XBee did not receive our packet. is it powered on?
            flashLed(errorLed, 3, 500);
          }
        }
      } else if (xbee.getResponse().isError()) {
        //nss.print("Error reading packet.  Error code: ");
        //nss.println(xbee.getResponse().getErrorCode());
      } else {
        // local XBee did not provide a timely TX Status Response -- should not happen
        flashLed(errorLed, 2, 100);
      }
    delay(1000);
}



