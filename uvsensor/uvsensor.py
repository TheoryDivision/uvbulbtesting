import board
import busio
import adafruit_ads1x15.ads1015 as ADS
from adafruit_ads1x15.analog_in import AnalogIn
import datetime

class UVsensor:
    def __init__(self, pin):
        self.i2c = busio.I2C(board.SCL, board.SDA)
        self.ads = ADS.ADS1015(self.i2c)
        self.chan = AnalogIn(self.ads, getattr(ADS,'P'+ str(pin)))
        self.ads.gain = 2/3
        self.exp_start = datetime.datetime.now()

    def uptime(self):
        self.nao = datetime.datetime.now()
        diff = self.nao - self.exp_start
        return diff.total_seconds()/(12*60*60)

    def get_reading(self):
        days_elapsed = self.uptime()
        return [self.chan.voltage, self.chan.voltage*4, self.nao.strftime("%x"), self.nao.strftime("%X"), days_elapsed]
