import discord
from discord.ext import commands, tasks
import asyncio
from datetime import datetime
import pytz
from dotenv import load_dotenv
import os

load_dotenv('environment/var.env')

intents = discord.Intents.default()
intents.members = True
intents.voice_states = True

bot = commands.Bot(command_prefix='!', intents=intents)
VOICE_CHANNEL_NAME = os.getenv('VOICE_CHANNEL_NAME')

@bot.event
async def on_ready():
    print(f'Logged in as {bot.user}')
    if len(bot.guilds) == 0:
        print("The bot is not a member of any servers.")
        return

    print(f"Connected to server: {bot.guilds[0].name} - Targeting VC-{VOICE_CHANNEL_NAME}")
    hourly_bong.start()
    print("Hourly bong task started.")

@tasks.loop(minutes=1)
async def hourly_bong():
    timezone_str = os.getenv('TIMEZONE', 'Europe/London')
    try:
        timezone = pytz.timezone(timezone_str)
    except pytz.UnknownTimeZoneError:
        print(f"Unknown timezone: {timezone_str}. Defaulting to 'Europe/London'.")
        timezone = pytz.timezone('Europe/London')

    now = datetime.now(timezone)

    if now.minute == 0:
        print(f"Time is {now.strftime('%H:%M')} - on the hour! Preparing to bong...")
    
        current_hour = now.hour % 12 or 12
        print(f"Current hour: {now.hour} (12-hour format: {current_hour}). Playing {current_hour} bongs.")

        guild = bot.guilds[0]
        voice_channel = discord.utils.get(guild.voice_channels, name=VOICE_CHANNEL_NAME)

        if not voice_channel:
            print(f"Voice channel '{VOICE_CHANNEL_NAME}' not found.")
            return

        non_bot_members = [member for member in voice_channel.members if not member.bot]
        if len(non_bot_members) == 0:
            print(f"No members in the voice channel '{voice_channel.name}'. Skipping bong.")
            return

        if not bot.voice_clients:
            try:
                vc = await voice_channel.connect()
                print(f"Connected to the voice channel: {voice_channel.name}")
                for count in range(current_hour):
                    print(f"Playing bong {count + 1} of {current_hour}...")
                    vc.play(discord.FFmpegPCMAudio(os.getenv('WAV_PATH')))
                    while vc.is_playing():
                        await asyncio.sleep(0.1)

                print("All bongs played. Disconnecting...")
                await vc.disconnect()
                print("Disconnected from the voice channel.")
                
            except Exception as e:
                print(f"Error while connecting or playing audio: {e}")
        else:
            print("Bot is already connected to a voice channel.")

token = os.getenv("DISCORD_TOKEN")
print(f"Token: {token}")
bot.run(token)
