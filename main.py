from typing import Final
import requests
from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes, JobQueue

# Telegram bot credentials
TOKEN: Final = '7407316205:AAHBkBw_LlyWgM6IBmZUOvOXqHgIzMV7fGI'
BOT_USERNAME: Final = '@Gygnusdon_bot'

# DexScreener API endpoint
DEX_API_URL = 'https://api.dexscreener.com/token-boosts/latest/v1'

# Initialize global variable to store previously notified tokens
previous_tokens = []


# Start command
async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text('Hello! I will notify you about boosted Solana meme coins automatically.')


# Function to fetch boosted tokens from DexScreener
def fetch_boosted_tokens():
    try:
        response = requests.get(DEX_API_URL)
        response.raise_for_status()  # Ensure we raise an error for bad responses
        return response.json()  # Parse the JSON response
    except requests.RequestException as e:
        print(f"Error fetching tokens: {e}")
        return None


# Function to filter and send notifications for new boosted Solana meme coins
async def notify_boosted_tokens(context: ContextTypes.DEFAULT_TYPE):
    global previous_tokens

    data = fetch_boosted_tokens()

    if data:
        solana_meme_coins = [
            token for token in data
            if token.get('chainId') == 'solana' and 'meme' in token.get('description', '').lower()
        ]

        # Check for new tokens that haven't been notified yet
        new_tokens = [token for token in solana_meme_coins if token['tokenAddress'] not in previous_tokens]

        # If there are new Solana meme coins boosted, send alerts
        if new_tokens:
            for coin in new_tokens:
                message = (
                    f"🚀 New Solana Meme Coin Boosted! 🚀\n\n"
                    f"Name: {coin.get('description', 'Unknown')}\n"
                    f"Amount Boosted: {coin.get('amount', 'N/A')}\n"
                    f"Total Boost: {coin.get('totalAmount', 'N/A')}\n"
                    f"More info: {coin.get('url', 'No link available')}"
                )
                # Send message to the Telegram chat
                await context.bot.send_message(chat_id=context.job.chat_id, text=message)

            # Update the list of previously notified tokens
            previous_tokens = [token['tokenAddress'] for token in solana_meme_coins]


# Function to start the automatic notification job
async def start_auto_notifications(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id

    # Set up a job to periodically check for updates (every 1 minutes)
    job_queue: JobQueue = context.job_queue
    job_queue.run_repeating(notify_boosted_tokens, interval=1, first=10, chat_id=chat_id)

    await update.message.reply_text("You will receive automatic notifications on boosted Solana meme coins!")


# Main function to run the bot
def main():
    # Create the application instance
    application = Application.builder().token(TOKEN).build()

    # Register the commands
    application.add_handler(CommandHandler("start", start_command))
    application.add_handler(CommandHandler("auto", start_auto_notifications))

    # Run the bot
    print("Bot is running...")
    application.run_polling()


if __name__ == "__main__":
    main()
