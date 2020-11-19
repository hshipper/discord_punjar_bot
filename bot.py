'''
A bot to listen to a discord server and keep track of puns that are made
'''

import discord
from discord.ext import commands

# client = discord.Client()


# @client.event
# async def on_ready():
#     print("We have logged in as {0.user}".format(client))


# @client.event
# async def on_message(message):
#     if message.author == client.user:
#         return

#     if message.content.startswith("$hello"):
#         await message.channel.send("Hello!")

intents = discord.Intents.default()
intents.members = True
bot = commands.Bot(command_prefix="$", intents=intents)

@bot.event
async def on_ready():
    print(f'{bot.user.name} is connected!')
    await bot.change_presence(activity=discord.Game(name='around with tests'))

@bot.command()
async def pun(ctx, arg):
    await ctx.send(f'{arg} made a terrible pun.')

@bot.command()
async def members(ctx):
    for user in bot.get_all_members():
        print(user.id)
        await ctx.send(f'{user.name}\'s id is {user.id}')

@bot.command()
async def test(ctx):
    print(len(ctx.guild.roles))

# the bot needs a secret token to connect
# that token is being stored in a separate file for safety purposes
with open(".token_file", "r") as tk:
    token = tk.read()

bot.run(token)
