import board
import busio
import adafruit_ads1x15.ads1015 as ADS
from adafruit_ads1x15.analog_in import AnalogIn
import csv
import datetime
import asyncio
import time

class UVsensor:
    def __init__(self, pin):
        self.i2c = busio.I2C(board.SCL, board.SDA)
        self.ads = ADS.ADS1015(self.i2c)
        self.chan = AnalogIn(self.ads, getattr(ADS,'P'+ pin))
        self.ads.gain = 2/3

    async def get_reading(self):
        nao = datetime.datetime.now()
        return [self.chan.voltage, self.chan.voltage*4, nao.strftime("%x"), nao.strftime("%X")]
