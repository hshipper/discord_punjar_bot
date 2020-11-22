"""
A bot to listen to a discord server and keep track of puns that are made
"""

import discord
from discord.ext import commands
from google.cloud import firestore
from firestore_helpers import create_user_documents
import os

os.environ["TZ"] = "US/Western"
intents = discord.Intents.default()
intents.members = True
bot = commands.Bot(command_prefix="$", intents=intents)


@bot.event
async def on_ready():
    print(f"{bot.user.name} is connected!")
    await bot.change_presence(activity=discord.Game(name="tracking your bad jokes"))


class RecordPuns(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self._last_punmaker = None
        self._last_pun_time = None
        self.db = firestore.Client()

    @commands.Cog.listener()
    async def on_ready(self):
        create_user_documents(self)

    @commands.command(name="deposit")
    async def deposit(self, ctx, *, member: discord.Member = None):
        member = member or ctx.author
        self._last_punmaker = member
        punmaker_data = self.db.collection("puns").document(str(member.id))
        pun_count = punmaker_data.get().to_dict()["pun_count"]
        punmaker_data.update({"pun_count": firestore.Increment(1)})
        await ctx.send(f"{member.mention} has made {pun_count + 1} " "awful jokes.")

    @commands.command(name="subtract")
    async def subtract(self, ctx, *, member: discord.Member = None):
        member = member or ctx.author
        punmaker_data = self.db.collection("puns").document(str(member.id))
        pun_count = punmaker_data.get().to_dict()["pun_count"]
        if pun_count > 0:
            punmaker_data.update({"pun_count": firestore.Increment(-1)})
            await ctx.send(
                f"{member.mention}'s last joke wasn't that bad. They've"
                f"made {pun_count - 1} puns."
            )
        else:
            await ctx.send(
                f"{member.mention} hasn't made any bad jokes," "unbelievably."
            )

    @commands.command(name="puncount")
    async def count_puns(self, ctx, *, member: discord.Member = None):
        member = member or ctx.author
        punmaker_data = self.db.collection("puns").document(str(member.id))
        pun_count = punmaker_data.get().to_dict()["pun_count"]
        await ctx.send(
            f"{member.mention} has contributed ${pun_count}" " to the pun jar."
        )

    @commands.command(name="lastpun")
    async def identify_last_pun(self, ctx, member: discord.Member = None):
        if member:
            punmaker_data = self.db.collection("puns").document(str(member.id))
            last_pun_time = punmaker_data.get().to_dict()["last_pun"]
            await ctx.send(
                f"{member.mention} last made a pun at "
                f"{last_pun_time.isoformat(sep=' ')}"
            )
        if self._last_punmaker:
            await ctx.send(f"{self._last_punmaker.mention} made the last pun")
        else:
            await ctx.send("I forgot who made the last pun.")


bot.add_cog(RecordPuns(bot))


# the bot needs a secret token to connect
# that token is being stored in a separate file for safety purposes


with open(".token_file", "r") as tk:
    token = tk.read()


bot.run(token)
