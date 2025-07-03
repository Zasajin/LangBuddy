import discord
from discord.exe import commands
import asyncio
import os
from dotenv import load_dotenv
from openai import AsyncOpenAI
import logging
import json

# Loading environment variables
load_dotenv()

# Logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Bot config
intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix='!', intents=intents)

# OpenRouter config via OpenAI lib
client = AsyncOpenAI(
    api_key=os.getenv('OPENROUTER_API_KEY'),
    base_url='https://openrouter.ai/api/v1',
    default_headers={
        'HTTP_Referer': os.getenv('API_URL', 'http://localhost:3000'),
        'X-Title': 'Discord Language Learning Bot'
    }
)

# TODO: insert LLM Models as per need
MODEL_OPTIONS = {}

@bot.event
async def on_ready():

    # TODO maybe customize
    print(f'{bot.user} hat sich angemeldet!')

@bot.event
async def on_message(message):

    if message.author == bot.user:
        return
    
    if message.content.startswith('!hello'):

        # TODO customize message
        await message.channel.send('Hello! I am you new partner for learning new languages!')

# Keepalive server
async def health_check(request):

    return web.Response(text='Bot is alive!')

async def start_web_server():

    app = web.Application()
    app.router.add_get('/', health_check)
    runner = web.AppRunner(app)
    await runner.setup()
    site = web.TCPSite(runner , '0.0.0.0', int(os.environ.get('PORT', 8080)))
    await site.start()

# Bot start
async def main():

    await start_web_server()
    await bot.start(os.environ['DISCORD_TOKEN'])

if __name__ == '__main__':

    asyncio.run(main())
