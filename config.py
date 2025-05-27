import os
from dotenv import load_dotenv
   
load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN")
API_ID = int(os.getenv("API_ID"))
API_HASH = os.getenv("API_HASH")
SESSION_STRING = os.getenv("SESSION_STRING")
SESSION_NAME = os.getenv("SESSION_NAME", "session_iptv")
raw_admin_id = os.getenv("ADMIN_ID")
ADMIN_ID = [int(admin_id.strip()) for admin_id in raw_admin_id.split(',')] if raw_admin_id else []
ADMIN_FILE = os.getenv("ADMIN_FILE", "temp_admins.json")
CHANNEL_ID = int(os.getenv("CHANNEL_ID"))
LOG_CHANNEL = int(os.getenv("LOG_CHANNEL"))
STORE_CHANNEL_ID = int(os.getenv("STORE_CHANNEL_ID", "-1002627919828"))
RECORDINGS_DIR = os.getenv("RECORDINGS_DIR", "recordings")
MAX_PART_SIZE = 2 * 1024 * 1024 * 1024