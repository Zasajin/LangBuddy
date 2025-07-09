import discord
from discord.ext import commands
import asyncio
import os
from dotenv import load_dotenv
from openai import AsyncOpenAI
import logging
from aiohttp import web
from ai_bot import AILanguageBot
import db

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

MODEL_OPTIONS = {

    # Core learning features
    'translate': 'qwen/qwen3-8b',
    'grammar': 'deepseek/deepseek-r1-0528-qwen3-8b',
    'vocabulary': 'qwen/qwen3-8b',
    'mediation': 'mistralai/mistral-small-3.2-24b',

    # Interactive features
    'conversation': 'mistralai/mistral-small-3.2-24b',
    'assessment': 'deepseek/deepseek-r1-0528-qwen3-8b',
    'progress_analysis': 'deepseek/deepseek-r1-0528-qwen3-8b',

    # Special features
    'etymologie': 'qwen/qwen3-8b',
    'free_chat': 'qwen/qwen3-8b',
    #'cultural_context': 'mistralai/mistral-small-3.2-24b',
    # To avoid unneccessary model swapping mid learning, this might as well just be part of conversation
    # where mistral is used anyways

    # Fallback
    'general': 'qwen/qwen3-8b',
}

# Initialize the AI Language Bot
ai_language_bot = AILanguageBot(client, MODEL_OPTIONS)


@bot.event
async def on_ready():

    # TODO maybe customize
    print(f'{bot.user} hat sich angemeldet!')


@bot.command(name='hello')
async def hello_command(ctx):

    await ai_language_bot.first_contact(ctx)


@bot.command(name='commands')
async def cmds_command(ctx):

    await ctx.send('Available commands: !hello, !commands, !clear')


@bot.command(name='clear')
async def clear_command(ctx):

    success = await ai_language_bot.reset_conversation(str(ctx.author.id))

    if success:

        await ctx.send('Your conversation history has been reset.')

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

    await db.init_db_pool()
    await start_web_server()
    await bot.start(os.environ['DISCORD_TOKEN'])


if __name__ == '__main__':

    asyncio.run(main())
