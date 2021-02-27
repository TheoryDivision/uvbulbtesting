from slackeventsapi import SlackEventAdapter
import yaml
import re

from degtester import DegTester

def uvbot(tester):
    greetings = ["hi", "hello", "hey", "hai", "sup"]
    data_req = ["data", "csv"]
    graph_req = ["graph", "plot"]
    cycle_req = ["cycle", "loop"]

    slack_config = yaml.safe_load(open("slack_config.yml"))
    slack_signing_secret = slack_config['SLACK_SIGNING_SECRET']

    slack_events_adapter = SlackEventAdapter(slack_signing_secret, "/slack/events")

    def extract_mins(string):
        numbers = re.findall("[-+]?\d*\.?\d+|[-+]?\d+", string)
        if "hour" in string:
            return float(numbers[-1])*60*60
        elif "min" in string:
            return float(numbers[-1])*60
        elif "sec" in string:
            return float(numbers[-1])

    def report_params(confirm, channel): 
        if confirm: tester.send_message(channel, "Confirmed.")
        tester.send_message(channel, 
                "Power Cycle Interval:\n"\
                f"\t On: {tester.on/60} minutes\n"\
                f"\t Off: {tester.off/60} minutes\n"\
                "Read/Write Interval:\n"\
                f"\t On: {tester.sinton} seconds\n"\
                f"\t Off: {tester.sintoff} seconds\n"\
                "Graphing:\n"\
                f"\t Interval: {tester.gint/60} minutes\n"\
                f"\t Lines to Graph: {tester.grapher.graphlast} lines of data")

    def secondsToText(secs):     
        if secs:
            days = secs//86400
            hours = (secs - days*86400)//3600
            minutes = (secs - days*86400 - hours*3600)//60
            seconds = secs - days*86400 - hours*3600 - minutes*60
            result = ("{0} day{1}, ".format(days, "s" if days!=1 else "") if days else "") + \
            ("{0} hour{1}, ".format(hours, "s" if hours!=1 else "") if hours else "") + \
            ("{0} minute{1}, ".format(minutes, "s" if minutes!=1 else "") if minutes else "") + \
            ("{0} second{1}, ".format(seconds, "s" if seconds!=1 else "") if seconds else "")
            return result[:-2]
        else:
            return "0 seconds"

    @slack_events_adapter.on("app_mention")
    def handle_message(event_data):
            message = event_data["event"]
            mtext = re.sub("<[^>]*>", "", message.get('text').lower())
            if message.get("subtype") is None:
                channel = message["channel"]
                if any(txt in mtext for txt in greetings):
                    tester.send_message(channel, f'Hello <@{message["user"]}>! :party_parrot:')
                elif "uptime" in mtext:
                    uptimetext = secondsToText(int(tester.sensor.uptime()))
                    tester.send_message(channel, uptimetext)
                elif any(txt in mtext for txt in data_req):
                    tester.upload_file(channel, "Here is the most recent file:", tester.filepath)
                elif any(txt in mtext for txt in cycle_req):
                    tester.send_message(channel, f"Cycles: {tester.cycles}")
                elif "latest" in mtext:
                    tester.sendlastline(channel)
                elif "param" in mtext:
                    report_params(False, channel)
                elif "adjust" in mtext:
                    if "power" in mtext:
                        if "on" in mtext:
                            tester.on = extract_mins(mtext)
                            report_params(True, channel)
                        elif "off" in mtext:
                            tester.off = extract_mins(mtext)
                            report_params(True, channel)
                    if "rw" in mtext:
                        if "on" in mtext:
                            tester.sinton = extract_mins(mtext)
                            report_params(True, channel)
                        elif "off" in mtext:
                            tester.sintoff = extract_mins(mtext)
                            report_params(True, channel)
                    elif "graph" in mtext:
                        if "int" in mtext:
                            tester.gint = extract_mins(mtext)
                            report_params(True, channel)
                        if "line" in mtext:
                            numbers = re.findall("[-+]?\d*\.?\d+|[-+]?\d+", mtext)
                            tester.grapher.graphlast = int(numbers[-1])
                            report_params(True, channel)
                elif any(txt in mtext for txt in graph_req):
                    if tester.grapher.gs:
                        tester.upload_file(channel, "Here you go:", tester.imagepath)
                    else:
                        tester.send_message(channel, "A graph has not been generated yet. Check back later.")

    @slack_events_adapter.on("error")
    def error_handler(err):
        print("ERROR: " + str(err))

    slack_events_adapter.start(port=3000)
