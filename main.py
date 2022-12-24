import discord.errors
from discord.ext import commands
from discord import Intents
import json

# Setup
client = commands.Bot(command_prefix=">", help_command=None, intents=Intents.all())
running = False
task = None
try:
    with open("config.json") as file:
        config = json.load(file)
        TOKEN = config["token"]
        PING_ROLE = config["pingRole"]
        AUTHORIZED_USERS = config["authorizedUsers"]
        if PING_ROLE == "":
            PING_ROLE = "everyone"
except KeyError:
    print("KeyError")
    exit()
except FileNotFoundError:
    print("FileNotFoundError")
    exit()


# Ping bot-ping-channels periodically
async def ping(guild):
    global task
    while True:
        for channel in guild.channels:
            if not running:
                task.cancel()
                task = None
                return
            try:
                if str(channel.type) == "text":
                    if channel.name.startswith("bot-ping-channel"):
                        await channel.send(f"@{PING_ROLE}")
            except discord.errors.Forbidden:
                print("Missing Permissions")
                pass


# Start pinging
@client.command()
async def start(ctx):
    global running
    global task
    # Check if authorized
    if ctx.author.id not in AUTHORIZED_USERS and AUTHORIZED_USERS:
        print("Unauthorized user attempted to use command")
        await ctx.send("You are not authorized to use this command.")
        return
    # Check if already running
    if task:
        print("Bot is already pinging")
        await ctx.send("Bot is already pinging.")
        return
    guild = ctx.message.guild
    running = True
    task = client.loop.create_task(ping(guild))


@client.command()
async def stop(ctx):
    global running
    if not task:
        print("No task running")
        await ctx.send("No task is currently running.")
    running = False


# Create specific number of channels to ping in
@client.command()
async def create_channels(ctx, amount=None):
    # Setup default variables and check if authorized
    if amount is None:
        amount = 1
    if ctx.author.id not in AUTHORIZED_USERS and AUTHORIZED_USERS:
        await ctx.send("You are not authorized to use this command.")
        return
    guild = ctx.message.guild
    channels = [channel.name for channel in guild.channels]
    # Create channels
    try:
        for i in range(1, int(amount)+1):
            if f"bot-ping-channel-{i}" not in channels:
                await guild.create_text_channel(f"bot-ping-channel-{i}")
    except ValueError:
        print("ValueError")
        await ctx.send("Value must be an integer.")
    except discord.errors.Forbidden:
        print("Missing Permissions")
        pass


# Start Bot
if __name__ == "__main__":
    client.run(TOKEN)
