import asyncio
import sys

from uvsensor import UVsensor
from datasaver import backup_existing, writedata
from uvgrapher import UVSlackGrapher

class DegTester:
    def __init__(self, sensor, args):
        self.__dict__.update(args.__dict__)
        self.chans = list(sensor.chan.keys())
        self.grapher = UVSlackGrapher(self.chans, self.graphlast, self.filepath, self.imagepath)
        self.sensor = sensor
        backup_existing(self.filepath, self.imagepath)
        self.sensetask = None
        
        headers = []
        for p in self.chans:
            headers.extend([f"Pin {p} Voltage", f"Pin {p} UV-C Power"])
        asyncio.run(writedata(headers + ["Temperature", "Date", "Time", "SUDS State","Days Elapsed"], self.filepath))

    async def scheduler(self, interval, function):
        while True:
            await asyncio.gather(asyncio.sleep(interval),
                    function())

    async def poweron(self):
        if self.sensetask is not None: self.sensetask.cancel()
        self.sensor.turnon()
        self.sensetask = asyncio.create_task(self.scheduler(self.sinton, self.readandwrite))
        await asyncio.sleep(self.on)
        self.powertask = asyncio.create_task(self.poweroff())

    async def poweroff(self):
        if self.sensetask is not None: self.sensetask.cancel()
        self.sensor.turnoff()
        self.sensetask = asyncio.create_task(self.scheduler(self.sintoff, self.readandwrite))
        await asyncio.sleep(self.off)
        self.powertask = asyncio.create_task(self.poweron())

    async def readandwrite(self):
        data = await self.sensor.get_reading()
        await writedata(data, self.filepath)

    def upload_file(self, channel, message, path): asyncio.run(self.grapher.upload_file(channel, message, path))

    def send_message(self, channel, message): asyncio.run(self.grapher.send_message(channel, message))

    async def graph(self):
        await asyncio.gather(asyncio.sleep(self.gint),
                                self.grapher.genpost_graph())
        self.graphtask = asyncio.create_task(self.graph())

    async def main(self):
        self.powertask = asyncio.create_task(self.poweron())
        await asyncio.sleep(self.gint)
        await self.graph()

    def start(self):
        self.loop = asyncio.new_event_loop()
        self.loop.create_task(self.main())
        self.loop.run_forever()

