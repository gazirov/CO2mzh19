project for connecting CO2 sensor mzh19 to orangePI or similar boards via COM port

The project https://www.circuits.dk/testing-mh-z19-ndir-co2-sensor-module/ was taken as a basis, the script of which was brought to working form 

---


there are 3 scripts in the set 

**mhz19.py** 
working script from the first example outputs data to console and also writes to CSV file.

**mzh19MQ.py**
script transfers sensor data to the MQ bus, for example, for data collection by a smart home 

**mhz19MQ_CSV.py**
transfers sensor data both to the MQ bus and to a CSV file


---

In all scripts it is necessary to specify the name of the port to which the sensor is connected.

```pyton
port = '/dev/ttyS0'
```

