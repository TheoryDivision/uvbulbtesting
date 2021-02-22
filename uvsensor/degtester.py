import asyncio
import sys

# from uvsensor import UVsensor
# from datasaver import writedata

class DegTester:
    def __init__(self, sensor, sint, gint, filepath, imagepath):
        self.sensor = sensor
        self.sint = sint
        self.gint = gint
        self.filepath = filepath
        self.imagepath = imagepath

        with open(output, "a") as f:
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
        gathertree = await asyncio.gather(
                self.scheduler(15*60, self.readandwrite)
                    )
                )

    def start(self):
        asyncio.run(self.main())

