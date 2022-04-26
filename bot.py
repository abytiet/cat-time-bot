"""
Cat Bot by Aby Tiet
"""

import ssl
import discord
from discord.ext import commands
from discord.utils import get
from pymongo import MongoClient
import asyncio
import random
import requests
import constants as cons

intents = discord.Intents(members=True, messages=True, guilds=True)
client = commands.Bot(command_prefix='~', intents=intents)

cluster = MongoClient(cons.MONGODB_TOKEN, ssl=True, ssl_cert_reqs=ssl.CERT_NONE)
db = cluster["UserData"]
collection = db["UserData"]


@client.event
async def on_ready():
    """
    Print on bot ready
    """
    print('CAT TIME IS READY!')


@client.event
async def on_guild_join(guild):
    """
    Send message in server on bot join
    :param guild: Discord server
    """
    print(f'{client} has joined the server.')
    for channel in guild.text_channels:
        if channel.permissions_for(guild.me).send_messages:
            await channel.send('meow i am a cat meow ~commands')
        break


@client.event
async def on_member_join(member):
    """
    Send a message when a user joins the server
    :param member: User who joined
    """
    print(f'{member} has joined a server')
    channel = member.guild.system_channel
    if channel is not None:
        await asyncio.sleep(2)
        ment = member.mention
        await channel.send(f'welcome {ment} :3c!')


@client.event
async def on_member_remove(member):
    """
    Send a message when a user leaves the server
    :param member: User who left
    """
    print(f'{member} has left a server.')
    channel = member.guild.system_channel
    if channel is not None:
        await asyncio.sleep(2)
        ment = member.mention
        await channel.send(f'goodbye {ment} :3c...')


@client.event
async def on_message(ctx):
    """
    Lowers happiness and hunger levels by 1 if user owns a cat and not using a command
    :param ctx: Context of command
    """
    query = {"_id": ctx.author.id}
    if (not ctx.author.bot) and (ctx.content.lower() not in cons.COMMANDS) and (collection.count_documents(query) != 0):
        hunger = change_hunger(-1, ctx.author.id)
        happiness = change_happiness(-1, ctx.author.id)
        cat_name = get_cat_name(ctx.author.id)
        if happiness == 0:
            lonely = random.choice(cons.LONELY)
            await ctx.channel.send(f'**{cat_name}**: {ctx.author.mention} ' + lonely)
        if hunger == 0:
            hungry = random.choice(cons.HUNGRY)
            await ctx.channel.send(f'**{cat_name}**: {ctx.author.mention} ' + hungry)
    await client.process_commands(ctx)


@client.command()
async def adopt(ctx):
    """
    Add user to DB on ~join command
    Message sent if user already owns a cat
    :param ctx: Context of command
    """
    query = {"_id": ctx.author.id}
    if collection.count_documents(query) == 0:
        query = {"_id": ctx.author.id, "happiness": 100, "hunger": 50, "name": "cat"}
        collection.insert_one(query)
        print(f'cat has been added to user {ctx.author}')
        await ctx.send(f'i will love you forever {ctx.author.mention}')
    else:
        cat_name = get_cat_name(ctx.author.id)
        await ctx.send(f'**{cat_name}**: meow. {ctx.author.mention} wtf!!! u need to take care of me first.')


@client.command()
async def name(ctx):
    """
    Change the name of the user's cat
    :param ctx: Context of command
    """
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


@client.command()
async def meow(ctx):
    """
    Cat sends meow message on ~meow command, lowers happiness level by 2
    :param ctx: Context of command
    """
    query = {"_id": ctx.author.id}
    if collection.count_documents(query) != 0:
        change_happiness(-2, ctx.author.id)
        name = get_cat_name(ctx.author.id)
        print(f'{ctx.author}\'s cat meows')
        await ctx.send(f'**{name}**: meow...')
    else:
        await ctx.send('```cats are waiting to be adopted. \n~adopt```')


@client.command()
async def pet(ctx):
    """
    Cat sends :3 message on ~pet, raises happiness level by 2
    :param ctx: Context of command
    """
    query = {"_id": ctx.author.id}
    if collection.count_documents(query) != 0:
        change_happiness(2, ctx.author.id)
        name = get_cat_name(ctx.author.id)
        print(f'{ctx.author}\'s cat has been pet')
        await ctx.send(f'**{name}**: :3')
    else:
        await ctx.send('```cats are waiting to be adopted. \n~adopt```')


@client.command()
async def feed(ctx):
    """
    Feeds cat on ~feed command, raises hunger level
    :param ctx: Context of command
    """
    query = {"_id": ctx.author.id}
    if collection.count_documents(query) != 0:
        change_hunger(20, ctx.author.id)
        cat_name = get_cat_name(ctx.author.id)
        print(f'{ctx.author}\'s cat has been fed')
        await ctx.send(f'**{cat_name}**: thank u for feeding me {ctx.author.mention}...')
    else:
        await ctx.send('```cats are waiting to be adopted. \n~adopt```')


@client.command()
async def play(ctx):
    """
    Plays with cat on ~play command, raises happiness level but lowers hunger level
    :param ctx: Context of command
    """
    query = {"_id": ctx.author.id}
    if collection.count_documents(query) != 0:
        change_happiness(20, ctx.author.id)
        change_hunger(-20, ctx.author.id)
        cat_name = get_cat_name(ctx.author.id)
        print(f'{ctx.author}\'s cat has been played with')
        await ctx.send(f'**{cat_name}**: yaaaayyyyy :3')
    else:
        await ctx.send('```cats are waiting to be adopted. \n~adopt```')


@client.command()
async def scold(ctx):
    """
    Lower happiness level of cat on ~scold command
    :param ctx: Context of command
    """
    query = {"_id": ctx.author.id}
    if collection.count_documents(query) != 0:
        change_happiness(-20, ctx.author.id)
        cat_name = get_cat_name(ctx.author.id)
        print(f'{ctx.message.author.name}\'s cat has been scolded')
        await ctx.send(f'**{cat_name}**: i am sad u would yell at me like that')
    else:
        await ctx.send('```cats are waiting to be adopted. \n~adopt```')


@client.command()
async def abandon(ctx):
    """
    Remove a cat from the user
    :param ctx: Context of command
    """
    query = {"_id": ctx.author.id}
    if collection.count_documents(query) != 0:
        cat_name = get_cat_name(ctx.author.id)
        collection.delete_one(query)
        print(f'{ctx.message.author.name}\'s cat has been abandoned')
        await ctx.send(f'**{cat_name}**: i\'ll love u forever, {ctx.author.mention}. goodbye.')
    else:
        await ctx.send(f'don\'t even think of adopting me if ur just gonna leave me {ctx.author.mention}! '
                       f'the pain will be too much for me to handle... :(')

@client.command(name="rehome")
@commands.has_role('CAT PROTECTION SERVICES')
async def rehome(ctx):
    """
    Remove a user's cat if the other has CPS role and owns a cat.
    :param ctx: Context of command
    """
    cmd = ctx.message.content.split(" ")
    # Incorrect arguments or did not mention a single user
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
    """
    Sends error message when someone tries to use a CAT PROTECTION SERVICES restricted command
    :param ctx: Context of command
    :param error: Error
    """
    await ctx.send("CAT PROTECTION SERVICES role is a requirement to use this command!")

@client.command()
async def cps(ctx):
    """
    Creates CAT PROTECTION SERVICES role in Discord server
    If it exists, message is sent to notify that role exists
    :param ctx: Context of command
    """
    if get(ctx.guild.roles, name="CAT PROTECTION SERVICES"):
        await ctx.send("Cat Protection Services are already called.")
    else:
        await ctx.guild.create_role(name="CAT PROTECTION SERVICES")
        await ctx.send("PROTECT OUR FELINE FRIENDS BY JOINING CAT PROTECTION SERVICES. "
                       "SAVE CATS FROM THEIR BAD OWNERS!")

@client.command()
async def fact(ctx):
    """
    Using Cat Facts API, get a random cat fact
    :param ctx: Context of command
    """
    query = {"_id": ctx.author.id}
    if collection.count_documents(query) != 0:
        cat_name = get_cat_name(ctx.author.id)
        response = requests.get("https://cat-fact.herokuapp.com/facts/random?animal_type=cat")
        cat_fact = response.json()["text"]
        await ctx.send(f'**{cat_name}**: you knyow i heard...```' + cat_fact + '```')
    # Command only works if you have a cat adopted
    else:
        await ctx.send('```cats are waiting to be adopted. \n~adopt```')


@client.command()
async def stats(ctx):
    """
    Get current happiness and hunger levels of cats on ~stats command
    :param ctx: Context of command
    """
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


@client.command()
async def commands(ctx):
    """
    Send message on usage for Cat Bot
    :param ctx: Context of command
    """
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
                   '‣ ~fact    → get a random cat fact\n'
                   '‣ ~abandon → leave me. for good. :(\n'
                   '‣ ~cps     → summon cat protection services\n'
                   '‣ ~rehome [mentioned user] → CPS role only! include mention of a user to rehome their cat```')


@client.command()
async def logout():
    """
    Logs out of Discord and closes all connections
    """
    await client.logout()


async def cat_status():
    """
    Background task that sets game status for Cat Bot
    Changes every 30 seconds
    """
    await client.wait_until_ready()
    statuses = cons.STATUSES
    while not client.is_closed():
        status = random.choice(statuses)
        await client.change_presence(activity=discord.Game(status))
        await asyncio.sleep(30)


def change_happiness(value, user_id):
    """
    Change happiness level of cat by given value
    :param value: Amount to change happiness
    :param user_id: User ID to change cat happiness level
    :return: Happiness level of cat after changing
    """
    happiness = get_happiness(user_id)
    if (happiness + value) < 0:
        happiness = 0
    elif (happiness + value) > 100:
        happiness = 100
    else:
        happiness += value
    collection.update_one({"_id": user_id}, {"$set": {"happiness": happiness}})
    return happiness


def change_hunger(value, user_id):
    """
    Change hunger level of cat by given value
    :param value: Amount to change hunger
    :param user_id: User ID to change cat hunger level
    :return: Hunger level of cat after changing
    """
    hunger = get_hunger(user_id)
    if (hunger + value) < 0:
        hunger = 0
    elif (hunger + value) > 100:
        hunger = 100
    else:
        hunger += value
    collection.update_one({"_id": user_id}, {"$set": {"hunger": hunger}})
    return hunger


def get_happiness(user_id):
    """
    Get happiness level of a user's cat
    :param user_id: User ID to get happiness level from
    :return: Cat happiness level (int)
    """
    query = {"_id": user_id}
    return collection.find_one(query)['happiness']


def get_hunger(user_id):
    """
    Get hunger level of a user's cat
    :param user_id: User ID to get hunger level from
    :return: Cat hunger level (int)
    """
    query = {"_id": user_id}
    return collection.find_one(query)['hunger']


def get_cat_name(user_id):
    """
    Get name of user's cat
    :param user_id: User ID to get cat from
    :return: Name of cat
    """
    query = {"_id": user_id}
    return collection.find_one(query)['name']


client.loop.create_task(cat_status())

client.run(cons.DISCORD_TOKEN)
