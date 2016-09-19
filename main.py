import logging
import asyncio
import aioredis
import aiohttp
import os
import json
from aiotg import Bot
import re
from tools.downloader import Chapter

with open("config.json") as cfg:
    config = json.load(cfg)

bot = Bot(**config)

logger = logging.getLogger("ReadMangaBot")
redis = None

async def search_manga(text, lang="en"):
    ch = Chapter(text)
    return ch

@bot.default
async def default(chat, message):
    text = "сообщение"
    print(message)
    if re.search(".+manga\.(me|ru).+", message["text"]):
        text = """
                вот тебе пдф, держи!
            """
        pdf = await search_manga(message["text"])
        with open(pdf.pdf, "rb") as f:
            await chat.send_document(f)
    print('типа отправил')
    return chat.reply(text)

async def main():
    global redis
    host = os.environ.get('REDIS_HOST', 'localhost')
    redis = await aioredis.create_redis((host, 6379), encoding="utf-8")
    await bot.loop()

if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)

    loop = asyncio.get_event_loop()
    try:
        loop.run_until_complete(main())
    except KeyboardInterrupt:
        bot.stop()