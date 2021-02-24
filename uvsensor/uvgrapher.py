import asyncio
from slack_sdk.web.async_client import AsyncWebClient
from slack_sdk.errors import SlackApiError
import yaml

import pandas as pd
import matplotlib.pyplot as plt

class UVSlackGrapher:
    def __init__(self, chans, filepath, imagepath):
        self.slack_config = yaml.safe_load(open("slack_config.yml"))
        self.slack_client = AsyncWebClient(token=self.slack_config['SLACK_BOT_TOKEN'])
        self.filepath = filepath
        self.imagepath = imagepath
        self.chans = chans
        self.gs = False
        asyncio.run(self.init_messages())

    async def init_messages(self):
        await self.slack_client.chat_postMessage(
                channel=self.slack_config['CHANNEL'], 
                text="UV Degredation Experiment Started")
        graph_resp = await self.slack_client.chat_postMessage(
                channel=self.slack_config['CHANNEL'], 
                text="Graphs")
        self.graphts = graph_resp['ts']

    async def gen_graph(self):
        data = pd.read_csv(self.filepath, index_col='Days Elapsed')
        plt.rcParams["figure.dpi"] = 200
        headers = []
        for p in self.chans: headers.append(f"Pin {p} UV-C Power")
        plot = data[headers].plot()
        plot.set_ylabel(ylabel='mW/cm²')
        fig = plot.get_figure()
        fig.savefig(self.imagepath)
        fig.clf(); plot = None; fig = None
        if not self.gs: self.gs = True

    async def post_graph_rep(self):
        await self.slack_client.files_upload(
                channels=self.slack_config['CHANNEL'], 
                file=self.imagepath,
                thread_ts = self.graphts
                )

    async def genpost_graph(self):
        await self.gen_graph()
        await self.post_graph_rep()

    async def send_message(self, channel, message):
        await self.slack_client.chat_postMessage(
                channel=channel, 
                text=message)

    async def upload_file(self, channel, message, path):
        await self.slack_client.files_upload(
                channels=channel, 
                file=path,
                initial_comment=message
                )

