import ssl

import discord
from discord.ext import commands
from pymongo import MongoClient
import asyncio
import random
import os
from dotenv import load_dotenv

client = commands.Bot(command_prefix='!')
HAPPINESS = 50
HUNGER = 50
COMMANDS = ['!commands', '!pet', '!feed', '!meow', '!stats', '!play', '!scold', '!join', '!abandon']
load_dotenv()
db_password = os.environ['DB_PASSWORD']
cluster = MongoClient(f'mongodb+srv://aby:{db_password}@abycluster.zscon.mongodb.net/test?authSource=admin&replicaSet=atlas-572'
                      f'jpr-shard-0&readPreference=primary&appname=MongoDB%20Compass&ssl=true', ssl_cert_reqs=ssl.CERT_NONE)
db = cluster["UserData"]
collection = db["UserData"]


# launching bot, bot is ready
@client.event
async def on_ready():
    print('CAT TIME IS READY!')


# when bot joins, it sends its first message
@client.event
async def on_guild_join(guild):
    print(f'{client} has joined the server.')
    for channel in guild.text_channels:
        if channel.permissions_for(guild.me).send_messages:
            await channel.send('meow i am a cat meow !commands')
        break


# person has joined the server
@client.event
async def on_member_join(member):
    print(f'{member} has joined a server')
    channel = member.guild.system_channel
    if channel is not None:
        await asyncio.sleep(2)
        ment = member.mention
        await channel.send(f'welcome {ment} :3c!')


# person has been removed/left the server
@client.event
async def on_member_remove(member):
    print(f'{member} has left a server.')
    channel = member.guild.system_channel
    if channel is not None:
        await asyncio.sleep(2)
        ment = member.mention
        await channel.send(f'goodbye {ment} :3c...')


# lowers happiness/hunger as messages are sent
@client.event
async def on_message(ctx):
    if (not ctx.author.bot) and (ctx.content.lower() not in COMMANDS):
        hunger = change_hunger(-1, ctx.author.id)
        happiness = change_happiness(-1, ctx.author.id)
        if happiness == 0:
            await ctx.channel.send('i am so lonely no one cares about me')
        if hunger == 0:
            await ctx.channel.send('i am going to die please feed me some food')
    await client.process_commands(ctx)


# user will get their own cat !join
@client.command()
async def join(ctx):
    query = {"_id": ctx.author.id, "happiness": 100, "hunger": 50}
    if collection.count_documents(query) == 0:
        collection.insert_one(query)
        print(f'cat has been added to user {ctx.author}')
        await ctx.send(f'i will love you forever {ctx.message.author.name}')


# meows when someone says !meow
@client.command()
async def meow(ctx):
    change_happiness(-2, ctx.author.id)
    print(f'{ctx.author}\'s cat meows')
    await ctx.send('meow...')


# replies with :D when someone says !pet
@client.command()
async def pet(ctx):
    change_happiness(2, ctx.author.id)
    print(f'{ctx.author}\'s cat has been pet')
    await ctx.send(':3')


# feed the cat when someone says !feed
@client.command()
async def feed(ctx):
    change_hunger(20, ctx.author.id)
    print(f'{ctx.author}\'s cat has been fed')
    await ctx.send('thank u for feeding me...')


# play with cat when !play
@client.command()
async def play(ctx):
    change_happiness(20, ctx.author.id)
    change_hunger(-20, ctx.author.id)
    print(f'{ctx.author}\'s cat has been played with')
    await ctx.send(f'yaaaayyyyy :3 i love you {ctx.message.author.name}')


# scold cat !scold
@client.command()
async def scold(ctx):
    change_happiness(-20, ctx.author.id)
    print(f'{ctx.message.author.name}\'s cat has been scolded')
    await ctx.send('i am sad u would yell at me like that')


# user removed from db
@client.command()
async def abandon(ctx):
    query = {"_id": ctx.author.id}
    collection.delete_one(query)
    await ctx.send(f'i love u forever, {ctx.message.author.name}. goodbye.')


# checks the current cat stats when !stats
@client.command()
async def stats(ctx):
    happiness = get_happiness(ctx.author.id)
    hunger = get_hunger(ctx.author.id)
    print(f'{ctx.author.id} stats: {happiness}/100, {hunger}/100')
    await ctx.send(f'```fix\n'
                   f'★ CAT STATS ★ \n'
                   f'‣ HAPPINESS: {happiness}/100 \n'
                   f'‣ HUNGER: {hunger}/100```')


# sends message what commands cat bot can do
@client.command()
async def commands(ctx):
    await ctx.send('```fix\n'
                   '☆ CAT COMMAND STATION ☆\n'
                   'KEEP HUNGER AND HAPPINESS LEVELS ABOVE 0\n'
                   '‣ !adopt   → own a cat!\n'
                   '‣ !stats   → check my happiness and hunger levels :3 \n'
                   '‣ !meow    → i meow → -2 happiness\n'
                   '‣ !pet     → pet me → +2 happiness\n'
                   '‣ !feed    → feed me → +20 hunger \n'
                   '‣ !play    → play time → +20 happiness -20 hunger\n'
                   '‣ !scold   → yell at me → -20 happiness\n'
                   '‣ !abandon → leave ur cat. for good. :(```')

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


# change happiness by given int value
def change_happiness(value, user_id):
    happiness = get_happiness(user_id)
    if (happiness + value) < 0:
        happiness = 0
    elif (happiness + value) > 100:
        happiness = 100
    else:
        happiness += value
    collection.update_one({"_id": user_id}, {"$set": {"happiness": happiness}})
    return happiness


# change hunger by given int value
def change_hunger(value, user_id):
    hunger = get_hunger(user_id)
    if (hunger + value) < 0:
        hunger = 0
    elif (hunger + value) > 100:
        hunger = 100
    else:
        hunger += value
    collection.update_one({"_id": user_id}, {"$set": {"hunger": hunger}})
    return hunger


# get a user's cat happiness
def get_happiness(user_id):
    query = {"_id": user_id}
    return collection.find_one(query)['happiness']


# get a user's cat hunger
def get_hunger(user_id):
    query = {"_id": user_id}
    return collection.find_one(query)['hunger']


client.loop.create_task(cat_status())
# privated the bot key
client.run(os.environ['DISCORD_TOKEN'])
