from typing import Final
import requests
from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes, JobQueue

# Telegram bot credentials
TOKEN: Final = '7407316205:AAHBkBw_LlyWgM6IBmZUOvOXqHgIzMV7fGI'
BOT_USERNAME: Final = '@Gygnusdon_bot'

# Dexscreener API endpoint
DEX_API_URL = "https://api.dexscreener.com/token-profiles/latest/v1"

# Global variable to store the previously notified tokens
previous_tokens = set()

# Function to fetch boosted tokens from DexScreener
def fetch_boosted_tokens():
    try:
        response = requests.get(DEX_API_URL)
        response.raise_for_status()  # Ensure we raise an error for bad responses
        return response.json()  # Parse the JSON response
    except requests.RequestException as e:
        print(f"Error fetching tokens: {e}")
        return None

# Function to send notifications for new boosted tokens
async def notify_boosted_tokens(context: ContextTypes.DEFAULT_TYPE):
    global previous_tokens

    data = fetch_boosted_tokens()
    
    if data:
        # No filtering, notify all tokens
        new_tokens = [token for token in data if token['tokenAddress'] not in previous_tokens]
        
        if new_tokens:
            for token in new_tokens:
                message = (
                    f"🚀 New Token Boosted! 🚀\n\n"
                    f"Name: {token.get('description', 'Unknown')}\n"
                    f"Amount Boosted: {coin.get('amount', 'N/A')}\n"
                    f"Total Boost: {coin.get('totalAmount', 'N/A')}\n"
                    f"More info: {token.get('url', 'No link available')}"
                )
                await context.bot.send_message(chat_id=context.job.chat_id, text=message)

            # Update the list of previously notified tokens
            previous_tokens.update(token['tokenAddress'] for token in new_tokens)

# Function to start the automatic notification job
async def start_auto_notifications(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id
    job_queue: JobQueue = context.job_queue
    job_queue.run_repeating(notify_boosted_tokens, interval=30, first=10, chat_id=chat_id)
    await update.message.reply_text("You will receive automatic notifications on boosted tokens!")

# Main function to run the bot
def main():
    application = Application.builder().token(TOKEN).build()
    application.add_handler(CommandHandler("start", start_auto_notifications))
    print("Bot is running...")
    application.run_polling()

if __name__ == "__main__":
    main()
