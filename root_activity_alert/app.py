import json
import os
import logging
from urllib.request import Request, urlopen, URLError, HTTPError

# Logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)


def lambda_handler(event, context):
    channel = os.environ['CHANNEL']
    headers = {"Content-Type": "application/json"}
    slack_message = {
        "type": "mrkdwn",
        "text": ":exclamation: *AWS Root usage " + event["detail"]["awsRegion"] + "* (" + event["detail"][
            "eventName"] + ") detected from " + event["detail"]["sourceIPAddress"] + "\n>" + json.dumps(event),
        "emoji": ":exclamation:"
    }
    slack_webhook = "https://hooks.slack.com/services/" + channel
    req = Request(slack_webhook, data=bytes(json.dumps(slack_message), encoding="utf-8"), headers=headers)
    try:
        response = urlopen(req)
        response.read()
        logger.info("Message posted to %s", channel)
    except HTTPError as e:
        logger.error("Request failed: %d %s", e.code, e.reason)
    except URLError as e:
        logger.error("Server connection failed: %s", e.reason)
