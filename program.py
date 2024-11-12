from datetime import datetime
import discord
import os
from dotenv import load_dotenv
import sqlite3
import random
from discord.ext.pages import Paginator, Page
from discord.commands import SlashCommandGroup
from discord.ext import commands, pages

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

def calculate_score():
    return random.randint(1, 100)

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
    
    # print(message.attachments.pop(0))

    res = cur.execute("SELECT name FROM sqlite_master WHERE name LIKE '{}'".format(guild_name))
    if (res.fetchone() == None):
        cur.execute("CREATE TABLE {}(id, user_name, message_id, message, attachments, score)".format(guild_name))

    res = cur.execute("SELECT message_id FROM {} WHERE message_id LIKE '{}'".format(guild_name, message.id))
    if (res.fetchone() == None):
        score = calculate_score()
        if (len(message.attachments) > 0):
            attachment = message.attachments.pop(0)
        else:
            attachment = ""
        cur.execute("INSERT INTO {} VALUES ({},'{}',{},'{}','{}',{})".format(guild_name, user.id, user.name, message.id, message.content, attachment, score))
        con.commit()

    res = cur.execute("SELECT score FROM {} WHERE message_id == {}".format(guild_name, message.id))
    score = res.fetchone()[0]
    await message.reply(f"Analysis... {score} funny points!")

@bot.slash_command(name="hello", description="Say hello to the bot")
async def hello(ctx: discord.ApplicationContext):
    await ctx.respond("Hey!")

async def get_messages(num_messages, guild_name, pages_made):
    res = cur.execute("SELECT id, message, score, attachments FROM {} ORDER BY score DESC LIMIT -1 OFFSET {}".format(guild_name, pages_made*2))

    data = res.fetchmany(num_messages)
    fields = []
    attachments = []
    
    i = 0
    while i < len(data):
        value = ""
        name = await bot.fetch_user(data[i][0])
        if name.global_name != None:
            name = name.global_name

        if data[i][1] == "" and data[i][3] != "":
            value = data[i][3]
        else:
            value = data[i][1]
        fields.append(
            discord.EmbedField(
                name = f"{name} - {data[i][2]} funny points!!",
                value = f"{value}"
            )
        )
        # attachments.append(data[i][3])
        i = i + 1

    return fields, attachments

async def page_maker(guild_name, num_pages, num_messages):
    pages = []
    
    i = 0
    while i < num_pages:
        fields, attachments = await get_messages(num_messages, guild_name, i)
        embed = discord.Embed(title = "Funniest Messages", fields = fields)
        # for pics in attachments:
        #     if pics != "":
        #         embed.image = pics
        pages.append(embed)
        i = i + 1

    discord.ext.pages = pages
    return discord.ext.pages

@bot.slash_command(name="list-messages", description="List the messages that have been analyzed")
async def list_messages(ctx: discord.ApplicationContext):
    # """Demonstrates using the paginator with the default options."""
    guild_name = ctx.guild
    paginator = pages.Paginator(pages = await page_maker((fix_name(str(guild_name))), 3, 5))
    await paginator.respond(ctx.interaction, ephemeral=False)

con = sqlite3.connect("database.db")
cur = con.cursor()

bot.run((os.getenv('token'))) # run the bot with the token

# res = cur.execute("SELECT * FROM Lol")
# print(res.fetchone())