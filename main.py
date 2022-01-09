import time
import board
import adafruit_dht
import requests
import datetime
from typing import List
import asyncio

loop = asyncio.get_event_loop()
dhtDevice = adafruit_dht.DHT22(board.D4, use_pulseio=False)

#URL = "http://localhost:3030"
URL = "http://192.168.0.100:8080"
hour_address = "{}/add_temp".format(URL)
last_address = "{}/add_last_temp".format(URL)

temps: List[float] = []

async def meassure():
    try:
        temperature_c = dhtDevice.temperature
        temps.append(float(temperature_c)) #type: ignore
    except RuntimeError as error:
        time.sleep(2)
        await meassure()
    except Exception as error:
        dhtDevice.exit()
        raise error

async def repeat_meassure():
    for _ in range(5):
        await meassure()
        time.sleep(2)

async def add_temp(address: str):
    await repeat_meassure()
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

async def wait_till_whole():
    date = datetime.datetime.now()
    #print("measured at {}".format(date.hour))
    await asyncio.sleep((59 - date.minute) * 60)

async def every_hour():
    while True:
        await add_temp(hour_address)
        await wait_till_whole()

async def every_minutes():
    while True:
        # little bit over 3 minutes
        await asyncio.sleep(270)
        await add_temp(last_address)

loop.create_task(every_hour())
loop.create_task(every_minutes())

loop.run_forever()
