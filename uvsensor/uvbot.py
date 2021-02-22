from flask import Flask, Response
from slackeventsapi import SlackEventAdapter
import os
from threading import Thread
from slack import WebClient
import yaml

from degtester import DegTester

class UVSlackBot:
    def __init__(self, tester, filepath, imgpath):
        self.app = Flask(__name__)
        self.tester = tester

        self.fpath = filepath
        self.ipath = imgpath
        base, ext = os.path.splitext(filepath)
        self.cpfpath = base + '_new' + ext

        self.greetings = ["hi", "hello", "hello there", "hey"]
        self.data_req = ["data", "send data", "data pls"]

        self.slack_config = yaml.safe_load(open("slack_config.yml"))

        self.slack_client = WebClient(self.slack_config['SLACK_BOT_TOKEN'])

    # An example of one of your Flask app's routes
    @app.route("/")
    def event_hook(self, request):
        json_dict = json.loads(request.body.decode("utf-8"))
        if json_dict["token"] != self.slack_config['VERIFICATION_TOKEN']:
            return {"status": 403}

        if "type" in json_dict:
            if json_dict["type"] == "url_verification":
                response_dict = {"challenge": json_dict["challenge"]}
                return response_dict
        return {"status": 500}
        return

    self.slack_events_adapter = SlackEventAdapter(
        self.slack_config['SLACK_SIGNING_SECRET'], "/slack/events", self.app
    )

    @self.slack_events_adapter.on("app_mention")
    def handle_message(self, event_data):
        def send_reply(value):
            event_data = value
            message = event_data["event"]
            if message.get("subtype") is None:
                command = message.get("text")
                channel_id = message["channel"]
                if any(item in command.lower() for item in self.greetings):
                    message = (
                        "Hello <@%s>! :party_parrot:"
                        % message["user"] 
                    )
                    self.slack_client.chat_postMessage(channel=channel_id, text=message)
                if any(item in command.lower() for item in self.data_req):
                    self.tester.copydata(self.fpath, self.cpfpath)
                    self.slack_client.files_upload(channel=channel_id, file=self.cpfpath ,initial_comment="Here it is.")
                    os.remove(self.cpfpath)
        thread = Thread(target=send_reply, kwargs={"value": event_data})
        thread.start()
        return Response(status=200)

    def start(self):
        self.app.run(port=3000)
