import os

import discord
from discord.ext import commands
from dotenv import load_dotenv
from pymongo import MongoClient
from rich.console import Console
from rich.table import Table


# from pprint import pprint


class SquadCounter:
    count = 1


counter = SquadCounter()

load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')
client = discord.Client()
print(TOKEN)
mango_url = os.getenv('MANGO_URL')
cluster = MongoClient(mango_url)
db = cluster["ChronoHunt"]

collection = db["squads"]
# Database structure
# id int Primary Key
# guild text
# member_1 text
# member_2 text
# member_3 text
# is_perm int DEFAULT 0
# times_won int DEFAULT 0
# last_date_won DEFAULT CURRENT_TIMESTAMP

bot = commands.Bot(command_prefix='!')


@bot.event
async def on_ready():
    print(f'{bot.user.name} has connected to Discord!')


def check_if_member_exists(name):
    name = name.lower()
    myquery = {"member_1": name}
    if collection.count_documents(myquery) == 0:
        myquery = {"member_2": name}
        if collection.count_documents(myquery) == 0:
            myquery = {"member_3": name}
            if collection.count_documents(myquery) == 0:
                return False
    return True


@bot.command(name='new', help='Command for adding a new temporary Chrono Hunt Squad. Call with !new name1 name2 name3')
async def new(ctx, arg1, arg2, arg3):
    print(f"{ctx.channel}: {ctx.author}: {ctx.author.name}: {arg1}: {arg2}: {arg3}")
    # Make sure none of these members are already in a squad
    if check_if_member_exists(arg1):
        await ctx.channel.send(f'{arg1} already belongs to a squad. Please delete or edit the other squad')
        return

    if check_if_member_exists(arg2):
        await ctx.channel.send(f'{arg2} already belongs to a squad. Please delete or edit the other squad')
        return

    if check_if_member_exists(arg3):
        await ctx.channel.send(f'{arg3} already belongs to a squad. Please delete or edit the other squad')
        return

    post = {"member_1": arg1.lower(), "member_2": arg2.lower(), "member_3": arg3.lower(), "is_perm": 0,
            "times_won": 0, "last_win_date": "", "squad_num": counter.count}
    collection.insert_one(post)

    counter.count += 1

    await ctx.channel.send(f'Squad of {arg1}, {arg2}, and {arg3} has been added!')


@bot.command(name='changemember', help='Command for change a member an existing Chrono Hunt Squad. Call with !edit squad_number member_number new_member_name')
async def change_member(ctx, arg1, arg2, arg3):
    print(f"{ctx.channel}: {ctx.author}: {ctx.author.name}: {arg1}: {arg2}: {arg3}")

    # Make sure this squad number exists
    myquery = {"squad_num": int(arg1)}
    print(myquery)
    if collection.count_documents(myquery) == 0:
        await ctx.channel.send(f'Squad number {arg1} does not exist. Try using the !squads command to see the squads and their numbers')
        return

    if int(arg2) == 1:
        newvalues = {"$set": {"member_1": arg3}}
        collection.update_one(myquery, newvalues)
    elif int(arg2) == 2:
        newvalues = {"$set": {"member_2": arg3}}
        collection.update_one(myquery, newvalues)
    elif int(arg2) == 3:
        newvalues = {"$set": {"member_3": arg3}}
        collection.update_one(myquery, newvalues)
    else:
        await ctx.channel.send(f'Member number {arg2} does not exist. Please pick a number between 1 and 3')
        return
    await ctx.channel.send(f'Squad {arg1} has been updated!')


@bot.command(name='delete', help='Command for deleting a Chrono Hunt Squad. Call with !delete squad_number')
async def delete(ctx, arg1):
    print(f"{ctx.channel}: {ctx.author}: {ctx.author.name}: {arg1}")
    # Make sure this squad number exists
    myquery = {"squad_num": int(arg1)}
    print(myquery)
    if collection.count_documents(myquery) == 0:
        await ctx.channel.send(f'Squad number {arg1} does not exist. Try using the !squads command to see the squads and their numbers')
        return

    collection.delete_one(myquery)

    await ctx.channel.send(f'Squad {arg1} has been deleted!')


@bot.command(name='clear', help='Command for clearing all Chrono Hunt Squads not marked permanent. Call with !clear')
async def clear(ctx):
    print(f"{ctx.channel}: {ctx.author}: {ctx.author.name}")
    # Make sure this squad number exists
    myquery = {"is_perm": 0}
    print(myquery)

    collection.delete_one(myquery)

    await ctx.channel.send(f'All non permanent squads have been deleted!')


# @bot.command(name='perm', help='Command for making a Chrono Hunt Squad permanent. Call with !perm squad_number')
# async def perm(ctx, arg1):
#     print(f"{ctx.channel}: {ctx.author}: {ctx.author.name}: {arg1}")
#     # Make sure this squad number exists
#     myquery = {"squad_num": int(arg1)}
#     print(myquery)
#     if collection.count_documents(myquery) == 0:
#         await ctx.channel.send(f'Squad number {arg1} does not exist. Try using the !squads command to see the squads and their numbers')
#         return
#
#     newvalues = {"$set": {"is_perm": 1}}
#
#     collection.update_one(myquery, newvalues)
#
#     await ctx.channel.send(f'Squad {arg1} has been upgraded to permanent status!')


# @bot.command(name='notperm', help='Command for making a Chrono Hunt Squad no longer permanent. Call with !notperm squad_number')
# async def not_perm(ctx, arg1):
#     print(f"{ctx.channel}: {ctx.author}: {ctx.author.name}: {arg1}")
#     # Make sure this squad number exists
#     myquery = {"squad_num": int(arg1)}
#     print(myquery)
#     if collection.count_documents(myquery) == 0:
#         await ctx.channel.send(f'Squad number {arg1} does not exist. Try using the !squads command to see the squads and their numbers')
#         return
#
#     newvalues = {"$set": {"is_perm": 0}}
#
#     collection.update_one(myquery, newvalues)
#
#     await ctx.channel.send(f'Permanent status for squad {arg1} has been removed!')


@bot.command(name='squads', help='Command for displaying all Chrono Hunt Squads. Call with !squads')
async def squads(ctx):
    console = Console()
    cursor = collection.find({})

    table = Table(show_header=True, header_style="bold magenta")
    table.add_column("Squad Number", style="dim", width=12)
    table.add_column("Member 1")
    table.add_column("Member 2")
    table.add_column("Member 3")

    # (('apple', '$1.09', '80'), ('truffle', '$58.01', '2')):
    # ...
    # print
    '{0:<10} {1:>8} {2:>8}'.format((('apple', '$1.09', '80'), ('truffle', '$58.01', '2')))

    output = '{0:^15} {1:^10} {2:^10} {3:^10}\n'.format(['Squad Number', 'Member 1', 'Member 2', 'Member 3'])

    for document in cursor:
        output += '{0:^15} {1:^10} {2:^10} {3:^10}\n'.format((str(document['squad_num']), str(document['member_1']), str(document['member_2']), str(document['member_3'])))
        # table.add_row(str(document['squad_num']), str(document['member_1']), str(document['member_2']), str(document['member_3']))

    await ctx.channel.send(output)

bot.run(TOKEN)
