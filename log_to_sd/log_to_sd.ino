     
#include <Adafruit_GPS.h>
#include <SPI.h>
#include <SD.h>

// what's the name of the hardware serial port?
#define GPSSerial Serial1

// Connect to the GPS on the hardware port
Adafruit_GPS GPS(&GPSSerial);
     
// Set GPSECHO to 'false' to turn off echoing the GPS data to the Serial console
// Set to 'true' if you want to debug and listen to the raw GPS sentences
#define GPSECHO false

uint32_t timer = millis();
const int chipSelect = 4;

String linesToFile[12];
uint8_t counter = 0;

void setup() {
  pinMode(8, OUTPUT);
  pinMode(13, OUTPUT);

  Serial.begin(115200);
  while (!Serial);  // uncomment to have the sketch wait until Serial is ready


  // 9600 NMEA is the default baud rate for Adafruit MTK GPS's- some use 4800
  GPS.begin(9600);
  // uncomment this line to turn on RMC (recommended minimum) and GGA (fix data) including altitude
  GPS.sendCommand(PMTK_SET_NMEA_OUTPUT_RMCGGA);
  // uncomment this line to turn on only the "minimum recommended" data
  //GPS.sendCommand(PMTK_SET_NMEA_OUTPUT_RMCONLY);
  // For parsing data, we don't suggest using anything but either RMC only or RMC+GGA since
  // the parser doesn't care about other sentences at this time
  // Set the update rate
  GPS.sendCommand(PMTK_SET_NMEA_UPDATE_200_MILLIHERTZ);

  Serial.print("Initializing SD card...");

  // see if the card is present and can be initialized:
  if (!SD.begin(chipSelect)) {
    Serial.println("Card failed, or not present");
    // don't do anything more:
    return;
  }
  Serial.println("card initialized.");

  delay(1000);
  
  // Ask for firmware version
  GPSSerial.println(PMTK_Q_RELEASE);
}

void loop() {
  
  // read data from the GPS in the 'main loop'
  char c = GPS.read();
  // if you want to debug, this is a good time to do it!
//  if (GPSECHO)
//    if (c) Serial.print(c);
  // if a sentence is received, we can check the checksum, parse it...
  if (GPS.newNMEAreceived()) {
    // a tricky thing here is if we print the NMEA sentence, or data
    // we end up not listening and catching other sentences!
    // so be very wary if using OUTPUT_ALLDATA and trytng to print out data
//    Serial.println(GPS.lastNMEA()); // this also sets the newNMEAreceived() flag to false
    if (!GPS.parse(GPS.lastNMEA())) // this also sets the newNMEAreceived() flag to false
      return; // we can fail to parse a sentence in which case we should just wait for another
  }
  // if millis() or timer wraps around, we'll just reset it
  if (timer > millis()) timer = millis();
     
  if (millis() - timer > 5000) {
    timer = millis(); // reset the timer


    if (GPS.fix) {
      digitalWrite(13, HIGH);
      // initialize with 20 on some yk2 shit
      linesToFile[counter] = "20";
      linesToFile[counter] += String(GPS.year, DEC);
      linesToFile[counter] += "-";
      linesToFile[counter] += String(GPS.month, DEC);
      linesToFile[counter] += "-";
      linesToFile[counter] += String(GPS.day, DEC);
      linesToFile[counter] += "T";
      linesToFile[counter] += String(GPS.hour, DEC);
      linesToFile[counter] += ":";
      linesToFile[counter] += String(GPS.minute, DEC);
      linesToFile[counter] += ":";
      linesToFile[counter] += String(GPS.seconds, DEC);
      linesToFile[counter] += ".";
      linesToFile[counter] += String(GPS.milliseconds, DEC);
      linesToFile[counter] += ",";
      linesToFile[counter] += String(GPS.latitudeDegrees, 8);
      linesToFile[counter] += ",";
      linesToFile[counter] += String(GPS.longitudeDegrees, 8);
      linesToFile[counter] += ",";
      linesToFile[counter] += String(GPS.speed);
      linesToFile[counter] += ",";
      linesToFile[counter] += String(GPS.angle);
      linesToFile[counter] += ",";
      linesToFile[counter] += String(GPS.satellites);

      if(counter == 11) {
        digitalWrite(8, HIGH);
        File dataFile = SD.open("gps.csv", FILE_WRITE);

        if (dataFile) {
          for(uint8_t i=0; i < 12; i++) {
            dataFile.println(linesToFile[i]);
            Serial.println(linesToFile[i]);
          }
          dataFile.close();
        }
        // if the file isn't open, pop up an error:
        else {
          Serial.println("error opening datalog.txt");
        }
        digitalWrite(8, LOW);
        counter = 0;

      } else {
        counter++;
      }

      delay(100);
      digitalWrite(13, LOW);

    } else {
      Serial.println("No Fix");
    }
  }
}
