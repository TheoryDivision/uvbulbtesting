#!/bin/python3

import argparse
import threading

from uvsensor import UVsensor
from degtester import DegTester
from uvbot import uvbot

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='UV Degredation Slack Bot')
    parser.add_argument('-p', '--pin', default='0', type=int, help='Pin of ADC sensor is attached to')
    parser.add_argument('-s', '--sint', default='15', type=float, help='Interval (minutes) for sensing')
    parser.add_argument('-g', '--gint', default='90', type=float, help='Interval (minutes) for graphing')
    parser.add_argument('-o', '--output', default='uvdata.csv', type=str, help='File name for data')
    parser.add_argument('-i', '--image', default='graph.png', type=str, help='Image name for graph')

    args = parser.parse_args()

    sensor = UVsensor(args.pin)
    tester = DegTester(sensor, args.sint, args.gint, args.output, args.image)
    bot = threading.Thread(target = uvbot, args = (tester, args.output, args.image))
    bot.start()
    tester.start()
