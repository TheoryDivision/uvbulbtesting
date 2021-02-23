from slackeventsapi import SlackEventAdapter
from slack_sdk import WebClient
import yaml
import os

from degtester import DegTester

def uvbot(tester, fpath, ipath):
    greetings = ["hi", "hello", "hey", "hai"]
    data_req = ["data", "csv"]
    graph_req = ["graph", "plot"]

    slack_config = yaml.safe_load(open("slack_config.yml"))
    slack_signing_secret = slack_config['SLACK_SIGNING_SECRET']

    slack_events_adapter = SlackEventAdapter(slack_signing_secret, "/slack/events")

    @slack_events_adapter.on("app_mention")
    def handle_message(event_data):
            message = event_data["event"]
            if message.get("subtype") is None:
                channel = message["channel"]
                if any(txt in message.get('text').lower() for txt in greetings):
                    tester.send_message(channel, f'Hello <@{message["user"]}>! :party_parrot:')
                elif "uptime" in message.get('text').lower():
                    days = round(tester.sensor.uptime(),2)
                    tester.send_message(channel, f"{days} days")
                elif any(txt in message.get('text').lower() for txt in data_req):
                    tester.upload_file(channel, "Here is the most recent file:", fpath)
                elif any(txt in message.get('text').lower() for txt in graph_req):
                    if os.path.exists(ipath):
                        tester.upload_file(channel, "Here you go:", ipath)
                    else:
                        tester.send_message(channel, "A graph has not been generated yet. Check back later.")

    @slack_events_adapter.on("error")
    def error_handler(err):
        print("ERROR: " + str(err))

    slack_events_adapter.start(port=3000)
