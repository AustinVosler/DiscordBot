import os
import random
import sqlite3
from datetime import datetime
from multipledispatch import dispatch

import discord
from discord.ext import pages
from dotenv import load_dotenv

# import analysis

# 
# INITIAL CONFIGS
# 

load_dotenv() # load all the variables from the env file
intents = discord.Intents.default()
intents.message_content = True
bot = discord.Bot(intents=intents)

# analysis.hi()

# 
# HELPER METHODS
# 

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

def calculate_score():
    return random.randint(1, 100)

def fix_message(message):
    i = 0

    for ch in message:
        if (ch == "'"):
            message = message[:i] + "'" + message[i:]
            print(message)
            i = i + 1
        i = i + 1

    return message

# 
# GATHER MESSAGE DATA ON REACTION
# 

@bot.event
async def on_raw_reaction_add(payload):
    if (payload.emoji.name != "🔍"):
        return
    
    message = await bot.get_channel(payload.channel_id).fetch_message(payload.message_id)

    print(message.content)

    message_content = fix_message(message.content)

    guild_name = fix_name(bot.get_channel(payload.channel_id).guild.name)
    user = message.author

    if (user.id == bot.user.id):
        return

    print("id {} name {}".format(user.id, user.name))
    print("Message reacted to: \"{}\" with {} in channel {} in {} at {}\n"
            .format(message_content, payload.emoji.name, 
                    bot.get_channel(payload.channel_id), 
                    bot.get_channel(payload.channel_id).guild.name,
                    datetime.now()))

    res = cur.execute("SELECT name FROM sqlite_master WHERE name LIKE '{}'".format(guild_name))
    if (res.fetchone() is None):
        cur.execute("CREATE TABLE {}(id, user_name, message_id, message, attachments, score)".format(guild_name))

    res = cur.execute("SELECT message_id FROM {} WHERE message_id LIKE '{}'".format(guild_name, message.id))
    if (res.fetchone() is None):
        score = calculate_score()
        if (len(message.attachments) > 0):
            attachment = message.attachments.pop(0)
        else:
            attachment = ""
        cur.execute("INSERT INTO {} VALUES ({},'{}',{},'{}','{}',{})".format(guild_name, user.id, user.name, message.id, message_content, attachment, score))
        con.commit()

    res = cur.execute("SELECT score FROM {} WHERE message_id == {}".format(guild_name, message.id))
    score = res.fetchone()[0]
    await message.reply(f"Analysis... {score} funny points! (requested by {payload.member.mention})")

# 
# PAGINATION FUNCTIONS
# 

async def get_messages(data):    
    fields = []
    i = 0
    while i < len(data):
        value = ""
        name = await bot.fetch_user(data[i][0])
        if name.global_name is not None:
            name = name.global_name

        if data[i][1] == "" and data[i][3] != "":
            value = data[i][3]
        else:
            value = data[i][1]

        # msg = await name.fetch_message(data[i][4])
        # msg_link = msg.jump_url
        # print(msg_link)

        fields.append(
            discord.EmbedField(
                name = f"{name} - {data[i][2]} funny points!!",
                value = f"{value}"
            )
        )
        i = i + 1

    return fields

async def page_maker(guild_name, num_messages, num_pages):
    pages = []
    
    i = 0
    while i < num_pages:
        res = cur.execute("SELECT id, message, score, attachments, message_id FROM {} ORDER BY score DESC LIMIT -1 OFFSET {}".format(guild_name, i * num_messages))
        data = res.fetchmany(num_messages)
        fields = await get_messages(data)
        embed = discord.Embed(title = "Funniest Messages", fields = fields)
        pages.append(embed)
        i = i + 1

    discord.ext.pages = pages
    return discord.ext.pages

async def page_maker_id(guild_name, user_id, num_messages, num_pages):
    pages = []
    name = await bot.fetch_user(user_id)

    if name.global_name is not None:
        name = name.global_name
    
    i = 0
    while i < num_pages:
        res = cur.execute("SELECT id, message, score, attachments, message_id FROM {} WHERE id = {} ORDER BY score DESC LIMIT -1 OFFSET {}".format(guild_name, user_id, i * num_messages))
        data = res.fetchmany(num_messages)
        fields = await get_messages(data)
        embed = discord.Embed(title = f"Funniest Messages by {name}", fields = fields)
        pages.append(embed)
        i = i + 1

    discord.ext.pages = pages
    return discord.ext.pages

# 
# SLASH COMMANDS
# 

@bot.slash_command(name="hello", description="Say hello to the bot")
async def hello(ctx: discord.ApplicationContext):
    await ctx.respond("Hey!")

@bot.slash_command(name="list-messages", description="List the messages that have been analyzed")
async def list_messages(ctx: discord.ApplicationContext):
    guild_name = ctx.guild
    paginator = pages.Paginator(pages = await page_maker((fix_name(str(guild_name))), 5, 3))
    await paginator.respond(ctx.interaction, ephemeral=False)

@bot.slash_command(name="list-messages-personal", description="List the messages (sent by you!) that have been analyzed")
async def list_messages_personal(ctx: discord.ApplicationContext):
    guild_name = ctx.guild
    user_id = ctx.author.id
    paginator = pages.Paginator(pages = await page_maker_id((fix_name(str(guild_name))), user_id, 5, 3))
    await paginator.respond(ctx.interaction, ephemeral=False)

# 
# BOT SETUP
# 

@bot.event
async def on_ready():
    print(f"{bot.user} is ready and online!")

con = sqlite3.connect("database.db")
cur = con.cursor()

bot.run((os.getenv('token'))) # run the bot with the token