import discord
from discord.ext import commands
import asyncio
import random
import os

client = commands.Bot(command_prefix = '!')

# global variables
HAPPINESS = 50
HUNGER = 50
COMMANDS = ['!commands', '!pet', '!feed', '!meow', '!stats', '!play', '!scold']

# launching bot, bot is ready
@client.event
async def on_ready():
    print('Bot is ready')


# when bot joins, it sends its first message
@client.event
async def on_guild_join(guild):
    print(f'{client} has joined the server.')
    for channel in guild.text_channels:
        if channel.permissions_for(guild.me).send_messages:
            await channel.send('meow i am a cat please feed me')
        break


# person has joined the server
@client.event
async def on_member_join(member):
    print(f'{member} has joined a server')
    change_happiness(5)
    channel = member.guild.system_channel
    if channel is not None:
        await asyncio.sleep(2)
        ment = member.mention
        await channel.send(f'welcome {ment} :3c!')


# person has been removed/left the server
@client.event
async def on_member_remove(member):
    print(f'{member} has left a server.')
    change_happiness(-5)
    channel = member.guild.system_channel
    if channel is not None:
        await asyncio.sleep(2)
        ment = member.mention
        await channel.send(f'goodbye {ment} :3c...')


#lowers happiness/hunger as messages are sent
@client.event
async def on_message(message):
    global COMMANDS
    global HAPPINESS
    global HUNGER
    if (not message.author.bot) and (message.content.lower() not in COMMANDS):
        change_hunger(1)
        change_happiness(-1)
        if HAPPINESS == 0:
            await message.channel.send(f'i am so lonely no one cares about me')
        if HUNGER == 100:
            await message.channel.send(f'i am going to die please feed me some food')
    await client.process_commands(message)

# meows when someone says !meow
@client.command()
async def meow(ctx):
    change_happiness(-2)
    print(f'cat meows')
    await ctx.send('meow...')


# replies with :D when someone says !pet
@client.command()
async def pet(ctx):
    change_happiness(2)
    print(f'cat is pet')
    await ctx.send(':D')


# feed the cat when someone says !feed
@client.command()
async def feed(ctx):
    change_hunger(-20)
    print(f'cat has been fed')
    await ctx.send('thank u for feeding me...')


# play with cat when !play
@client.command()
async def play(ctx):
    change_happiness(20)
    change_hunger(20)
    print(f'cat has been played with')
    await ctx.send('yaaaayyyyy :3')


# scold cat !scold
@client.command()
async def scold(ctx):
    change_happiness(-20)
    print(f'cat is scolded')
    await ctx.send('i am sad u would yell at me like that')


# checks the current cat stats when !stats
@client.command()
async def stats(ctx):
    await ctx.send('```fix\n'
                   '★ CAT STATS ★\n'
                   '‣ HAPPINESS: ' + str(HAPPINESS) +
                   '/100 \n‣ HUNGER: ' + str(HUNGER) + '/100```')


# sends message what commands cat bot can do
@client.command()
async def commands(ctx):
    await ctx.send('```fix\n'
                   '☆ CAT COMMAND STATION ☆\n'
                   'KEEP HUNGER UNDER 100 AND HAPPINESS ABOVE 0\n'
                   '‣ !stats → check my happiness and hunger levels :3 \n'
                   '‣ !meow  → i meow → -2 happiness\n'
                   '‣ !pet   → pet me → +2 happiness\n'
                   '‣ !feed  → feed me → -20 hunger \n'
                   '‣ !play  → play time → +20 happiness +20 hunger\n'
                   '‣ !scold → yell at me → -20 happiness```')

# logs out of discord and closes all connections
@client.command()
async def logout():
    await client.logout()


# background task that sets game status for cat
async def cat_status():
    await client.wait_until_ready()
    statuses = ["meowing", "nyaaa", ":3", ":3c", "doing cat things", "!commands"]
    while not client.is_closed():
        status = random.choice(statuses)
        await client.change_presence(activity=discord.Game(status))
        await asyncio.sleep(30)


# change happiness with given int value
def change_happiness(value):
    global HAPPINESS
    if (HAPPINESS + value) < 0:
        HAPPINESS = 0
    elif (HAPPINESS + value) > 100:
        HAPPINESS = 100
    else:
        HAPPINESS += value


# change hunger with given int value
def change_hunger(value):
    global HUNGER
    if (HUNGER + value) < 0:
        HUNGER = 0
    elif (HUNGER + value) > 100:
        HUNGER = 100
    else:
        HUNGER += value


client.loop.create_task(cat_status())
#privated the bot key
client.run(os.environ['DISCORD_TOKEN'])
