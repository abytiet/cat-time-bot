import ssl
import discord
from discord.ext import commands
from discord.utils import get
from pymongo import MongoClient
import asyncio
import random
import os
from dotenv import load_dotenv
import requests

intents = discord.Intents(members=True, messages=True, guilds=True)
client = commands.Bot(command_prefix='~', intents=intents)

COMMANDS = ['~commands', '~pet', '~feed', '~meow', '~stats', '~play', '~scold', '~adopt', '~abandon', '~name', '~cps',
            '~fact', '~rehome']

load_dotenv()
cluster = MongoClient(os.environ['MONGODB'], ssl=True, ssl_cert_reqs=ssl.CERT_NONE)
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
            await channel.send('meow i am a cat meow ~commands')
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
    query = {"_id": ctx.author.id}
    if (not ctx.author.bot) and (ctx.content.lower() not in COMMANDS) and (collection.count_documents(query) != 0):
        hunger = change_hunger(-1, ctx.author.id)
        happiness = change_happiness(-1, ctx.author.id)
        cat_name = get_cat_name(ctx.author.id)
        if happiness == 0:
            await ctx.channel.send(f'**{cat_name}**: {ctx.author.mention} i am so lonely no one cares about me')
        if hunger == 0:
            await ctx.channel.send(f'**{cat_name}**: {ctx.author.mention} i am going to die please feed me some food')
    await client.process_commands(ctx)


# user will get their own cat !join
@client.command()
async def adopt(ctx):
    query = {"_id": ctx.author.id}
    if collection.count_documents(query) == 0:
        query = {"_id": ctx.author.id, "happiness": 100, "hunger": 50, "name": "cat"}
        collection.insert_one(query)
        print(f'cat has been added to user {ctx.author}')
        await ctx.send(f'i will love you forever {ctx.author.mention}')
    else:
        cat_name = get_cat_name(ctx.author.id)
        await ctx.send(f'**{cat_name}**: meow. {ctx.author.mention} wtf!!! u need to take care of me first.')


# names the cat
@client.command()
async def name(ctx):
    query = {"_id": ctx.author.id}
    if collection.count_documents(query) != 0:
        cat_name = ' '.join(ctx.message.content.split(' ')[1:])
        if cat_name == '':
            await ctx.send('i need a name! please include it after the !name command')
        else:
            new_value = {"name": cat_name}
            collection.update_one(query, {"$set": new_value})
            await ctx.send(f'i am {cat_name}')
    else:
        await ctx.send('```cats are waiting to be adopted. \n~adopt```')


# meows when someone says !meow
@client.command()
async def meow(ctx):
    query = {"_id": ctx.author.id}
    if collection.count_documents(query) != 0:
        change_happiness(-2, ctx.author.id)
        name = get_cat_name(ctx.author.id)
        print(f'{ctx.author}\'s cat meows')
        await ctx.send(f'**{name}**: meow...')
    else:
        await ctx.send('```cats are waiting to be adopted. \n~adopt```')


# replies with :D when someone says !pet
@client.command()
async def pet(ctx):
    query = {"_id": ctx.author.id}
    if collection.count_documents(query) != 0:
        change_happiness(2, ctx.author.id)
        name = get_cat_name(ctx.author.id)
        print(f'{ctx.author}\'s cat has been pet')
        await ctx.send(f'**{name}**: :3')
    else:
        await ctx.send('```cats are waiting to be adopted. \n~adopt```')


# feed the cat when someone says !feed
@client.command()
async def feed(ctx):
    query = {"_id": ctx.author.id}
    if collection.count_documents(query) != 0:
        change_hunger(20, ctx.author.id)
        cat_name = get_cat_name(ctx.author.id)
        print(f'{ctx.author}\'s cat has been fed')
        await ctx.send(f'**{cat_name}**: thank u for feeding me {ctx.author.mention}...')
    else:
        await ctx.send('```cats are waiting to be adopted. \n~adopt```')


# play with cat when !play
@client.command()
async def play(ctx):
    query = {"_id": ctx.author.id}
    if collection.count_documents(query) != 0:
        change_happiness(20, ctx.author.id)
        change_hunger(-20, ctx.author.id)
        cat_name = get_cat_name(ctx.author.id)
        print(f'{ctx.author}\'s cat has been played with')
        await ctx.send(f'**{cat_name}**: yaaaayyyyy :3')
    else:
        await ctx.send('```cats are waiting to be adopted. \n~adopt```')


# scold cat ~scold
@client.command()
async def scold(ctx):
    query = {"_id": ctx.author.id}
    if collection.count_documents(query) != 0:
        change_happiness(-20, ctx.author.id)
        cat_name = get_cat_name(ctx.author.id)
        print(f'{ctx.message.author.name}\'s cat has been scolded')
        await ctx.send(f'**{cat_name}**: i am sad u would yell at me like that')
    else:
        await ctx.send('```cats are waiting to be adopted. \n~adopt```')


# user removed from db
@client.command()
async def abandon(ctx):
    query = {"_id": ctx.author.id}
    if collection.count_documents(query) != 0:
        cat_name = get_cat_name(ctx.author.id)
        collection.delete_one(query)
        print(f'{ctx.message.author.name}\'s cat has been abandoned')
        await ctx.send(f'**{cat_name}**: i\'ll love u forever, {ctx.author.mention}. goodbye.')
    else:
        await ctx.send(f'don\'t even think of adopting me if ur just gonna leave me {ctx.author.mention}! '
                       f'the pain will be too much for me to handle... :(')

# remove a user's cat if the author is in CPS
@client.command(name="rehome")
@commands.has_role('CAT PROTECTION SERVICES')
async def rehome(ctx):
    cmd = ctx.message.content.split(" ")
    if len(cmd) != 2 or len(ctx.message.mentions) != 1:
        await ctx.send("Incorrect arguments provided...meow")
    else:
        mention = ctx.message.mentions[0]
        query = {"_id": mention.id}
        if collection.count_documents(query) != 0:
            collection.delete_one(query)
            print(f'{mention} \'s cat has been re-homed.')
            await ctx.send(f'{mention.mention}\'s cat has been re-homed.')
        else:
            await ctx.send("This user does not own a cat.")

@rehome.error
async def rehome_error(ctx, error):
    await ctx.send("CAT PROTECTION SERVICES role is a requirement to use this command!")

# creates CAT PROTECTION SERVICES role
@client.command()
async def cps(ctx):
    if get(ctx.guild.roles, name="CAT PROTECTION SERVICES"):
        await ctx.send("Cat Protection Services are already called.")
    else:
        await ctx.guild.create_role(name="CAT PROTECTION SERVICES")
        await ctx.send("PROTECT OUR FELINE FRIENDS BY JOINING CAT PROTECTION SERVICES. "
                       "SAVE CATS FROM THEIR BAD OWNERS!")

# use Cat Facts API to get random cat facts
@client.command()
async def fact(ctx):
    response = requests.get("https://cat-fact.herokuapp.com/facts/random?animal_type=cat")
    cat_fact = response.json()["text"]
    await ctx.send(cat_fact + " :3")

# checks the current cat stats when ~stats
@client.command()
async def stats(ctx):
    query = {"_id": ctx.author.id}
    if collection.count_documents(query) != 0:
        happiness = get_happiness(ctx.author.id)
        hunger = get_hunger(ctx.author.id)
        cat_name = get_cat_name(ctx.author.id).upper()
        print(f'{ctx.author.id} stats: {happiness}/100 happiness, {hunger}/100 hunger')
        await ctx.send(f'{ctx.author.mention}\n```fix\n'
                       f'★ {cat_name}\'S STATS ★ \n'
                       f'‣ HAPPINESS: {happiness}/100 \n'
                       f'‣ HUNGER: {hunger}/100```')
    else:
        await ctx.send('```cats are waiting to be adopted. \n~adopt```')


# sends message what commands cat bot can do
@client.command()
async def commands(ctx):
    await ctx.send('```fix\n'
                   '☆ CAT COMMAND STATION ☆\n'
                   'KEEP HUNGER AND HAPPINESS LEVELS ABOVE 0\n'
                   '‣ ~adopt   → adopt me\n'
                   '‣ ~name    → name me \n'
                   '‣ ~stats   → check my happiness and hunger levels :3 \n'
                   '‣ ~meow    → i meow → -2 happiness\n'
                   '‣ ~pet     → pet me → +2 happiness\n'
                   '‣ ~feed    → feed me → +20 hunger \n'
                   '‣ ~play    → play time → +20 happiness -20 hunger\n'
                   '‣ ~scold   → yell at me → -20 happiness\n'
                   '‣ ~fact   → get a random cat fact'
                   '‣ ~abandon → leave me. for good. :(\n'
                   '‣ ~cps     → summon cat protection services\n'
                   '‣ ~rehome [mentioned user] → CPS role only! include mention of a user to rehome their cat```')


# logs out of discord and closes all connections
@client.command()
async def logout():
    await client.logout()


# background task that sets game status for cat
async def cat_status():
    await client.wait_until_ready()
    statuses = ["meowing", "nyaaa", ":3", ":3c", "doing cat things", "~commands", "~adopt me"]
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


# get a user's cat name
def get_cat_name(user_id):
    query = {"_id": user_id}
    return collection.find_one(query)['name']


client.loop.create_task(cat_status())
# privated the bot key
client.run(os.environ['DISCORD_TOKEN'])
