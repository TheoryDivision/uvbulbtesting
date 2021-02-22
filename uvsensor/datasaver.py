import asyncio
import aiofiles
import shutil


async def writedata(data, filepath):
    async with aiofiles.open(filepath, "a") as f:
        for i in data[:-1]:
            await f.write(f"{i},")
        await f.write(f"{data[-1]}\n")

def copyfile(inputf, outputf): shutil.copyfile(inputf, outputf)

