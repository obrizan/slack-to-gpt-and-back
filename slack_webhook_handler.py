import os
from flask import Flask, request, jsonify, g
from time import time
from slack_sdk import WebClient
from slack_sdk.errors import SlackApiError
import ssl
import certifi
from openai import OpenAI
import logging

SLACK_BOT_TOKEN = os.environ.get("SLACK_BOT_TOKEN")
OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY")
OPENAI_PROMPT_ID = os.environ["OPENAI_PROMPT_ID"]
OPENAI_PROMPT_VERSION = os.environ["OPENAI_PROMPT_VERSION"]

app = Flask(__name__)

logging.basicConfig(
    level=logging.DEBUG,
    format='[%(asctime)s] %(levelname)s in %(module)s: %(message)s',
)

@app.before_request
def log_request_info():
    g.start_time = time()
    app.logger.info(
        "REQUEST:\nMethod: %s\nPath: %s\nHeaders: %s\nBody: %s",
        request.method,
        request.path,
        dict(request.headers),
        request.get_data(as_text=True)
    )

@app.after_request
def log_response_info(response):
    duration = time() - g.get("start_time", time())
    app.logger.info(
        "RESPONSE:\nStatus: %s\nHeaders: %s\nBody: %s\nDuration: %.3f sec",
        response.status,
        dict(response.headers),
        response.get_data(as_text=True),
        duration
    )
    return response

# Use certifi to provide CA certificates for SSL verification
ssl_context = ssl.create_default_context(cafile=certifi.where())
slack_client = WebClient(token=SLACK_BOT_TOKEN, ssl=ssl_context)

openai_client = OpenAI()


@app.route("/slack/webhook", methods=["POST"])
def slack_webhook():
    data = request.get_json(force=True)

    if isinstance(data, dict) and data.get("type") == "url_verification":
        return jsonify({"challenge": data.get("challenge", "")}), 200

    event = None
    if isinstance(data, list) and data:
        event = data[0]
    elif isinstance(data, dict):
        event = data.get("event", data)

    if not event or event.get("type") != "message":
        return "ignored", 200

    user_id = event.get("user")
    text = event.get("text", "")
    channel = event.get("channel")

    profile = {}
    if user_id:
        try:
            profile_resp = slack_client.users_profile_get(user=user_id)
            if profile_resp["ok"]:
                profile = profile_resp["profile"]
        except SlackApiError:
            pass

    ai_response_text = ""
    try:
        oa_resp = openai_client.responses.create(
            prompt={
                "id": OPENAI_PROMPT_ID,
                "version": OPENAI_PROMPT_VERSION,
            },
            input=text,
        )
        ai_response_text = oa_resp.output_text
    except Exception as e:
        app.logger.exception("OpenAI responses API call failed")
        ai_response_text = f"Error calling OpenAI: {e}"

    if ai_response_text and channel:
        slack_client.chat_postMessage(channel=channel, text=ai_response_text)

    return "ok", 200


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 8000)))
