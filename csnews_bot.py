import discord
import feedparser
import requests
import asyncio
import os
from discord.ext import commands, tasks
from googleapiclient.discovery import build
from datetime import datetime

# importing os module for environment variables
import os
# importing necessary functions from dotenv library
from dotenv import load_dotenv, dotenv_values 
# loading variables from .env file
load_dotenv() 

# --------------- CONFIG ------------------
DISCORD_TOKEN = os.getenv("DISCORD_TOKEN")
CHANNEL_ID = int(os.getenv('CHANNEL_ID'))  # replace with your #cs-news channel ID
YOUTUBE_API_KEY = os.getenv('YOUTUBE_API_KEY')
YOUTUBE_CHANNEL_IDS = ['UCsBjURrPoezykLs9EqgamOA']  # Fireship ID, you can add more
RSS_FEEDS = [
    'https://news.ycombinator.com/rss',
    'https://www.theverge.com/rss/index.xml',
]
# -----------------------------------------

intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix='!', intents=intents)

@bot.event
async def on_ready():
    print(f'Logged in as {bot.user}')
    cs_news.start()

@tasks.loop(hours=24)
async def cs_news():
    channel = bot.get_channel(CHANNEL_ID)
    await post_rss_news(channel)
    await asyncio.sleep(3)
    await post_youtube_updates(channel)
    await asyncio.sleep(3)
    await post_newsletter_digest(channel)
    await asyncio.sleep(3)

async def post_rss_news(channel):
    await channel.send("🗞️ **Top Tech Headlines:**")
    for feed_url in RSS_FEEDS:
        feed = feedparser.parse(feed_url)
        for entry in feed.entries[:2]:
            await channel.send(f"**{entry.title}**\n{entry.link}")

async def post_youtube_updates(channel):
    await channel.send("📺 **New Tech Videos:**")
    youtube = build('youtube', 'v3', developerKey=YOUTUBE_API_KEY)
    for channel_id in YOUTUBE_CHANNEL_IDS:
        req = youtube.search().list(part='snippet', channelId=channel_id, order='date', maxResults=1)
        res = req.execute()
        for item in res['items']:
            video_title = item['snippet']['title']
            video_url = f"https://youtube.com/watch?v={item['id']['videoId']}"
            await channel.send(f"**{video_title}**\n{video_url}")

async def post_newsletter_digest(channel):
    await channel.send("📬 **Newsletter Digest (TLDR/Weekly):**\nCheck out [https://www.tldr.tech/newsletters](https://www.tldr.tech/newsletters) or subscribe directly to your inbox!")

bot.run(DISCORD_TOKEN)