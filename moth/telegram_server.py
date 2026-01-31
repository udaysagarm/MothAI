import os
import telebot
from dotenv import load_dotenv
from moth.agent import run_agent
import threading
import time
from moth.tools.gmail_ops import read_recent_emails
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.messages import SystemMessage, HumanMessage

# Load environment variables
load_dotenv()

# Initialize Bot
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")

if not TELEGRAM_BOT_TOKEN:
    print("Error: TELEGRAM_BOT_TOKEN not found in .env")
    exit(1)

bot = telebot.TeleBot(TELEGRAM_BOT_TOKEN)

print("Moth AI Telegram Bot is running...")

@bot.message_handler(func=lambda message: True)
def handle_message(message):
    """
    Listens for ANY text message, sends it to Moth AI agent, 
    and replies with the response.
    """
    user_id = message.chat.id
    user_input = message.text
    
    print(f"Received from {user_id}: {user_input}")

    try:
        # Show "Typing..." status
        bot.send_chat_action(user_id, 'typing')
        
        # Run Agent
        # Pass empty list for chat_history as it's now handled by the persistent DB
        response = run_agent(user_input, chat_history=[])
        
        # Send Reply
        bot.reply_to(message, response)
        
    except Exception as e:
        error_msg = f"⚠️ Error processing message: {str(e)}"
        print(error_msg)
        bot.send_message(user_id, error_msg)

def run_supervisor():
    """
    Background thread that checks for urgent emails every 15 minutes.
    """
    print("👀 Supervisor started: Monitoring emails every 15 minutes...")
    chat_id = os.getenv("TELEGRAM_CHAT_ID")
    if not chat_id:
        print("⚠️ Supervisor Warning: TELEGRAM_CHAT_ID not found. Notifications disabled.")
        return

    # Initialize LLM for analysis
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        print("⚠️ Supervisor Warning: GEMINI_API_KEY not found.")
        return

    # Use the same model logic as agent, maybe simpler
    llm = ChatGoogleGenerativeAI(model="gemini-2.0-flash", google_api_key=api_key)

    while True:
        try:
            print("👀 Supervisor: Checking for urgent emails...")
            # 1. Get recent emails (invoke tool)
            email_summary = read_recent_emails.invoke({"limit": 3})
            
            # 2. Analyze
            system_prompt = "Analyze these emails. If any are URGENT or require immediate attention, return a short summary. Otherwise, return 'NO_ALERT'."
            messages = [
                SystemMessage(content=system_prompt),
                HumanMessage(content=f"Here are the recent emails:\n{email_summary}")
            ]
            response = llm.invoke(messages)
            content = response.content.strip()
            
            if "NO_ALERT" not in content:
                print("🚨 Supervisor: Urgent email detected! Notifying user.")
                bot.send_message(chat_id, f"🚨 **Moth Supervisor Alert** 🚨\n\n{content}")
            else:
                print("✅ Supervisor: No urgent emails found.")
                
        except Exception as e:
            print(f"⚠️ Supervisor Error: {e}")
            
        # Sleep 15 mins (900 seconds)
        time.sleep(900)

if __name__ == "__main__":
    # Start Supervisor Thread
    if os.getenv("TELEGRAM_CHAT_ID"):
        supervisor_thread = threading.Thread(target=run_supervisor, daemon=True)
        supervisor_thread.start()
    else:
        print("Skipping Supervisor: No TELEGRAM_CHAT_ID env var found.")

    try:
        bot.infinity_polling()
    except KeyboardInterrupt:
        print("\nStopping Telegram Bot...")
