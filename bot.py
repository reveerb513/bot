import discord
from discord.ext import commands, tasks
import google.generativeai as genai
import asyncio
import datetime
import yt_dlp
import os
import json

# Load bot token and API keys
GEMINI_API_KEY = "AIzaSyDCEnnmQRqGJQqs4sy1rH2eOOaBY221yuo"
genai.configure(api_key=GEMINI_API_KEY)
DISCORD_TOKEN = "MTM0NjczMzAzNjk1NTI0MjYwNg.GfhZ_P.cdzdA4O1op934K57dLSxUyrXxDkU6BHohf_zic"
OPENAI_API_KEY = "YOUR_OPENAI_API_KEY"

#openai.api_key = OPENAI_API_KEY

# Bot setup
intents = discord.Intents.default()
intents.messages = True
intents.guilds = True
intents.message_content = True
bot = commands.Bot(command_prefix="!", intents=intents)

# Reminder storage
reminders = []

# Event: Bot ready
@bot.event
async def on_ready():
    print(f'Logged in as {bot.user}')
    reminder_checker.start()

# AI Chat Command
'''@bot.command()
async def chat(ctx, *, message: str):
    response = openai.ChatCompletion.create(
        model="gpt-4",
        messages=[{"role": "user", "content": message}]
    )
    await ctx.send(response["choices"][0]["message"]["content"])'''

# Reminder Commands
@bot.command()
async def reminder(ctx, time: int, *, task: str):
    reminder_time = datetime.datetime.now() + datetime.timedelta(minutes=time)
    reminders.append({"time": reminder_time, "task": task, "user": ctx.author.id})
    await ctx.send(f'Reminder set for {task} in {time} minutes.')

@tasks.loop(seconds=60)
async def reminder_checker():
    now = datetime.datetime.now()
    for reminder in reminders:
        if reminder["time"] <= now:
            user = bot.get_user(reminder["user"])
            await user.send(f'Reminder: {reminder["task"]}')
            reminders.remove(reminder)

# Poll Command
@bot.command()
async def poll(ctx, question: str, *options):
    if len(options) < 2:
        await ctx.send("You need at least two options for a poll.")
        return
    embed = discord.Embed(title=question, description="\n".join([f'{i+1}: {option}' for i, option in enumerate(options)]), color=0x00ff00)
    poll_msg = await ctx.send(embed=embed)
    for i in range(len(options)):
        await poll_msg.add_reaction(f'{i+1}\N{combining enclosing keycap}')

# Music Player
@bot.command()
async def play(ctx, url: str):
    if ctx.author.voice is None or ctx.author.voice.channel is None:
        await ctx.send("You need to be in a voice channel to play music.")
        return
    voice_channel = ctx.author.voice.channel
    vc = await voice_channel.connect()
    ydl_opts = {'format': 'bestaudio', 'postprocessors': [{'key': 'FFmpegExtractAudio', 'preferredcodec': 'mp3', 'preferredquality': '192'}]}
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(url, download=False)
        url2 = info['url']
        vc.play(discord.FFmpegPCMAudio(url2))



@bot.command()
async def search(ctx, *, query: str):
    """Uses Gemini AI to search the web and provide answers."""
    try:
        model = genai.GenerativeModel("gemini-1.5-flash")  # Faster and works for most users

        response = model.generate_content(f"Search the web and summarize information about: {query}")
        
        # Ensure response is valid
        if response and response.text:
            await ctx.send(f"🔎 **Search Results for:** {query}\n\n{response.text}")
        else:
            await ctx.send("❌ Sorry, I couldn't find relevant information.")
    
    except Exception as e:
        await ctx.send("⚠️ An error occurred while searching.")
        print(f"Error: {e}")

# Welcome Message
@bot.event
async def on_member_join(member):
    channel = discord.utils.get(member.guild.text_channels, name="general")
    if channel:
        await channel.send(f'Welcome {member.mention} to the server!')

bot.run(DISCORD_TOKEN)