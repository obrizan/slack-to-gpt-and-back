# slack-to-gpt-and-back

Slackbot integrated with OpenAI response API with predefined prompt and tools.

## Slack webhook handler

`slack_webhook_handler.py` implements a small Flask application that accepts
Slack message webhooks. It retrieves the user's full profile, forwards the text
prompt to OpenAI using the responses API and sends the AI reply back to the
original Slack channel.

### Running locally

1. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
   The project uses `certifi` so that SSL requests to Slack work even on
   systems without global certificate bundles.
2. Set environment variables:
   - `SLACK_BOT_TOKEN` – Bot token to call Slack APIs.
   - `OPENAI_API_KEY` – API key for OpenAI.
   - `OPENAI_PROMPT_ID` – ID of the predefined OpenAI prompt.
   - `OPENAI_PROMPT_VERSION` – Prompt version for your predefined prompt.
3. Start the server:
   ```bash
   python slack_webhook_handler.py
   ```

The server exposes `/slack/webhook` for Slack to send events.

### Running with Docker

To build and run the application using Docker:

```bash
# build the image
docker build -t slack-to-gpt .

# run the container
# Environment variables listed above must be set
# 8000 is the default port exposed by the Flask app

docker run -p 8000:8000 -e SLACK_BOT_TOKEN=... -e OPENAI_API_KEY=... \
  -e OPENAI_PROMPT_ID=... -e OPENAI_PROMPT_VERSION=... slack-to-gpt
```

The application will be available on `http://localhost:8000/slack/webhook`.
