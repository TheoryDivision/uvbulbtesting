import board
import busio
import adafruit_ads1x15.ads1015 as ADS
from adafruit_ads1x15.analog_in import AnalogIn
import csv
import datetime
import time

class UVrecorder:
    def __init__(self, pin, datafile, rec_interval):
        self.i2c = busio.I2C(board.SCL, board.SDA)
        self.ads = ADS.ADS1015(self.i2c)
        self.chan = AnalogIn(self.ads, getattr(ADS,'P'+ pin))
        self.ads.gain = 2/3
        self.datafile = datafile
        self.rec_interval = rec_interval
        with open(datafile, 'a') as file:
            writer = csv.writer(file)
            writer.writerow(["Voltage", "UV-C Power", "Date", "Time"])
            file.close()

    def getUVreading(self):
        nao = datetime.datetime.now()
        return [self.chan.voltage, self.chan.voltage*4, nao.strftime("%x"), nao.strftime("%X")]

    def saveUVreading(self):
        with open(self.datafile, 'a') as file:
            writer = csv.writer(file)
            writer.writerow(self.getUVreading())
            file.close()

