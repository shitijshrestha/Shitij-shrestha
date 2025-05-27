import os
import subprocess
import re
from datetime import datetime, timedelta
from pytz import timezone
import requests
import telebot

from config import RECORDINGS_DIR, BOT_TOKEN, STORE_CHANNEL_ID
from utils.utils import format_bytes, format_duration
from uploader import send_video

bot = telebot.TeleBot(BOT_TOKEN)

def resolve_stream(url):
    try:
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/120.0.0.0 Safari/537.36",
            "Referer": "https://imranapk.site/"
        }
        response = requests.get(url, headers=headers, timeout=10, allow_redirects=True)
        return response.url if response.ok else url
    except Exception as e:
        print(f"[Stream Resolver] Error resolving URL: {e}")
        return url

def parse_ffmpeg_time(time_str):
    try:
        parts = time_str.split(":")
        secs = float(parts[2])
        return int(parts[0]) * 3600 + int(parts[1]) * 60 + secs
    except Exception:
        return 0

def start_recording(url, duration, channel, title, chat_id):
    try:
        ist = timezone("Asia/Kolkata")
        now = datetime.now(ist)

        try:
            h, m, s = map(int, duration.split(":"))
        except ValueError:
            bot.send_message(chat_id, "Invalid duration format. Use HH:MM:SS.")
            return

        total_seconds = h * 3600 + m * 60 + s
        end_time = now + timedelta(seconds=total_seconds)

        start_time_str = now.strftime("%H-%M-%S")
        end_time_str = end_time.strftime("%H-%M-%S")
        date_str = now.strftime("%d-%m-%Y")

        filename = f"{title}.{channel}.Quality.{start_time_str}-{end_time_str}.{date_str}.IPTV.WEB-DL.dfmdubber.mkv"
        output_path = os.path.join(RECORDINGS_DIR, filename)
        os.makedirs(RECORDINGS_DIR, exist_ok=True)

        print(f"[Recorder] Recording started: {filename}")
        stream_url = resolve_stream(url)

        cmd = [
            "ffmpeg",
            "-y",
            "-headers", "User-Agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/120.0.0.0 Safari/537.36\r\nReferer: https://imranapk.site/",
            "-i", stream_url,
            "-t", duration,
            "-map", "0:v?",
            "-map", "0:a?",
            "-map", "0:s?",
            "-c", "copy",
            output_path
        ]

        progress_msg = bot.send_message(chat_id, "⏺️ Recording started...\nProgress: 0%")
        process = subprocess.Popen(cmd, stderr=subprocess.PIPE, universal_newlines=True)

        last_percent = 0
        time_pattern = re.compile(r'time=(\d{2}:\d{2}:\d{2}\.\d{2})')

        while True:
            line = process.stderr.readline()
            if line == '' and process.poll() is not None:
                break
            if line:
                match = time_pattern.search(line)
                if match:
                    current_time = parse_ffmpeg_time(match.group(1))
                    percent = int((current_time / total_seconds) * 100)
                    if percent > last_percent and percent <= 100:
                        last_percent = percent
                        try:
                            bot.edit_message_text(
                                chat_id=chat_id,
                                message_id=progress_msg.message_id,
                                text=f"⏺️ Recording in progress...\nProgress: {percent}%"
                            )
                        except Exception:
                            pass

        process.wait()
        if process.returncode != 0:
            bot.send_message(chat_id, "❌ Recording failed due to FFmpeg error.")
            return

        # Generate thumbnail
        thumb_path = output_path.replace(".mkv", "_thumb.jpg")

        def generate_thumb(time_str):
            cmd_thumb = [
                "ffmpeg", "-y", "-i", output_path,
                "-ss", time_str, "-vframes", "1",
                "-vf", "scale=320:-1",
                thumb_path
            ]
            subprocess.run(cmd_thumb, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

        generate_thumb("00:00:20.000")
        if not os.path.exists(thumb_path) or os.path.getsize(thumb_path) == 0:
            generate_thumb("00:00:10.000")
        if not os.path.exists(thumb_path) or os.path.getsize(thumb_path) == 0:
            thumb_path = None

        size = os.path.getsize(output_path)
        readable_size = format_bytes(size)
        readable_duration = format_duration(duration)

        caption = f"""🎥 Recording Completed!

Filename: {filename}
Duration: {readable_duration}
File-Size: {readable_size}
Progress: ██████████ 100%
Time Left: 00:00:00 / {readable_duration}
"""

        bot.edit_message_text(chat_id=chat_id, message_id=progress_msg.message_id, text="✅ Recording completed.\nUploading...")
        message_id = send_video(output_path, caption, thumb_path)

        if message_id:
            bot.copy_message(chat_id=chat_id, from_chat_id=STORE_CHANNEL_ID, message_id=message_id)
            bot.send_message(chat_id, "✅ Uploaded successfully.")
        else:
            bot.send_message(chat_id, "❌ Video upload failed.")

        # Cleanup
        for f in [output_path, thumb_path]:
            if f and os.path.exists(f):
                os.remove(f)
                print(f"[Recorder] Deleted: {f}")

    except Exception as e:
        print(f"[ERROR in recorder.py] {str(e)}")
        bot.send_message(chat_id, f"Recording error: {e}")
