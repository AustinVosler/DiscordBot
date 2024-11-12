import discord
import os # default module
from dotenv import load_dotenv
import sqlite3

from pkg_resources import safe_name

load_dotenv() # load all the variables from the env file
bot = discord.Bot()

@bot.event
async def on_ready():
    print(f"{bot.user} is ready and online!")

@bot.slash_command(name="hello", description="Say hello to the bot")
async def hello(ctx: discord.ApplicationContext):
    await ctx.respond("Hey!")

# bot.run(str(os.getenv('token'))) # run the bot with the token

con = sqlite3.connect("messages.db")

cur = con.cursor()

def print_all_messages(table_name):
    for row in cur.execute("SELECT * FROM {}".format(table_name)):
        print(row)
    

print("All data entries:")
print_all_messages("Sample_Messages")

print("\nSorted by score:")
for row in cur.execute("SELECT name, score FROM Sample_Messages ORDER BY score DESC"):
    print(row)

# print(f"")