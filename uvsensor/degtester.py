import asyncio
import sys

from uvsensor import UVsensor
from datasaver import backup_existing, writedata
from uvgrapher import UVSlackGrapher

class DegTester:
    def __init__(self, sensor, sint, gint, filepath, imagepath):
        self.chans = len(sensor.chan)
        self.grapher = UVSlackGrapher(self.chans, filepath, imagepath)
        self.sensor = sensor
        self.sint = sint
        self.gint = gint
        self.filepath = filepath
        self.imagepath = imagepath
        backup_existing(filepath, imagepath)
        
        headers = []
        for p in range(self.chans):
            headers.extend([f"Pin {p} Voltage", f"Pin {p} UV-C Power"])
        asyncio.run(writedata(headers+["Date", "Time", "Days Elapsed"], filepath))

    async def scheduler(self, interval, function):
        while True:
            await asyncio.gather(
                    asyncio.sleep(interval),
                    function()
                )

    async def readandwrite(self):
        data = self.sensor.get_reading()
        await writedata(data, self.filepath)

    def upload_file(self, channel, message, path): asyncio.run(self.grapher.upload_file(channel, message, path))

    def send_message(self, channel, message): asyncio.run(self.grapher.send_message(channel, message))

    async def staggered_graphing(self):
        await asyncio.sleep(self.gint*60)
        await self.scheduler(self.gint*60, self.grapher.genpost_graph)

    async def main(self):
        self.gathertree = await asyncio.gather(
                self.scheduler(self.sint*60, self.readandwrite),
                self.staggered_graphing()
            )

    def start(self):
        asyncio.run(self.main())

