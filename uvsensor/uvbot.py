from slackeventsapi import SlackEventAdapter
import yaml
import re

from degtester import DegTester

def uvbot(tester, fpath, ipath):
    greetings = ["hi", "hello", "hey", "hai", "sup"]
    data_req = ["data", "csv"]
    graph_req = ["graph", "plot"]

    slack_config = yaml.safe_load(open("slack_config.yml"))
    slack_signing_secret = slack_config['SLACK_SIGNING_SECRET']

    slack_events_adapter = SlackEventAdapter(slack_signing_secret, "/slack/events")

    def extract_mins(string):
        numbers = re.findall(r"[-+]?\d*\.?\d+|[-+]?\d+", string)
        if "min" in string:
            return float(numbers[-1])
        if "hour" in string:
            return float(numbers[-1]*60)

    @slack_events_adapter.on("app_mention")
    def handle_message(event_data):
            message = event_data["event"]
            mtext = message.get('text').lower()
            if message.get("subtype") is None:
                channel = message["channel"]
                if any(txt in mtext for txt in greetings):
                    tester.send_message(channel, f'Hello <@{message["user"]}>! :party_parrot:')
                elif "uptime" in mtext:
                    days = round(tester.sensor.uptime(),2)
                    tester.send_message(channel, f"{days} days")
                elif any(txt in mtext for txt in data_req):
                    tester.upload_file(channel, "Here is the most recent file:", fpath)
                elif "param" in mtext:
                    tester.send_message(channel, f"Read/Write Interval: {tester.sint} minutes\nGraphing Interval: {tester.gint} minutes")
                elif "adjust" in mtext:
                    if "rw" in mtext:
                        tester.sint = extract_mins(mtext)
                        tester.send_message(channel, "Confirmed.")
                        tester.send_message(channel, f" Changed Read/Write Interval: {tester.sint} minutes\nGraphing Interval: {tester.gint} minutes")
                    elif "graph" in mtext:
                        tester.gint = extract_mins(mtext)
                        tester.send_message(channel, "Confirmed.")
                        tester.send_message(channel, f"Read/Write Interval: {tester.sint} minutes\nChanged Graphing Interval: {tester.gint} minutes")
                elif any(txt in mtext for txt in graph_req):
                    if tester.grapher.gs:
                        tester.upload_file(channel, "Here you go:", ipath)
                    else:
                        tester.send_message(channel, "A graph has not been generated yet. Check back later.")

    @slack_events_adapter.on("error")
    def error_handler(err):
        print("ERROR: " + str(err))

    slack_events_adapter.start(port=3000)
