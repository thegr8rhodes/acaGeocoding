import os
import requests
from slack import WebClient
from dotenv import load_dotenv
from slackeventsapi import SlackEventAdapter
from slack_bolt import App
from slack_bolt.adapter.socket_mode import SocketModeHandler


load_dotenv()

SLACK_BOT_TOKEN = os.environ["user_oauth_token"]
SLACK_APP_TOKEN = os.environ["socket_mode_token"]

app = App(token=SLACK_BOT_TOKEN)

# Listens to incoming messages that contain "hello"
@app.message("hello")
def message_hello(message, say):
    # say() sends a message to the channel where the event was triggered
    say(
        blocks=[
            {
                "type": "section",
                "text": {"type": "mrkdwn", "text": f"Hey there <@{message['user']}>!"},
                "accessory": {
                    "type": "button",
                    "text": {"type": "plain_text", "text": "Click Me"},
                    "action_id": "button_click"
                }
            }
        ],
        text=f"Hey there <@{message['user']}>!"
    )

# Read Slack OAuth token and Google Geocoding API Key from config.json
import json

with open("config.json") as config_file:
    config = json.load(config_file)
    slack_token = config["slack_token"]
    google_api_key = config["google_api_key"]

client = WebClient(token=slack_token)

def geocode_address(address):
    url = f"https://maps.googleapis.com/maps/api/geocode/json?address={address}&key={google_api_key}"
    response = requests.get(url)
    data = response.json()
    if data['status'] == 'OK':
        location = data['results'][0]['geometry']['location']
        return location
    else:
        return None

# Example usage
address = "1600 Amphitheatre Parkway, Mountain View, CA"
location = geocode_address(address)
if location:
    message = f"Latitude: {location['lat']}, Longitude: {location['lng']}"
    client.chat_postMessage(channel="#general", text=message)
else:
    client.chat_postMessage(channel="#general", text="Geocoding failed.")
