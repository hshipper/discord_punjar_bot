'''
A bot to listen to a discord server and keep track of puns that are made
'''

import discord
from discord.ext import commands
from google.cloud import firestore
import json

intents = discord.Intents.default()
intents.members = True
bot = commands.Bot(command_prefix="$", intents=intents)


@bot.event
async def on_ready():
    print(f'{bot.user.name} is connected!')
    await bot.change_presence(activity=discord.Game(name='around with tests'))


class RecordPuns(commands.Cog):
    def __init__(self, bot):
        with open('pun_data.json', 'r') as pun_file:
            self.puns = json.load(pun_file)
        self.bot = bot
        self._last_punmaker = None

    @commands.command()
    async def deposit(self, ctx, *, member: discord.Member = None):
        member = member or ctx.author
        self._last_punmaker = member
        try:
            self.puns[member.id]['count'] += 1
        except KeyError:
            self.puns[member.id] = {'count': 1}
        await ctx.send(f"{member.mention} has made {self.puns[member.id]['count']} \
            awful jokes.")

    @commands.command()
    async def subtract(self, ctx, *, member: discord.Member = None):
        member = member or ctx.author
        try:
            self.puns[member.id]['count'] -= 1
            await ctx.send(f"{member.mention}\'s last joke wasn\'t that bad. They\'ve \
                made {self.puns[member.id]['count']} puns.")
        except KeyError:
            await ctx.send(f'{member.mention} hasn\'t made any bad jokes,\
                 unbelievably.')


bot.add_cog(RecordPuns(bot))


# the bot needs a secret token to connect
# that token is being stored in a separate file for safety purposes


with open(".token_file", "r") as tk:
    token = tk.read()


bot.run(token)
