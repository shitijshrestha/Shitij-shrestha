from pyrogram import Client, errors

API_ID = '21166002'
API_HASH = 'b9ef6d3610ad089bc79fb0dd38b1cdb8'
SESSION_NAME = 'session_iptv'
VIDEO_PATH = 'test.Disney.Quality.08:50:44-08:50:49.19-05-2025.IPTV.WEB-DL.dfmdubber.mkv'

app = Client(SESSION_NAME, api_id=API_ID, api_hash=API_HASH)

def upload_video():
    try:
        with app:
            app.send_video(chat_id='-1002323987687', video=VIDEO_PATH)
            print("Video uploaded successfully!")
    except errors.BadRequest as e:
        print("Bad request:", e)
    except errors.FloodWait as e:
        print("Too many requests, please wait:", e.x)
    except Exception as e:
        print("An unexpected error occurred:", e)

if __name__ == "__main__":
    upload_video()