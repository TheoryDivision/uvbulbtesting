import asyncio
import aiofiles
from aiocsv import AsyncWriter

import os
from datetime import datetime

def backup_existing(filepath, imagepath):
    fexist = os.path.exists(filepath)
    iexist = os.path.exists(imagepath)
    if fexist or iexist:
        if not os.path.exists('backups'): os.makedirs('backups')
        fid = datetime.now().strftime("%m%d%y.%H%M")
        folder = f'backups/{fid}/'
        if not os.path.exists(folder): os.makedirs(folder)

        if fexist: os.rename(filepath, folder+filepath)
        if iexist: os.rename(imagepath, folder+imagepath)


async def writedata(data, filepath):
    async with aiofiles.open(filepath, "a", encoding="utf-8", newline="") as f:
        writer = AsyncWriter(f, dialect="unix")
        await writer.writerow(data)

