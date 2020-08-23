import json
import os
import logging
import gzip
import base64
from urllib.request import Request, urlopen, URLError, HTTPError

# Logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)


def lambda_handler(event, context):
    # Retrieve data from CloudWatch
    cloudwatch_data = event['awslogs']['data']

    # Data is encoded, so base64 decode then decompress gzip
    decompress = gzip.decompress(base64.b64decode(cloudwatch_data))

    # Cast to dict
    ascii_msg = decompress.decode('ascii')
    ascii_msg = ascii_msg.replace("'", "\"")
    output_dict = json.loads(ascii_msg)

    # Get the main message
    event_detail = json.loads(output_dict['logEvents'][0]['message'])

    # Slack
    channel = os.environ['CHANNEL']
    headers = {"Content-Type": "application/json"}
    slack_message = {
        "type": "mrkdwn",
        "text": ":t-rex: AWS Root " + event_detail["eventName"] + " detected from " + event_detail[
            "sourceIPAddress"],
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
