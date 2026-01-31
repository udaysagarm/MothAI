import os
import requests
from langchain.tools import tool
from dotenv import load_dotenv

load_dotenv()

@tool
def send_telegram_alert(message: str) -> str:
    """
    Sends a proactive notification to the user via Telegram.
    Use this to notify the user when a task is done, a decision is needed, or for daily summaries.
    """
    token = os.getenv("TELEGRAM_BOT_TOKEN")
    chat_id = os.getenv("TELEGRAM_CHAT_ID")
    
    if not token or not chat_id:
        return "Error: Telegram credentials missing in .env"

    # Fixed the URL string which had markdown syntax in the user request
    url = f"https://api.telegram.org/bot{token}/sendMessage"
    payload = {
        "chat_id": chat_id,
        "text": message
    }
    
    try:
        response = requests.post(url, json=payload, timeout=10)
        if response.status_code == 200:
            return "Notification sent successfully."
        else:
            return f"Failed to send Telegram: {response.text}"
    except Exception as e:
        return f"Telegram Connection Error: {e}"
