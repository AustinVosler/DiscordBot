import sqlite3
import discord
from discord.ext import commands

class Casino(discord.Cog):
    def __init__(self, bot):
        self.bot = bot
        # self.con = sqlite3.connect("message_score.db")
        # self.cur = self.con.cursor()

    @discord.slash_command(name="roulette", description="Play roulette")
    async def roulette(self, ctx: discord.ApplicationContext):
        embed = discord.Embed(title="Click to Spin the Wheel!", description="🎡 Click below to try your luck!", color=0x00ff00)
        embed.url = "https://www.austinvosler.dev/tools/coinflip"
        await ctx.send(embed=embed)
