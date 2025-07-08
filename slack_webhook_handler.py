import os
from flask import Flask, request, jsonify
from slack_sdk import WebClient
from slack_sdk.errors import SlackApiError
from openai import OpenAI

SLACK_BOT_TOKEN = os.environ.get("SLACK_BOT_TOKEN")
OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY")
OPENAI_PROMPT_ID = os.environ.get("OPENAI_PROMPT_ID")
OPENAI_PROMPT_VERSION = os.environ.get("OPENAI_PROMPT_VERSION")

app = Flask(__name__)
slack_client = WebClient(token=SLACK_BOT_TOKEN)
openai_client = OpenAI()

@app.route("/slack/webhook", methods=["POST"])
def slack_webhook():
    data = request.get_json(force=True)

    if isinstance(data, dict) and data.get("type") == "url_verification":
        return jsonify({"challenge": data.get("challenge")})

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

    prompt = {
        "id": OPENAI_PROMPT_ID,
        "version": OPENAI_PROMPT_VERSION,
        "input": text,
    }
    ai_response_text = ""
    try:
        oa_resp = openai_client.responses.create(prompt=prompt)
        ai_response_text = getattr(oa_resp, "text", "") or oa_resp.get("text", "")
    except Exception as e:
        app.logger.exception("OpenAI responses API call failed")
        ai_response_text = f"Error calling OpenAI: {e}"

    if ai_response_text and channel:
        slack_client.chat_postMessage(channel=channel, text=ai_response_text)

    return "ok", 200

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 8000)))
