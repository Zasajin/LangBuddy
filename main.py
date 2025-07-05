import discord
from discord.ext import commands
import asyncio
import os
from dotenv import load_dotenv
from openai import AsyncOpenAI
import logging
from aiohttp import web
from ai_bot import AILanguageBot

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
MODEL_OPTIONS = {
    'cypher-free': 'openrouter/cypher-alpha:free',
}

# Initialize the AI Language Bot
ai_language_bot = AILanguageBot(client)

@bot.event
async def on_ready():

    # TODO maybe customize
    print(f'{bot.user} hat sich angemeldet!')

@bot.command(name='hello')
async def hello_command(ctx):

    await ctx.send('Hello! I am your AI Language Bot. Enter !cmds to see a list of commands at your disposal.')

@bot.command(name='commands')
async def cmds_command(ctx):

    await ctx.send('Available commands: !hello, !commands, !clear')

@bot.command(name='clear')
async def clear_command(ctx):

    success = await ai_language_bot.clear_history(str(ctx.author.id))

    if success:

        await ctx.send('Your conversation history has been cleared.')

    else:

        await ctx.send('Failed to clear your conversation history. Please try again later.')


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
