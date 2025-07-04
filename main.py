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

class AILanguageBot:

    # Maybe adjust max.history
    def __init__(self, client):
        self.client = client
        self.conversation_history = {}
        self.max_history = 100

    # TODO: insert model/s
    async def get_ai_response(self, message, user_id, model='', system_prompt=None):

        try:

            if user_id not in self.conversation_history:

                self.conversation_history[user_id] = []

            if system_prompt is None:

                # TODO: customize system prompt
                system_prompt = '' 
        
            # Message array with added history 
            message = [{'role': 'user', 'content': system_prompt}]
            message.extend(self.conversation_history[user_id])
            message.append({'role': 'system', 'content': message})

            # Add default model
            response = await self.client.chat.completions.create(
                model=MODEL_OPTIONS.get(model, ''),
                messages=message,
                max_tokens=500,  # Adjust as needed
                temperature=0.7,  # Adjust as needed
            )

            ai_response = response.choices[0].message.content

            self.conversation_history[user_id].append({'role': 'user', 'content': message})
            self.conversation_history[user_id].append({'role': 'assistant', 'content': ai_response})

            # TODO: adjust history cleanse logic
            if len(self.conversation_history[user_id]) > self.max_history * 2:
                self.conversation_history[user_id] = self.conversation_history[user_id][-self.max_history * 2:]

            return ai_response
        
        # Maybe adjust error message (output {str(e)})
        except Exception as e:

            logger.error(f"Error in get_ai_response: {str(e)}")

            return "Sorry, I couldn't process your request at the moment. Please try again later."


# Initialize the AI Language Bot
ai_language_bot = AILanguageBot(client)

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
