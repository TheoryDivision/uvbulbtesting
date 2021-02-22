import asyncio
import aiofiles

async def writedata(data, filepath):
    async with aiofiles.open(filepath, "a") as f:
        for i in data[:-1]:
            await f.write(f"{i},")
        await f.write(f"{data[-1]}\n")
