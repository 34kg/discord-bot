# This example requires the 'message_content' intent.

import discord
import os
from dotenv import load_dotenv

intents = discord.Intents.default()
intents.message_content = True

load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')
client = discord.Client(intents=intents)

@client.event
async def on_ready():
    print(f'We have logged in as {client.user}')

@client.event
async def on_message(message):
    if message.author == client.user:
        return

    if message.content.startswith('/dou'):
        await message.channel.send('今日みんな予定 dou?')

    if message.content.startswith('$hello'):
        await message.channel.send('Hello!')

# Run Discord Bot
client.run(TOKEN)
