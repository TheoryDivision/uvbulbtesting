import asyncio
from slack_sdk.web.async_client import AsyncWebClient
# from slack_sdk.errors import SlackApiError
from dotenv import load_dotenv

import pandas as pd
import matplotlib.pyplot as plt


class UVSlackGrapher:
    def __init__(self, filepath, imagepath):
        self.client = AsyncWebClient(token=os.environ['SLACK_BOT_TOKEN'])
        self.filepath = filepath
        self.imagepath = imagepath

    async def submit_graph(self):

