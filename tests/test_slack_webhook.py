import json
import importlib
from unittest.mock import MagicMock

import pytest


@pytest.fixture
def app_client(monkeypatch):
    monkeypatch.setenv("OPENAI_API_KEY", "x")
    monkeypatch.setenv("SLACK_BOT_TOKEN", "x")

    handler = importlib.import_module("slack_webhook_handler")

    with open('tests/slack_get_profile_response.json') as f:
        profile = json.load(f)[0]

    mock_slack = MagicMock()
    mock_slack.users_profile_get.return_value = {"ok": True, "profile": profile}
    mock_slack.chat_postMessage.return_value = {"ok": True}
    monkeypatch.setattr(handler, "slack_client", mock_slack)

    mock_openai = MagicMock()
    mock_openai.responses.create.return_value = MagicMock(text="AI reply")
    monkeypatch.setattr(handler, "openai_client", mock_openai)
    monkeypatch.setattr(handler, "OPENAI_PROMPT_ID", "pid")
    monkeypatch.setattr(handler, "OPENAI_PROMPT_VERSION", "v1")

    return handler.app.test_client(), handler


def test_webhook_message(app_client):
    client, handler = app_client

    with open('tests/slack_webhook_payload.json') as f:
        payload = json.load(f)

    resp = client.post('/slack/webhook', json=payload)
    assert resp.status_code == 200
    assert resp.data == b"ok"

    handler.slack_client.users_profile_get.assert_called_once_with(user="example_user_id")
    handler.openai_client.responses.create.assert_called_once()
    handler.slack_client.chat_postMessage.assert_called_once_with(channel="example_channel", text="AI reply")

