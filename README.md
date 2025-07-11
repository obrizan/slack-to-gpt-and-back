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
   - `HOST` – Host to bind to (Docker compose).
   - `PORT` – Port to bind to (Docker compose).
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

### Running with Docker Compose

You can also launch the service using `docker-compose`. Create a `.env` file (for example by copying `.example.env`) and populate it with the required environment variables. Then run:

```bash
docker-compose up --build
```

The application will be available on `http://localhost:8000/slack/webhook`.

## Slack verification challenge

Example `curl` verification request (recorded from actual call to webhook.site, `content-lenght` and `host` headers are removed):

```bash
curl --compressed -i -X 'POST' 'https://example.com/' \
  -H 'x-slack-request-timestamp: 1752230969' \
  -H 'x-slack-signature: v0=3ae6b229f397cfbd2e307cca7935ae4c409d3e57a82ab3764a531698c4e8d8de' \
  -H 'content-type: application/json' \
  -H 'accept-encoding: gzip,deflate' \
  -H 'accept: */*' \
  -H 'user-agent: Slackbot 1.0 (+https://api.slack.com/robots)' \
  -d $'{"token":"token","challenge":"widk3LpTzv27InfrlIs8ZVHmTndX7PhiQZcUYRc6EbtYetrAfsb4","type":"url_verification"}'
```

Expected response ([url_verification event](https://api.slack.com/events/url_verification)):

```text
HTTP/1.1 200 OK
Server: nginx/1.18.0 (Ubuntu)
Date: Fri, 11 Jul 2025 12:29:49 GMT
Content-Type: application/json
Connection: close
Content-Encoding: gzip

{"challenge":"widk3LpTzv27InfrlIs8ZVHmTndX7PhiQZcUYRc6EbtYetrAfsb4"}
```
