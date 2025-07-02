import discord
import asyncio
import aiohttp
from aiohttp import web
import os

# 
intents = discord.Intents.default()
intents.message_content = True
bot = discord.Client(intents=intents)

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
