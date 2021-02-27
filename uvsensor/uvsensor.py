import board
import busio
import datetime

import adafruit_ads1x15.ads1015 as ADS
from adafruit_ads1x15.analog_in import AnalogIn
import RPi.GPIO as GPIO
from w1thermsensor import AsyncW1ThermSensor, Unit


class UVsensor:
    def __init__(self, pin, gpiop):
        self.i2c = busio.I2C(board.SCL, board.SDA)
        self.ads = ADS.ADS1015(self.i2c)
        self.chan = {}
        for p in pin: self.chan[p] = AnalogIn(self.ads, getattr(ADS,'P'+ str(p)))

        self.gpiop = gpiop
        GPIO.setmode(GPIO.BCM)
        GPIO.setup(gpiop, GPIO.OUT)
        self.powerstate = False

        self.tempsensor = AsyncW1ThermSensor()
        self.exp_start = datetime.datetime.now()

    def turnon(self):
        GPIO.output(self.gpiop, GPIO.HIGH)
        self.powerstate = True

    def turnoff(self):
        GPIO.output(self.gpiop, GPIO.LOW)
        self.powerstate = False
    
    def uptime(self):
        self.nao = datetime.datetime.now()
        diff = self.nao - self.exp_start
        return diff.total_seconds()

    async def get_reading(self):
        temp = await self.tempsensor.get_temperature()
        days_elapsed = self.uptime()/(24*60*60)
        readings = []
        state = "On" if self.powerstate else "Off"
        for adc in self.chan.values():
            v = adc.voltage
            readings.extend([v, v*4])
        return readings+[temp, self.nao.strftime("%x"), self.nao.strftime("%X"), state, days_elapsed]
