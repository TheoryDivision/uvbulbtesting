#!/bin/python3

import board
import busio
import adafruit_ads1x15.ads1015 as ADS
from adafruit_ads1x15.analog_in import AnalogIn
import csv
import datetime
import time

i2c = busio.I2C(board.SCL, board.SDA)
ads = ADS.ADS1015(i2c)
chan = AnalogIn(ads, ADS.P0)
ads.gain = 2/3

with open('uvbulbdata.csv', 'a') as file:
    writer = csv.writer(file)
    writer.writerow(["Voltage", "UV-C Power", "Date", "Time"])
    file.close()

while True:
    nao = datetime.datetime.now()
    with open('uvbulbdata.csv', 'a') as file:
        writer = csv.writer(file)
        writer.writerow([chan.voltage, chan.voltage*4, nao.strftime("%x"), nao.strftime("%X")])
        file.close()
    time.sleep(10)
