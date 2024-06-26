#!/usr/bin/python3
#based on this project https://www.circuits.dk/testing-mh-z19-ndir-co2-sensor-module/

import serial, os, time, sys, datetime, csv

def logfilename():
    now = datetime.datetime.now()
    return f'CO2LOG-{now.year:04d}-{now.month:02d}-{now.day:02d}-{now.hour:02d}ua789{now.minute:02d}ua789{now.second:02d}.csv'

def crc8(a):
    crc = 0x00
    count = 1
    b = bytearray(a)
    while count < 8:
        crc += b[count]
        count += 1
    crc %= 256
    crc = ~crc & 0xFF
    crc += 1
    return crc
#it is necessary to specify the port on your device where the sensor is connected.it is necessary to specify the port on your device where the sensor is connected.
#for example on raspberry PI port='/dev/serial0'
port = '/dev/ttyS0'

sys.stderr.write(f'Trying port {port}\n')

try:
    with serial.Serial(port, 9600, timeout=2.0) as ser:
        result = ser.write(b'\xFF\x01\x86\x00\x00\x00\x00\x00\x79')
        time.sleep(0.1)
        data = ser.read(9)
        crc = crc8(data)
        if crc != data[8]:
            sys.stderr.write(f'CRC error calculated {crc} bytes= {data}\n')
        else:
            sys.stderr.write(f'Logging data on {port} to {logfilename()}\n')
    
        outfname = logfilename()
        with open(outfname, 'a') as f:
            while True:
                result = ser.write(b'\xFF\x01\x86\x00\x00\x00\x00\x00\x79')
                time.sleep(0.1)
                data = ser.read(9)
                crc = crc8(data)
                if crc != data[8]:
                    sys.stderr.write(f'CRC error calculated {crc} bytes= {data}\n')
                else:       
                    if data[0] == 0xFF and data[1] == 0x86:
                        co2value = data[2] * 256 + data[3]
                        print(f"co2= {co2value}")
                        now = time.ctime()
                        parsed = time.strptime(now)
                        lgtime = time.strftime("%Y %m %d %H:%M:%S")
                        row = [lgtime, co2value]
                        w = csv.writer(f)
                        w.writerow(row)
                        t = datetime.datetime.now()
                        sleeptime = 60 - t.second
                        time.sleep(sleeptime)
except Exception as e:
    sys.stderr.write(f'Error reading serial port {type(e).__name__}: {e}\n')
except KeyboardInterrupt:
    sys.stderr.write(f'\nCtrl+C pressed, exiting log of {port} to {outfname}\n')
finally:
    f.close()
    ser.close()