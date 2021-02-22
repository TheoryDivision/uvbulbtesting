import asyncio
import aiofiles
from aiocsv import AsyncWriter
import shutil

async def writedata(data, filepath):
    async with aiofiles.open(filepath, "a", encoding="utf-8", newline="") as f:
        writer = AsyncWriter(f, dialect="unix")
        await writer.writerow(data)

def copyfile(inputf, outputf): shutil.copyfile(inputf, outputf)

