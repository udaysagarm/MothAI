#!/bin/bash
echo "Starting Moth AI Telegram Server..."
source venv/bin/activate
exec python -m moth.telegram_server
