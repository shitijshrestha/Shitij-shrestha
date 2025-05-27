# uploader.py
import asyncio
import os
from pyrogram import Client
from config import API_ID, API_HASH, SESSION_NAME, STORE_CHANNEL_ID
from utils.utils import split_video

def send_video(file_path, caption, chat_id=None):  # chat_id optional now
    try:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)

        file_size = os.path.getsize(file_path)
        MAX_SIZE = 2 * 1024 * 1024 * 1024  # 2GB

        with Client(SESSION_NAME, api_id=API_ID, api_hash=API_HASH) as app:
            if file_size <= MAX_SIZE:
                msg = app.send_video(chat_id=STORE_CHANNEL_ID, video=file_path, caption=caption)
                if msg and hasattr(msg, "id"):
                    return msg.id
            else:
                print("Video is larger than 2GB, splitting...")
                parts = split_video(file_path)
                msg_ids = []
                for part in parts:
                    msg = app.send_video(chat_id=STORE_CHANNEL_ID, video=part, caption=caption)
                    if msg and hasattr(msg, "id"):
                        msg_ids.append(msg.id)
                return msg_ids[0] if msg_ids else None
    except Exception as e:
        print(f"[ERROR in uploader.py] {str(e)}")
        return None
