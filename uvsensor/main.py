#!/bin/python3

import argparse
import threading

from uvsensor import UVsensor
from degtester import DegTester
from uvbot import uvbot

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='UV Degredation Slack Bot')
    parser.add_argument('-p', '--pin', default='0', nargs='+', type=int, help='Pin(s) of ADC sensor is attached to')
    parser.add_argument('-G', '--gpio', default='17', type=int, help='GPIO pin for relay control')
    parser.add_argument('-f', '--off', default='5', type=float, help='Interval (minutes) for device off')
    parser.add_argument('-n', '--on', default='1', type=float, help='Interval (minutes) for device on')
    parser.add_argument('-sn', '--sinton', default='5', type=float, help='Interval (seconds) for sensing when device is on')
    parser.add_argument('-sf', '--sintoff', default='10', type=float, help='Interval (seconds) for sensing when device is off')
    parser.add_argument('-g', '--gint', default='90', type=float, help='Interval (minutes) for graphing')
    parser.add_argument('-l', '--graphlast', default='1200', type=int, help='Lines of data to graph')
    parser.add_argument('-o', '--filepath', default='uvdata.csv', type=str, help='File name for data')
    parser.add_argument('-i', '--imagepath', default='graph.png', type=str, help='Image name for graph')

    args = parser.parse_args()
    [args.on, args.off, args.gint] = [i * 60 for i in [args.on, args.off, args.gint]]
    sensor = UVsensor(args.pin, args.gpio)
    tester = DegTester(sensor, args)
    bot = threading.Thread(target = uvbot, args = (tester,))
    bot.start()
    tester.start()
