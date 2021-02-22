import asyncio
import sys

# from uvsensor import UVsensor
# from datasaver import writedata
# from uvgrapher import UVSlackGrapher

class DegTester:
    def __init__(self, sensor, sint, gint, filepath, imagepath):
        self.sensor = sensor
        self.sint = sint
        self.gint = gint
        self.filepath = filepath
        self.imagepath = imagepath
        self.grapher = UVSlackGrapher(filepath, imagepath)

        with open(filepath, "a") as f:
            f.write("Voltage, UV-C Power, Date, Time\n")


    async def scheduler(self, interval, function):
        while True:
            await asyncio.gather(
                    asyncio.sleep(interval),
                    function(),
                )

    async def readandwrite(self):
        await data = self.sensor.getreading()
        await writedata(data, self.filepath)

    async def main(self):
        self.gathertree = await asyncio.gather(
                self.scheduler(self.sint*60, self.readandwrite),
                self.scheduler(self.gint*60, self.grapher.graph),
                )

    def start(self):
        asyncio.run(self.main())

