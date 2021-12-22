import time
import board
import adafruit_dht
import requests
import datetime
from typing import List

dhtDevice = adafruit_dht.DHT22(board.D4, use_pulseio=False)

#URL = "http://localhost:3030"
URL = "http://192.168.0.110:8080"
address = "{}/add_temp".format(URL)

temps: List[float] = []

def meassure():
    temperature_c = dhtDevice.temperature
    temps.append(float(temperature_c)) #type: ignore

def repeat_meassure():
    for _ in range(5):
        meassure()
        time.sleep(2)

def add_temp():
    repeat_meassure()
    temp = sum(temps) / len(temps)
    date = datetime.datetime.now()
    data = {
        "y": date.year,
        "m": date.month,
        "d": date.day,
        "h": date.hour,
        "averageTemp": str(temp)
    }
    temps.clear()
    try:
        requests.post(address, json=data)
    except requests.ConnectionError as error:
        print(error)

while True:
    try:
        add_temp()

    except RuntimeError as error:
        time.sleep(2.0)
        continue
    except Exception as error:
        dhtDevice.exit()
        raise error

    time.sleep(60 * 60)
