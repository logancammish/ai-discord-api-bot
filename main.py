import discord
from discord.ext import commands
import os
from dotenv import load_dotenv
import anthropic
import google.generativeai as genai
from google.generativeai import GenerativeModel

load_dotenv()

GEMINI_TOKEN = os.getenv('GEMINI_TOKEN')  
CLAUDE_TOKEN = os.getenv("ANTHROPIC_API_KEY")
TOKEN = os.getenv('DISCORD_TOKEN')


client = anthropic.Anthropic(
    api_key = CLAUDE_TOKEN,
)
genai.configure(api_key=GEMINI_TOKEN)
gemini_model = GenerativeModel("gemini-2.0-flash")
intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix='!', intents=intents)

@bot.event
async def on_ready():
    """Event triggered when the bot is ready and connected to Discord."""
    print(f'{bot.user.name} has connected to Discord!')
    print(f'Bot is in {len(bot.guilds)} servers')

@bot.command(name='gemini')
async def gemini_command(ctx, *, prompt=None):
    """Interact with Gemini API"""
    if not prompt:
        await ctx.send("Please provide a prompt after !gemini")
        return
    
    async with ctx.typing():
        try:
            response = gemini_model.generate_content(
                prompt
            )
            gemini_response = response.text
            
            if len(gemini_response) <= 2000:
                await ctx.send(gemini_response)
            else:
                for i in range(0, len(gemini_response), 2000):
                    chunk = gemini_response[i:i+2000]
                    await ctx.send(chunk)
        except Exception as error: 
            await ctx.send("Error: " + str(error)) 

@bot.command(name='claude')
async def claude_command(ctx, *, prompt=None):
    """Interact with Claude API"""
    if not prompt:
        await ctx.send("Please provide a prompt after !claude")
        return
    
    async with ctx.typing():
        try:
            response = client.messages.create(
                model="claude-3-7-sonnet-20250219",
                max_tokens=300,
                temperature=1,
                messages=[
                    {"role": "user", "content": prompt}
                ]
            )
            claude_response = response.content[0].text
            
            if len(claude_response) <= 2000:
                await ctx.send(claude_response)
            else:
                for i in range(0, len(claude_response), 2000):
                    chunk = claude_response[i:i+2000]
                    await ctx.send(chunk)
        except Exception as error: 
            await ctx.send("Error" + str(error))

@bot.command(name='ping')
async def ping(ctx):
    """Command that shows the bot's latency."""
    latency = round(bot.latency * 1000)
    await ctx.send(f'Pong! Bot latency is {latency}ms')

@bot.event
async def on_message(message):
    """Event triggered when a message is sent in a channel the bot can see."""
    if message.author == bot.user:
        return

    await bot.process_commands(message)
    
    if 'help me' in message.content.lower():
        await message.channel.send(f'Need help, {message.author.mention}? Use `!hello` or `!ping` to test me out!')

bot.run(TOKEN)