from flask import Flask, Response
from slackeventsapi import SlackEventAdapter
import os
import time
from threading import Thread
from slack import WebClient
from dotenv import load_dotenv
import psutil
from shutil import copyfile

class UVSlackBot:
    def __init__(self, filepath, imgpath):
        self.app = Flask(__name__)

        self.fpath = filepath
        self.ipath = imgpath
        base, ext = os.path.splitext(filepath)
        self.cpfpath = base + '_new' + ext

        self.greetings = ["hi", "hello", "hello there", "hey"]
        self.data_req = ["data", "send data", "data pls"]

        SLACK_SIGNING_SECRET = os.environ['SLACK_SIGNING_SECRET']
        slack_token = os.environ['SLACK_BOT_TOKEN']
        VERIFICATION_TOKEN = os.environ['VERIFICATION_TOKEN']

        #instantiating slack client
        self.slack_client = WebClient(slack_token)

        self.slack_events_adapter = SlackEventAdapter(
            SLACK_SIGNING_SECRET, "/slack/events", self.app
        )

    def has_handle(self, fpath):
        for proc in psutil.process_iter():
            try:
                for item in proc.open_files():
                    if fpath == item.path:
                        return True
            except Exception:
                pass

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
                    while True:
                        if not self.has_handle(self.fpath):
                            copyfile(self.fpath, self.cpfpath)
                            break
                        else:
                            time.sleep(1)
                    self.slack_client.files_upload(channel=channel_id, file=self.cpfpath ,initial_comment="Here it is.")
        thread = Thread(target=send_reply, kwargs={"value": event_data})
        thread.start()
        return Response(status=200)

    def start(self):
        self.app.run(port=3000)
