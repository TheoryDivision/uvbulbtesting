import board
import busio
import adafruit_ads1x15.ads1015 as ADS
from adafruit_ads1x15.analog_in import AnalogIn
import datetime

class UVsensor:
    def __init__(self, pin):
        self.i2c = busio.I2C(board.SCL, board.SDA)
        self.ads = ADS.ADS1015(self.i2c)
        self.chan = {}
        for p in pin: self.chan[p] = AnalogIn(self.ads, getattr(ADS,'P'+ str(p)))
        self.ads.gain = 2/3
        self.exp_start = datetime.datetime.now()

    def uptime(self):
        self.nao = datetime.datetime.now()
        diff = self.nao - self.exp_start
        return diff.total_seconds()/(12*60*60)

    def get_reading(self):
        days_elapsed = self.uptime()
        readings = []
        for adc in self.chan.values():
            v = adc.voltage
            readings.extend([v, v*4])
        return readings+[self.nao.strftime("%x"), self.nao.strftime("%X"), days_elapsed]
