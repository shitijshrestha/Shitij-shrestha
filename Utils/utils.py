# utils.py

import os
import subprocess
from datetime import timedelta

def format_bytes(size):
    # Convert bytes to MB/GB etc.
    for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
        if size < 1024.0:
            return f"{size:.2f} {unit}"
        size /= 1024.0

def format_duration(duration_str):
    h, m, s = map(int, duration_str.split(":"))
    total = timedelta(hours=h, minutes=m, seconds=s)
    hours, remainder = divmod(total.total_seconds(), 3600)
    minutes, seconds = divmod(remainder, 60)
    return f"{int(hours)}hr, {int(minutes)}min, {int(seconds)}sec"

def split_video(file_path):
    size = os.path.getsize(file_path)
    max_size = 2 * 1024 * 1024 * 1024  # 2GB
    parts = []
    base_name = os.path.splitext(file_path)[0]

    duration_cmd = [
        "ffprobe", "-v", "error", "-show_entries",
        "format=duration", "-of",
        "default=noprint_wrappers=1:nokey=1", file_path
    ]
    result = subprocess.run(duration_cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    total_duration = float(result.stdout.decode().strip())

    # How many parts?
    num_parts = int(size / max_size) + 1
    part_duration = total_duration / num_parts

    for i in range(num_parts):
        start = i * part_duration
        out_file = f"{base_name}_part{i+1}.mp4"
        cmd = [
            "ffmpeg", "-i", file_path, "-ss", str(int(start)), "-t",
            str(int(part_duration)), "-c", "copy", out_file
        ]
        subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        parts.append(out_file)

    return parts