"""
A bot to listen to a discord server and keep track of puns that are made
"""

import discord
from discord.ext import commands
from google.cloud import firestore
from firestore_helpers import create_user_documents
from datetime import datetime
import os

os.environ["TZ"] = "US/Western"
intents = discord.Intents.default()
intents.members = True
bot = commands.Bot(command_prefix="$", intents=intents)


@bot.event
async def on_ready():
    print(f"{bot.user.name} is connected!")
    await bot.change_presence(activity=discord.Game(
        name="tracking your bad jokes")
    )


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
        self._last_pun_time = datetime.now()
        punmaker_doc = self.db.collection("puns").document(str(member.id))
        pun_dict = punmaker_doc.get().to_dict()
        pun_count = pun_dict["pun_count"]
        punmaker_doc.update({"pun_count": firestore.Increment(1),
                            "last_pun_at": firestore.SERVER_TIMESTAMP})
        await ctx.send(f"{member.mention} has made {pun_count + 1} "
                       "awful jokes.")

    @commands.command(name="subtract")
    async def subtract(self, ctx, *, member: discord.Member = None):
        member = member or ctx.author
        self._last_punmaker = None
        self._last_pun_time = None
        punmaker_doc = self.db.collection("puns").document(str(member.id))
        pun_count = punmaker_doc.get().to_dict()["pun_count"]
        if pun_count > 0:
            punmaker_doc.update({"pun_count": firestore.Increment(-1),
                                 "last_pun_at": None})
            await ctx.send(
                f"{member.mention}'s last joke wasn't that bad. They've"
                f" made {pun_count - 1} puns."
            )
        else:
            await ctx.send(
                f"{member.mention} hasn't made any bad jokes, unbelievably."
            )

    @commands.command(name="puncount")
    async def count_puns(self, ctx, *, member: discord.Member = None):
        member = member or ctx.author
        punmaker_doc = self.db.collection("puns").document(str(member.id))
        pun_dict = punmaker_doc.get().to_dict()
        pun_count = pun_dict["pun_count"]
        last_pun_time = pun_dict.get("last_pun_at")
        await ctx.send(
            f"{member.mention} has contributed ${pun_count} to the pun jar.\n"
            f"Their last pun was at or on {last_pun_time}"
        )

    @commands.command(name="lastpun")
    async def identify_last_pun(self, ctx, member: discord.Member = None):
        if member:
            punmaker_doc = self.db.collection("puns").document(str(member.id))
            last_pun_time = punmaker_doc.get().to_dict()["last_pun"]
            self._last_pun_time = last_pun_time
            await ctx.send(
                f"{member.mention} last made a pun at "
                f"{last_pun_time.isoformat(sep=' ')}.\n"
            )
        if self._last_punmaker:
            await ctx.send(f"{self._last_punmaker.mention} made the last pun "
                           f"at {self._last_pun_time.isoformat(sep=' ')}.")
        else:
            await ctx.send("I forgot who made the last pun.")


bot.add_cog(RecordPuns(bot))


# the bot needs a secret token to connect
# that token is being stored in a separate file for safety purposes


with open(".token_file", "r") as tk:
    token = tk.read()


bot.run(token)
