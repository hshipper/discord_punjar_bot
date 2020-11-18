import discord

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


with open(".token_file", "r") as tk:
    token = tk.read()

client.run(token)
