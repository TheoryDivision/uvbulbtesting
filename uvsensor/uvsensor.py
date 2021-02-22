import board
import busio
import adafruit_ads1x15.ads1015 as ADS
from adafruit_ads1x15.analog_in import AnalogIn
import datetime
import asyncio

class UVsensor:
    def __init__(self, pin):
        self.i2c = busio.I2C(board.SCL, board.SDA)
        self.ads = ADS.ADS1015(self.i2c)
        self.chan = AnalogIn(self.ads, getattr(ADS,'P'+ pin))
        self.ads.gain = 2/3
        self.exp_start = datetime.datetime.now()

    async def get_reading(self):
        nao = datetime.datetime.now()
        diff = self.exp_start - nao
        days_elapsed = diff.total_seconds()/(12*60*60)
        return [self.chan.voltage, self.chan.voltage*4, nao.strftime("%x"), nao.strftime("%X"), days_elapsed]
