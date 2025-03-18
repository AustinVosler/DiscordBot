import discord
from discord.ext import commands
from discord.ext import pages
import pandas as pd

FILE_PATH = "TestSheet.xlsx"

class Bracket(discord.Cog):
    def __init__(self, bot):
        self.bot = bot

    @discord.slash_command(name="scoreboard", description="Check the March Madness Scoreboard")
    async def scoreboard(self, ctx: discord.ApplicationContext):
        paginator = pages.Paginator(pages = await self.page_maker(5, 4), author_check=False, disable_on_timeout=False)
        await paginator.respond(ctx.interaction, ephemeral=False)

    async def page_maker(self, num_messages, num_pages):
        df = pd.read_excel(FILE_PATH, "Sheet1")

        pages = []
        for i in range(num_pages):
            fields = []
            for j in range(num_messages):
                row = (i * 5) + j
                fields.append(
                    discord.EmbedField(
                        name=f"{df.iloc[row, 0]} - {df.iloc[row, 1]}",
                        value=f"{df.iloc[row, 2]}",
                    )
                )
            embed = discord.Embed(title="March Madness Scoreboard", fields = fields)
            pages.append(embed)

        return pages 