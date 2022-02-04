import time
import board
import adafruit_dht
import requests
import datetime
from typing import List

dhtDevice = adafruit_dht.DHT22(board.D4, use_pulseio=False)

#URL = "http://localhost:3030"
URL = "http://192.168.0.100:8080"
hour_address = "{}/add_temp".format(URL)
last_address = "{}/add_last_temp".format(URL)

temps: List[float] = []

def meassure():
    try:
        temperature_c = dhtDevice.temperature
        temps.append(float(temperature_c)) #type: ignore
    except RuntimeError as error:
        time.sleep(2)
        meassure()
    except Exception as error:
        dhtDevice.exit()
        raise error

def repeat_meassure():
    for _ in range(5):
        meassure()
        time.sleep(2)

def add_temp(address: str):
    repeat_meassure()
    temp = sum(temps) / len(temps)
    date = datetime.datetime.now()
    data = {
        "y": date.year,
        "m": date.month,
        "d": date.day,
        "h": date.hour,
        "averageTemp": str(round(temp, 2))
    }
    temps.clear()
    try:
        requests.post(address, json=data)
    except requests.ConnectionError as error:
        print(error)

def wait_till_whole():
    date = datetime.datetime.now()
    #print("measured at {}".format(date.hour))
    time.sleep((59 - date.minute) * 60)

add_temp(last_address)
time.sleep(60)

while True:
    date = datetime.datetime.now()
    if date.minute == 0:
        add_temp(hour_address)
    elif date.minute % 4.0 == 0.0:
        add_temp(last_address)
    time.sleep(50)
