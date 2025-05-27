import os
import json
import shlex
from datetime import datetime, timedelta
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton
from recorder import start_recording  # Import from recorder.py
from utils.admin_checker import is_temp_admin
from config import ADMIN_ID, ADMIN_FILE

def register_handlers(bot):
    @bot.message_handler(commands=["start"])
    def start_handler(message):
        user = message.from_user
        chat_id = message.chat.id

        keyboard = InlineKeyboardMarkup()
        keyboard.row(
            InlineKeyboardButton("Help / Contact Developer", url="https://t.me/Requestadminuser_bot")
        )
        keyboard.row(
            InlineKeyboardButton("Request Admin Access", callback_data="request_admin")
        )

        with open("assets/welcome.jpg", "rb") as photo:
            bot.send_photo(
                chat_id,
                photo,
                caption=f"**Welcome {user.first_name}**\n\nThis bot helps you record IPTV with ease.",
                parse_mode="Markdown",
                reply_markup=keyboard
            )

    @bot.callback_query_handler(func=lambda call: call.data == "request_admin")
    def handle_admin_request(call):
        user = call.from_user
        msg = (
            f"⚠️ *Admin Access Requested*\n\n"
            f"👤 Name: `{user.first_name}`\n"
            f"🆔 User ID: `{user.id}`\n"
        )
        if user.username:
            msg += f"🔗 Username: @{user.username}"

        bot.send_message(ADMIN_ID, msg, parse_mode="Markdown")
        bot.answer_callback_query(call.id, "Request sent to admin!")

    @bot.message_handler(commands=['help'])
    def help_handler(message):
        if message.from_user.id not in ADMIN_ID and not is_temp_admin(message.from_user.id):
            return bot.reply_to(message, "⚠️ Unauthorized access.")

        markup = InlineKeyboardMarkup()
        markup.add(InlineKeyboardButton(text="Bot Status: ✅ Online", callback_data="status"))

        help_text = (
            "**Welcome to IPTV Recorder Bot!**\n\n"
            "To schedule a recording, use the format below:\n"
            "`/record \"stream_url\" duration channel_name title`\n\n"
            "_Example:_\n"
            "`/record \"http://test.m3u8\" 00:10:00 SonyYay \"Test Title\"`\n\n"
            "_Only admins can use this bot._"
        )

        bot.send_message(message.chat.id, help_text, parse_mode="Markdown", reply_markup=markup)

    @bot.message_handler(commands=['record'])
    def record_handler(message):
        if message.from_user.id not in ADMIN_ID and not is_temp_admin(message.from_user.id):
            return bot.reply_to(message, "⚠️ Unauthorized access.")

        try:
            parts = shlex.split(message.text)
            if len(parts) < 4:
                return bot.reply_to(message,
                    "❗ *Invalid Format!*\n\n"
                    "Use this format:\n"
                    "`/record \"url\" duration channel title`\n\n"
                    "Example:\n"
                    "`/record \"http://test.m3u8\" 00:10:00 SonyYay \"Test Title\"`",
                    parse_mode="Markdown"
                )

            url = parts[1].strip('"')
            duration = parts[2]
            channel = parts[3]
            title = " ".join(parts[4:]) if len(parts) > 4 else "Untitled"
            chat_id = message.chat.id

            
            

            bot.reply_to(
                message,
                f"**Recording Started!**\n\n"
                f"📹 **Title:** `{title}`\n"
                f"📺 **Channel:** `{channel}`\n"
                f"⏱️ **Duration:** `{duration}`\n"
                f"🔗 **URL:** `{url}`",
                parse_mode="Markdown"
            )
            
            # Start the recording immediately
            start_recording(url, duration, channel, title, chat_id)

        except Exception as e:
            bot.reply_to(message, f"❌ Error: `{str(e)}`", parse_mode="Markdown")

    @bot.message_handler(commands=['addadmin'])
    def add_temp_admin(message):
        if message.from_user.id not in ADMIN_ID:
            return bot.reply_to(message, "⚠️ Unauthorized.")

        parts = message.text.split()
        if len(parts) != 3:
            return bot.reply_to(message, "Usage: /addadmin user_id HH:MM:SS")

        try:
            user_id = str(parts[1])
            hours, minutes, seconds = map(int, parts[2].split(":"))
            expiry_time = datetime.now() + timedelta(hours=hours, minutes=minutes, seconds=seconds)
            expiry_str = expiry_time.strftime("%Y-%m-%d %H:%M:%S")

            admins = {}
            if os.path.exists(ADMIN_FILE):
                with open(ADMIN_FILE, "r") as f:
                    admins = json.load(f)

            admins[user_id] = expiry_str

            with open(ADMIN_FILE, "w") as f:
                json.dump(admins, f)

            bot.reply_to(message, f"✅ Temporary admin `{user_id}` added till `{expiry_str}`", parse_mode="Markdown")

        except Exception as e:
            bot.reply_to(message, f"❌ Error: {str(e)}")
