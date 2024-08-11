import os
import requests
import config
import aiohttp
import aiofiles

import yt_dlp
from yt_dlp import YoutubeDL
from pyrogram import Client, filters
from pyrogram.errors import FloodWait
from pyrogram.types import Message, InputTextMessageContent, InlineKeyboardMarkup, InlineKeyboardButton, ReplyKeyboardMarkup
from youtube_search import YoutubeSearch

from ZeMusic import app
from ZeMusic.plugins.play.filters import command

def remove_if_exists(path):
    if os.path.exists(path):
        os.remove(path)

Nem = config.BOT_NAME + " ابحث"
@app.on_message(command(["song","/song", "بحث",Nem]))
async def song_downloader(client, message: Message):
    query = " ".join(message.command[1:])
    m = await message.reply_text("<b>«- جـارِ البحث عـن المقطـع الصـوتـي . . .</b>")
    ydl_ops = {
        'format': 'bestaudio[ext=m4a]',
        'keepvideo': True,
        'prefer_ffmpeg': False,
        'geo_bypass': True,
        'outtmpl': '%(title)s.%(ext)s',
        'quite': True,
        'proxy': '200.174.198.86:8888'
    }
    try:
        results = YoutubeSearch(query, max_results=1).to_dict()
        link = f"https://youtube.com{results[0]['url_suffix']}"
        title = results[0]["title"][:40]
        thumbnail = results[0]["thumbnails"][0]
        thumb_name = f"{title}.jpg"
        thumb = requests.get(thumbnail, allow_redirects=True)
        open(thumb_name, "wb").write(thumb.content)
        duration = results[0]["duration"]

    except Exception as e:
        await m.edit("- لم يتم العثـور على نتائج ؟!\n- حـاول مجـدداً . . .")
        print(str(e))
        return
    await m.edit("<b>⇜ جـارِ التحميل ▬▭ . . .</b>")
    try:
        with yt_dlp.YoutubeDL(ydl_ops) as ydl:
            info_dict = ydl.extract_info(link, download=False)
            audio_file = ydl.prepare_filename(info_dict)
            ydl.process_info(info_dict)
        rep = f"-› @{app.username} "
        host = str(info_dict["uploader"])
        secmul, dur, dur_arr = 1, 0, duration.split(":")
        for i in range(len(dur_arr) - 1, -1, -1):
            dur += int(float(dur_arr[i])) * secmul
            secmul *= 60
        await m.edit("<b>⇜ جـارِ التحميل ▬▬ . . .</b>")
        
        await message.reply_audio(
            audio=audio_file,
            caption=rep,
            title=title,
            performer=host,
            thumb=thumb_name,
            duration=dur,
            reply_markup=InlineKeyboardMarkup(
            [
                [
                    InlineKeyboardButton(
                        text=config.CHANNEL_NAME, url=config.CHANNEL_LINK),
                ],

            ]

        ),
        )
        await m.delete()

    except Exception as e:
        await m.edit(" error, wait for bot owner to fix")
        print(e)

    try:
        remove_if_exists(audio_file)
        remove_if_exists(thumb_name)
    except Exception as e:
        print(e)


@app.on_message(command(["فيديو", "video","تحميل فيديو"]))
async def video_search(client, message):
    ydl_opts = {
        "format": "best",
        "keepvideo": True,
        "prefer_ffmpeg": False,
        "geo_bypass": True,
        "outtmpl": "%(title)s.%(ext)s",
        "quite": True,
    }
    query = " ".join(message.command[1:])
    try:
        results = YoutubeSearch(query, max_results=1).to_dict()
        link = f"https://youtube.com{results[0]['url_suffix']}"
        title = results[0]["title"][:40]
        thumbnail = results[0]["thumbnails"][0]
        # إزالة الأحرف غير الصحيحة من اسم الملف
        title = re.sub(r'[\\/*?:"<>|]', '', title)
        thumb_name = f"thumb{title}.jpg"
        thumb = requests.get(thumbnail, allow_redirects=True)
        with open(thumb_name, "wb") as file:
            file.write(thumb.content)
        results[0]["duration"]
        results[0]["url_suffix"]
        results[0]["views"]
        message.from_user.mention
    except Exception as e:
        print(e)
    try:
        msg = await message.reply("- يتم البحث الان .")
        with yt_dlp.YoutubeDL(ydl_opts) as ytdl:
            ytdl_data = ytdl.extract_info(link, download=True)
            file_name = ytdl.prepare_filename(ytdl_data)
    except Exception as e:
        return await msg.edit(f"🚫 <b>error:</b> {e}")
    thumb_path = f"thumb{title}.jpg"
    if not os.path.exists(thumb_path):
        return await msg.edit(f"🚫 <b>error:</b> Thumb file not found!")
    
    await msg.edit("- تم الرفع انتضر قليلاً .")
    await message.reply_video(
        file_name,
        duration=int(ytdl_data["duration"]),
        thumb=thumb_path,
        caption=ytdl_data["title"],
    )
    try:
        os.remove(file_name)
        os.remove(thumb_path)
        await msg.delete()
    except Exception as ex:
        print(f"- فشل : {ex}")
