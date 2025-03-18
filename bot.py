import os
import discord
from discord.ext import pages
from dotenv import load_dotenv

from cogs.message_score import MessageScore
from cogs.casino import Casino
from cogs.bracket import Bracket

# 
# INITIAL CONFIGS
# 

load_dotenv() # load all the variables from the env file
intents = discord.Intents.default()
intents.message_content = True
bot = discord.Bot(intents=intents)

bot.add_cog(MessageScore(bot))
bot.add_cog(Casino(bot))
bot.add_cog(Bracket(bot))

# 
# BOT SETUP
# 

@bot.event
async def on_ready():
    print(f"{bot.user} is ready and online!")

# bot.run((os.getenv('token'))) # run the bot with the token
