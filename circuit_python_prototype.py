
# this file needs to be renamed, e.g., code.py before sending to circuit board
# this prototype worked okay, but there are some issues that need to be worked out including increasing the battery life and increasing
# the significant figures retrieved from the GPS

import time
import board
import busio
import digitalio
import storage

import adafruit_gps
import adafruit_sdcard


led = digitalio.DigitalInOut(board.D13)
led.direction = digitalio.Direction.OUTPUT

RX = board.RX
TX = board.TX

LOG_FILE = '/sd/gps.csv'

LOG_MODE = 'ab'

LOG_PERIOD = 5.0

SD_CS_PIN = board.SD_CS  # CS for SD card (SD_CS is for Feather Adalogger)

spi = busio.SPI(board.SCK, MOSI=board.MOSI, MISO=board.MISO)
sd_cs = digitalio.DigitalInOut(SD_CS_PIN)
sdcard = adafruit_sdcard.SDCard(spi, sd_cs)
vfs = storage.VfsFat(sdcard)
storage.mount(vfs, '/sd')

uart = busio.UART(TX, RX, baudrate=9600, timeout=5000)

# Create a GPS module instance.
gps = adafruit_gps.GPS(uart)

# Turn on the basic GGA and RMC info (what you typically want)
gps.send_command('PMTK314,0,1,0,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0')
# Turn on just minimum info (RMC only, location):
#gps.send_command('PMTK314,0,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0')
# Turn off everything:
#gps.send_command('PMTK314,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0')
# Tuen on everything (not all of it is parsed!)
#gps.send_command('PMTK314,1,1,1,1,1,1,0,0,0,0,0,0,0,0,0,0,0,0,0')

# Set update rate to once a second (1hz) which is what you typically want.
gps.send_command('PMTK220,2000')
# Or decrease to once every two seconds by doubling the millisecond value.
# Be sure to also increase your UART timeout above!
#gps.send_command('PMTK220,2000')
# You can also speed up the rate, but don't go too fast or else you can lose
# data during parsing.  This would be twice a second (2hz, 500ms delay):
#gps.send_command('PMTK220,500')

with open(LOG_FILE, LOG_MODE) as outfile:

    outfile.write('timestamp,latitude,longitude,fix_quality,num_satellites,altitude,speed,track_angle,horizontal_dilution,height_geoid\n')
    outfile.flush()

    # Main loop runs forever printing the location, etc. every second.
    time_of_last_save = None

    while True:
        # Make sure to call gps.update() every loop iteration and at least twice
        # as fast as data comes from the GPS unit (usually every second).
        # This returns a bool that's true if it parsed new data (you can ignore it
        # though if you don't care and instead look at the has_fix property).
        gps.update()

        current = time.monotonic()
        if time_of_last_save is None or current - time_of_last_save >= LOG_PERIOD:
            last_print = current
            if not gps.has_fix:
                # Try again if we don't have a fix yet.
                print('Waiting for fix...')
                continue
            
            if gps.timestamp_utc.tm_mon == 0 or gps.timestamp_utc.tm_mday == 0 or gps.timestamp_utc.tm_year == 0:
                continue

            out = []
            out.append(
                '{}/{}/{} {:02}:{:02}:{:02}'.format(
                    gps.timestamp_utc.tm_mon,
                    gps.timestamp_utc.tm_mday,
                    gps.timestamp_utc.tm_year,
                    gps.timestamp_utc.tm_hour,
                    gps.timestamp_utc.tm_min, 
                    gps.timestamp_utc.tm_sec
                )
            )

            out.append('{0}'.format(gps.latitude))
            out.append('{0}'.format(gps.longitude))
            out.append('{0}'.format(gps.fix_quality))
            out.append('{0}'.format(gps.satellites))
            out.append('{0}'.format(gps.altitude_m))
            out.append('{0}'.format(gps.speed_knots))
            out.append('{0}'.format(gps.track_angle_deg))
            out.append('{0}'.format(gps.horizontal_dilution))
            out.append('{0}'.format(gps.height_geoid))

            
            try:
                outfile.write('{0}\n'.format(','.join(out)))
                outfile.flush()
            except Exception:
                print('{0}\n'.format(','.join(out)))
                continue
            else:
                print('written to csv: {0}'.format(','.join(out)))

            time_of_last_save = time.monotonic()

