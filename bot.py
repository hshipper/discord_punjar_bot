'''
A bot to listen to a discord server and keep track of puns that are made
'''

import discord
from discord.ext import commands

client = discord.Client()


@client.event
async def on_read():
    print("We have logged in as {0.user}".format(client))


@client.event
async def on_message(message):
    if message.author == client.user:
        return

    if message.content.startswith("$hello"):
        await message.channel.send("Hello!")

bot = commands.Bot(command_prefix="!")

@bot.command()
async def print_user(ctx):
    await ctx.send(ctx.author.name)

bot.add_command(print_user)

# the bot needs a secret token to connect
# that token is being stored in a separate file for safety purposes
with open(".token_file", "r") as tk:
    token = tk.read()

client.run(token)
