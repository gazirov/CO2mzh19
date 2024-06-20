#!/usr/bin/python3
import serial, os, time, sys, datetime, csv
import paho.mqtt.client as mqtt  # Import the MQTT library

# MQTT Settings
MQTT_BROKER = "127.0.0.1"
MQTT_PORT = 1883
MQTT_TOPIC = "sensor/co2"

def on_connect(client, userdata, flags, rc):
    if rc == 0:
        print("Connected to MQTT Broker!")
    else:
        print("Failed to connect, return code %d", rc)

def mqtt_publish(client, topic, payload):
    result = client.publish(topic, payload)
    status = result[0]
    if status == 0:
       # print(f"Send `{payload}` to topic `{topic}`")
    else:
        print(f"Failed to send message to topic {topic}")

def logfilename():
    now = datetime.datetime.now()
    #return f'CO2LOG-{now.year:04d}-{now.month:02d}-{now.day:02d}-{now.hour:02d}ua789{now.minute:02d}ua789{now.second:02d}.csv'

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

client = mqtt.Client()
client.on_connect = on_connect
client.connect(MQTT_BROKER, MQTT_PORT)
client.loop_start()  # Start the loop in the background (non-blocking)

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
                        # Send data to MQTT
                        mqtt_payload = str(co2value)
                        mqtt_publish(client, MQTT_TOPIC, mqtt_payload)
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