import asyncio
from slack_sdk.web.async_client import AsyncWebClient
# from slack_sdk.errors import SlackApiError
import yaml

import pandas as pd
import matplotlib.pyplot as plt


class UVSlackGrapher:
    def __init__(self, filepath, imagepath):
        self.slack_config = yaml.safe_load(open("slack_config.yml"))
        self.slack_client = AsyncWebClient(token=self.slack_config['SLACK_BOT_TOKEN'])
        self.filepath = filepath
        self.imagepath = imagepath
        asyncio.run(self.init_messages())

    async def init_messages(self):
        await client.chat_postMessage(
                channel=self.slack_config['CHANNEL'], 
                text="UV Degredation Experiment Started")
        graph_resp = await client.chat_postMessage(
                channel=self.slack_config['CHANNEL'], 
                text="Graphs")
        self.graphts = graph_resp['ts']

    async def gen_graph(self):
        data = pd.read(self.filepath, index_col='Days Elapsed')
        plt.rcParams["figure.dpi"] = 200
        plot = data[['UV-C Power']].plot()
        fig = plot.get_figure()
        fig.savefig(self.imagepath)

    async def post_graph(self):
        await self.slack_client.files_upload(
                channels=self.slack_config['CHANNEL'], 
                file=self.imagepath,
                thread_ts = self.graphts
                )

    async def genpost_graph(self):
        await self.gen_graph()
        await self.post_graph()

