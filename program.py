from datetime import datetime
import discord
import os
from dotenv import load_dotenv
import sqlite3
import random

load_dotenv() # load all the variables from the env file

intents = discord.Intents.default()
intents.message_content = True
bot = discord.Bot(intents=intents)

def fix_name(name):
    new_name = ""
    for char in name:
        if (char == '\''):
            continue
        if (char.isspace()):
            new_name += '_'
            continue
        new_name += char
            
    return new_name

@bot.event
async def on_ready():
    print(f"{bot.user} is ready and online!")

@bot.event
async def on_raw_reaction_add(payload):
    if (payload.emoji.name != "🔍"):
        return
    
    message = await bot.get_channel(payload.channel_id).fetch_message(payload.message_id)

    guild_name = fix_name(bot.get_channel(payload.channel_id).guild.name)
    user = message.author

    print("id {} name {}".format(user.id, user.name))
    print("Message reacted to: \"{}\" with {} in channel {} in {} at {}\n"
            .format(message.content, payload.emoji.name, 
                    bot.get_channel(payload.channel_id), 
                    bot.get_channel(payload.channel_id).guild.name,
                    datetime.now()))

    
    res = cur.execute("SELECT name FROM sqlite_master WHERE name LIKE '{}'".format(guild_name))
    if (res.fetchone() == None):
        cur.execute("CREATE TABLE {}(id, user_name, message_id, message, score)".format(guild_name))

    res = cur.execute("SELECT message_id FROM {} WHERE message_id LIKE '{}'".format(guild_name, message.id))
    if (res.fetchone() == None):
        cur.execute("INSERT INTO {} VALUES ({},'{}',{},'{}',{})".format(guild_name, user.id, user.name, message.id, message.content, random.randint(1, 100)))
        con.commit()

@bot.slash_command(name="hello", description="Say hello to the bot")
async def hello(ctx: discord.ApplicationContext):
    await ctx.respond("Hey!")

con = sqlite3.connect("database.db")
cur = con.cursor()

bot.run((os.getenv('token'))) # run the bot with the token

def print_all_messages(table_name):
    for row in cur.execute("SELECT * FROM {}".format(table_name)):
        print(row)