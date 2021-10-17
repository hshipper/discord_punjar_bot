"""
A bot to listen to a discord server and keep track of puns that are made
"""

import discord
from discord.ext import tasks, commands
from discord.ext.commands.errors import MissingRequiredArgument
from google.cloud import firestore
from firestore_helpers import create_user_documents
from datetime import datetime
import os
import logging
import logging.handlers

# log info, errors, warnings
logger = logging.getLogger("discord_punjar_bot")
logger.setLevel(logging.INFO)
rh = logging.handlers.RotatingFileHandler(
    filename="punjar_logs", backupCount=1, maxBytes=1000000
)
formatter = logging.Formatter("%(asctime)s | %(name)s | %(levelname)s | %(message)s")
rh.setFormatter(formatter)
logger.addHandler(rh)

os.environ["TZ"] = "US/Western"
intents = discord.Intents.default()
intents.members = True
bot = commands.Bot(command_prefix="$", intents=intents)

class TurnOnBot(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.db = firestore.Client()

    @commands.Cog.listener("on_ready")
    async def initialize_bot(self):
        READY_MESSAGE = f"{bot.user.name} is connected!"
        print(READY_MESSAGE)
        logger.info(READY_MESSAGE)
        await bot.change_presence(activity=discord.Game(name="tracking your bad jokes"))
    
    @tasks.loop(hours=24)
    async def setup_firestore(self):
        create_user_documents(self)

    @setup_firestore.before_loop
    async def before_setup_firestore(self):
        print('Waiting for bot to be ready')
        await self.bot.wait_until_ready()


class RecordPuns(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self._last_punmaker = None
        self._last_pun_time = None
        self.db = firestore.Client()

    @commands.command(name="deposit")
    async def deposit(self, ctx, *, member: discord.Member = None):
        member = member or ctx.author
        self._last_punmaker = member
        self._last_pun_time = datetime.now()
        punmaker_doc = self.db.collection("puns").document(str(member.id))
        pun_dict = punmaker_doc.get().to_dict()
        pun_count = pun_dict.get(["pun_count"], 0)
        punmaker_doc.update(
            {
                "pun_count": firestore.Increment(1),
                "last_pun_at": firestore.SERVER_TIMESTAMP,
            }
        )
        await ctx.send(f"{member.mention} has put ${pun_count + 1} in the jar.")
        logger.info(f"{member.name} made a deposit")

    @commands.command(name="multideposit")
    async def multideposit(self, ctx, member: discord.Member, qty: int):
        punmaker_doc = self.db.collection("puns").document(str(member.id))
        pun_dict = punmaker_doc.get().to_dict()
        pun_count = pun_dict.get(["pun_count"], 0)
        punmaker_doc.update(
            {
                "pun_count": firestore.Increment(qty),
                "last_pun_at": firestore.SERVER_TIMESTAMP,
            }
        )
        await ctx.send(
            f"{member.mention} put {qty} in the jar, bringing their total to {pun_count + qty}."
        )
        logger.info(f"{member} made a deposit")

    @multideposit.error
    async def multideposit_error(self, ctx, error):
        if isinstance(error, commands.MissingRequiredArgument):
            logger.info("multidepost_error missingrequiredargument")
            await ctx.send("Either a user wasn't tagged or a quantity was missing.")
        if isinstance(error, commands.BadArgument):
            logger.info("multidepost_error badargument")
            await ctx.send("Either a user was mis-specifed or a number was missing")

    @commands.command(name="subtract")
    async def subtract(self, ctx, *, member: discord.Member = None):
        member = member or ctx.author
        self._last_punmaker = None
        self._last_pun_time = None
        punmaker_doc = self.db.collection("puns").document(str(member.id))
        pun_count = punmaker_doc.get().to_dict()["pun_count"]
        if pun_count > 0:
            punmaker_doc.update(
                {"pun_count": firestore.Increment(-1), "last_pun_at": None}
            )
            await ctx.send(
                f"{member.mention} took a pun from the jar. They have ${pun_count - 1} in the jar."
            )
            logger.info(f"{member} took a pun from the jar")
        else:
            await ctx.send(f"{member.mention} hasn't made any bad jokes, unbelievably.")
            logger.info(
                f"{member.mention.name} tried to have a pun removed but had none to remove."
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
            f"Their last pun was {last_pun_time.strftime('%a, %B %d, %Y at %I:%M:%S %p')}"
        )
        logger.info(f"{member.mention.name}'s pun total was checked")

    @commands.command(name="lastpun")
    async def identify_last_pun(self, ctx, *, member: discord.Member = None):
        if member:
            punmaker_doc = self.db.collection("puns").document(str(member.id))
            last_pun_time = punmaker_doc.get().to_dict()["last_pun_at"]
            await ctx.send(
                f"{member.mention} last made a pun "
                f"{last_pun_time.strftime('%a, %B %d, %Y at %I:%M:%S %p')}.\n"
            )
            logger.info("The most recent deposit was shared")
        elif self._last_punmaker:
            await ctx.send(
                f"{self._last_punmaker.mention} made the last pun "
                f"{self._last_pun_time.strftime('%a, %B %d, %Y at %I:%M:%S %p')}."
            )
        else:
            await ctx.send("I forgot who made the last pun.")
            logger.info("The last deposit couldn't be found")

bot.add_cog(TurnOnBot(bot))
bot.add_cog(RecordPuns(bot))


# the bot needs a secret token to connect
# that token is being stored in a separate file for safety purposes


with open(".token_file", "r") as tk:
    token = tk.read()


bot.run(token)
