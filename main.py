from telebot import TeleBot
from config import BOT_TOKEN
from handlers import register_handlers

bot = TeleBot(BOT_TOKEN)

# Register all handlers
register_handlers(bot)

def run_bot():
    print("Bot is running...")
    bot.infinity_polling()

if __name__ == "__main__":
    run_bot()