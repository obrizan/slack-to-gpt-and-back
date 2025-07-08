FROM python:3.13-slim

# Install dependencies
COPY requirements.txt /app/requirements.txt
RUN pip install --no-cache-dir -r /app/requirements.txt

# Copy application code
COPY slack_webhook_handler.py /app/slack_webhook_handler.py

WORKDIR /app

EXPOSE 8000

CMD ["python", "slack_webhook_handler.py"]
