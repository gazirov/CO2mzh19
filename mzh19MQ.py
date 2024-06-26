#!/usr/bin/python3
import serial, os, time, sys, datetime
import paho.mqtt.client as mqtt  # Import the MQTT library

# MQTT Settings
MQTT_BROKER = "192.168.88.3"
MQTT_PORT = 44444
MQTT_TOPIC = "sensor/co2"

def on_connect(client, userdata, flags, rc):
    if rc == 0:
        print("Connected to MQTT Broker!")
    else:
        print("Failed to connect, return code %d", rc)

def mqtt_publish(client, topic, payload, retain=False):
    result = client.publish(topic, payload, retain=retain)
    status = result[0]
    if status == 0:
       print(f"Send `{payload}` to topic `{topic}` with retain={retain}")
    else:
        print(f"Failed to send message to topic {topic}")

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
            sys.stderr.write(f'CRC error {crc} vs {data[8]}\n')
        else:
            while True:
                result = ser.write(b'\xFF\x01\x86\x00\x00\x00\x00\x00\x79')
                time.sleep(0.1)
                data = ser.read(9)
                crc = crc8(data)
                if crc != data[8]:
                    sys.stderr.write(f'CRC error {crc} vs {data[8]}\n')
                else:       
                    co2value = data[2] * 256 + data[3]
                    #print(f"co2= {co2value}")
                    mqtt_payload = str(co2value)
                    mqtt_publish(client, MQTT_TOPIC, mqtt_payload, True)
                    t = datetime.datetime.now()
                    sleeptime = 60 - t.second
                    time.sleep(sleeptime)
except Exception as e:
    sys.stderr.write(f'Error reading serial port {type(e).__name__}: {e}\n')
finally:
    ser.close()
