import asyncio
from slack_sdk.web.async_client import AsyncWebClient
from slack_sdk.errors import SlackApiError
import yaml

import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.collections import PatchCollection
from matplotlib.patches import Polygon

class UVSlackGrapher:
    def __init__(self, chans, graphlast, filepath, imagepath):
        self.slack_config = yaml.safe_load(open("slack_config.yml"))
        self.slack_client = AsyncWebClient(token=self.slack_config['SLACK_BOT_TOKEN'])
        self.filepath = filepath
        self.imagepath = imagepath
        self.graphlast = graphlast
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

    def gen_graph(self):
        rawdata = pd.read_csv(self.filepath)
        data = rawdata.tail(self.graphlast)
        plt.rcParams["figure.dpi"] = 200
        headers = []
        for p in self.chans: headers.append(f"Pin {p} UV-C Power")
        plot = data.plot(x="Days Elapsed", y=headers, figsize=(9,9), zorder=2, style=['o']*len(headers))
        axes = plt.gca()
        ymin, ymax = axes.get_ylim()
        poly = []
        for index, row in data.iterrows():
            if index > data.index.start:
                if row["SUDS State"] == "On":
                    points = [[data.loc[index-1,:]["Days Elapsed"], ymin], [row["Days Elapsed"], ymin], [row["Days Elapsed"], ymax], [data.loc[index-1,:]["Days Elapsed"], ymax]]
                    polygon = plt.Polygon(points)
                    poly.append(polygon)
        coll=PatchCollection(poly, zorder=-1, color="tab:green", alpha=0.125, edgecolor=None, linewidth=None)
        axes.add_collection(coll)
        lines, labels = plot.get_legend_handles_labels()
        tempax = plot.twinx()
        data.plot(ax=tempax, x="Days Elapsed", y="Temperature", c="tab:red", legend=False, alpha=0.6, style=['x'], zorder=1)
        line, label = tempax.get_legend_handles_labels()
        lines+=line
        labels+=label
        plot.legend(lines, labels, loc=4)
        plot.set_ylabel(ylabel='mW/cm²')
        tempax.set_ylabel(ylabel='°C')
        fig = plot.get_figure()
        fig.savefig(self.imagepath)
        fig.clf(); plot = None; fig = None
        if not self.gs: self.gs = True

    async def post_graph_rep(self):
        await self.slack_client.files_upload(
                channels=self.slack_config['CHANNEL'], 
                file=self.imagepath,
                thread_ts = self.graphts)

    async def genpost_graph(self):
        self.gen_graph()
        await self.post_graph_rep()

    async def send_message(self, channel, message):
        await self.slack_client.chat_postMessage(
                channel=channel, 
                text=message)

    async def upload_file(self, channel, message, path):
        await self.slack_client.files_upload(
                channels=channel, 
                file=path,
                initial_comment=message)

