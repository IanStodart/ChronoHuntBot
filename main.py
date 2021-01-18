import os

import discord
from discord.ext import commands
from dotenv import load_dotenv
from pymongo import MongoClient

load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')
client = discord.Client()
mango_url = os.getenv('MANGO_URL')
cluster = MongoClient(mango_url)
db = cluster["ChronoHunt"]

squads_collection = db["squads"]
available_collection = db["available"]

bot = commands.Bot(command_prefix='!')


@bot.event
async def on_ready():
    print(f'{bot.user.name} has connected to Discord!')


def check_if_member_exists_in_squad(name):
    name = name.lower()
    print(name)
    if name == '[empty]':
        return False
    myquery = {"member_1": name}
    if squads_collection.count_documents(myquery) == 0:
        myquery = {"member_2": name}
        if squads_collection.count_documents(myquery) == 0:
            myquery = {"member_3": name}
            if squads_collection.count_documents(myquery) == 0:
                return False
    return True


def check_if_member_exists_in_available(name):
    name = name.lower()
    print(name)

    myquery = {"name": name}
    if available_collection.count_documents(myquery) == 0:
        return False
    return True


def check_if_squad_exists(squad_num):
    if int(squad_num) <= squads_collection.count({}):
        return True
    else:
        False


def find_member_to_update(focused_squad, myquery, arg2):
    if str(focused_squad['member_1']) == '[empty]':
        newvalues = {"$set": {"member_1": arg2.lower()}}
        squads_collection.update_one(myquery, newvalues)
    elif str(focused_squad['member_2']) == '[empty]':
        newvalues = {"$set": {"member_2": arg2.lower()}}
        squads_collection.update_one(myquery, newvalues)
    elif str(focused_squad['member_3']) == '[empty]':
        newvalues = {"$set": {"member_3": arg2.lower()}}
        squads_collection.update_one(myquery, newvalues)
    else:
        return False
    return True


def find_member_to_remove(focused_squad, myquery, arg2):
    if str(focused_squad['member_1']) == arg2.lower():
        newvalues = {"$set": {"member_1": '[empty]'}}
        squads_collection.update_one(myquery, newvalues)
    elif str(focused_squad['member_2']) == arg2.lower():
        newvalues = {"$set": {"member_2": '[empty]'}}
        squads_collection.update_one(myquery, newvalues)
    elif str(focused_squad['member_3']) == arg2.lower():
        newvalues = {"$set": {"member_3": '[empty]'}}
        squads_collection.update_one(myquery, newvalues)
    else:
        return False
    return True


def find_member_to_update(focused_squad, myquery, arg2, arg3):
    if str(focused_squad['member_1']) == arg2.lower():
        newvalues = {"$set": {"member_1": arg3.lower()}}
        squads_collection.update_one(myquery, newvalues)
    elif str(focused_squad['member_2']) == arg2.lower():
        newvalues = {"$set": {"member_2": arg3.lower()}}
        squads_collection.update_one(myquery, newvalues)
    elif str(focused_squad['member_3']) == arg2.lower():
        newvalues = {"$set": {"member_3": arg3.lower()}}
        squads_collection.update_one(myquery, newvalues)
    else:
        return False
    return True


@bot.command(name='newmain', help='Command for adding a new MAIN temporary Chrono Hunt Squad.') # MUST HAVE AT LEAST 1 MEMBER.') # Call with !new name1 name2 name3')
async def newmain(ctx, arg1, *args):
    temp_list = list(args)
    if len(temp_list) == 1:
        temp_list.append('[EMPTY]')
    elif len(temp_list) == 0:
        temp_list.append('[EMPTY]')
        temp_list.append('[EMPTY]')
    arg2 = temp_list[0]
    arg3 = temp_list[1]
    print(f"{ctx.channel}: {ctx.author}: {ctx.author.name}: {arg1}: {arg2}: {arg3}")

    # Make sure none of these members are already in a squad
    if check_if_member_exists_in_squad(arg1):
        await ctx.channel.send(f'{arg1} already belongs to a squad. Please delete or edit the other squad')
        return

    if check_if_member_exists_in_squad(arg2):
        await ctx.channel.send(f'{arg2} already belongs to a squad. Please delete or edit the other squad')
        return

    if check_if_member_exists_in_squad(arg3):
        await ctx.channel.send(f'{arg3} already belongs to a squad. Please delete or edit the other squad')
        return

    post = {"member_1": arg1.lower(), "member_2": arg2.lower(), "member_3": arg3.lower(), "is_perm": 0,
            "times_won": 0, "last_win_date": "", "squad_num": squads_collection.count(), "is_main": 1}
    squads_collection.insert_one(post)

    await ctx.channel.send(f'Squad of {arg1}, {arg2}, and {arg3} has been added!')


@bot.command(name='newalt', help='Command for adding a new ALT Chrono Hunt Squad.') # MUST HAVE AT LEAST 1 MEMBER.') # Call with !new name1 name2 name3')
async def newalt(ctx, arg1, *args):
    temp_list = list(args)
    if len(temp_list) == 1:
        temp_list.append('[EMPTY]')
    elif len(temp_list) == 0:
        temp_list.append('[EMPTY]')
        temp_list.append('[EMPTY]')
    arg2 = temp_list[0]
    arg3 = temp_list[1]
    print(f"{ctx.channel}: {ctx.author}: {ctx.author.name}: {arg1}: {arg2}: {arg3}")

    # Make sure none of these members are already in a squad
    if check_if_member_exists_in_squad(arg1):
        await ctx.channel.send(f'{arg1} already belongs to a squad. Please delete or edit the other squad')
        return

    if check_if_member_exists_in_squad(arg2):
        await ctx.channel.send(f'{arg2} already belongs to a squad. Please delete or edit the other squad')
        return

    if check_if_member_exists_in_squad(arg3):
        await ctx.channel.send(f'{arg3} already belongs to a squad. Please delete or edit the other squad')
        return

    post = {"member_1": arg1.lower(), "member_2": arg2.lower(), "member_3": arg3.lower(), "is_perm": 0,
            "times_won": 0, "last_win_date": "", "squad_num": squads_collection.count(), "is_main": 0}
    squads_collection.insert_one(post)

    await ctx.channel.send(f'Squad of {arg1}, {arg2}, and {arg3} has been added!')


@bot.command(name='change', help='Command for change a member an existing Chrono Hunt Squad.') # Call with !edit squad_number member_number new_member_name')
async def change_member(ctx, arg1, arg2, arg3):
    print(f"{ctx.channel}: {ctx.author}: {ctx.author.name}: {arg1}: {arg2}: {arg3}")

    if not (check_if_member_exists_in_squad(arg2)):
        await ctx.channel.send(f'{arg2} is not in a squad. Please add or edit the other squad')
        return

    # Make sure this squad number exists
    if not (check_if_squad_exists(arg1)):
        await ctx.channel.send(f'Squad number {arg1} does not exist. Try using the !squads command to see the squads and their numbers')
        return

    mains = squads_collection.find({'is_main': 1})
    alts = squads_collection.find({'is_main': 0})

    temp = int(arg1) - 1

    if int(arg1) <= mains.count():
        focused_squad = mains[temp]
        myquery = {"_id": focused_squad['_id']}
        if not (find_member_to_update(focused_squad, myquery, arg2, arg3)):
            await ctx.channel.send(f'Squad number {arg1} does not have {arg1}. Try using the !squads command to find which squad {arg1} is in.')
            return
    else:
        focused_squad = alts[temp - mains.count()]
        myquery = {"_id": focused_squad['_id']}
        if not (find_member_to_update(focused_squad, myquery, arg2, arg3)):
            await ctx.channel.send(f'Squad number {arg1} does not have {arg1}. Try using the !squads command to find which squad {arg1} is in.')
            return
    await ctx.channel.send(f'Squad {arg1} has been updated!')


@bot.command(name='add', help='Command to add a member to a squad that has an [EMPTY] spot.') # Call with !add squad_number, new_member_name')
async def add_member(ctx, arg1, arg2):

    if check_if_member_exists_in_squad(arg2):
        await ctx.channel.send(f'{arg2} already belongs to a squad. Please delete or edit the other squad')
        return

    # Make sure this squad number exists
    if not(check_if_squad_exists(arg1)):
        await ctx.channel.send(f'Squad number {arg1} does not exist. Try using the !squads command to see the squads and their numbers')
        return

    mains = squads_collection.find({'is_main': 1})
    alts = squads_collection.find({'is_main': 0})

    temp = int(arg1)-1

    if int(arg1) <= mains.count():
        focused_squad = mains[temp]
        myquery = {"_id": focused_squad['_id']}
        if not(find_member_to_update(focused_squad, myquery, arg2)):
            await ctx.channel.send(f'Squad number {arg1} does not have room for anyone else. Try using the !squads command to see the squads and where there is an [Empty] spot')
            return
    else:
        focused_squad = alts[temp-mains.count() - 1]
        myquery = {"_id": focused_squad['_id']}
        if not (find_member_to_update(focused_squad, myquery, arg2)):
            await ctx.channel.send(f'Squad number {arg1} does not have room for anyone else. Try using the !squads command to see the squads and where there is an [Empty] spot')
            return
    await ctx.channel.send(f'{arg2} has been added to Squad {arg1}!')


@bot.command(name='remove', help='Command to remove a member to from squad, creates[EMPTY] spot.') # Call with !add squad_number, new_member_name')
async def remove_member(ctx, arg1, arg2):

    if not (check_if_member_exists_in_squad(arg2)):
        await ctx.channel.send(f'{arg2} is not in a squad. Please add or edit the other squad')
        return

    # Make sure this squad number exists
    if not (check_if_squad_exists(arg1)):
        await ctx.channel.send(f'Squad number {arg1} does not exist. Try using the !squads command to see the squads and their numbers')
        return

    mains = squads_collection.find({'is_main': 1})
    alts = squads_collection.find({'is_main': 0})

    temp = int(arg1) - 1

    if int(arg1) <= mains.count():
        focused_squad = mains[temp]
        myquery = {"_id": focused_squad['_id']}
        if not (find_member_to_remove(focused_squad, myquery, arg2)):
            await ctx.channel.send(f'Squad number {arg1} does not have {arg1}. Try using the !squads command to find which squad {arg1} is in.')
            return
    else:
        focused_squad = alts[temp - mains.count()]
        myquery = {"_id": focused_squad['_id']}
        if not (find_member_to_remove(focused_squad, myquery, arg2)):
            await ctx.channel.send(f'Squad number {arg1} does not have {arg1}. Try using the !squads command to find which squad {arg1} is in.')
            return
    await ctx.channel.send(f'{arg2} has been removed from Squad {arg1}!')


@bot.command(name='delete', help='Command for deleting a Chrono Hunt Squad.') # Call with !delete squad_number')
async def delete(ctx, arg1):

    # Make sure this squad number exists
    if not (check_if_squad_exists(arg1)):
        await ctx.channel.send(f'Squad number {arg1} does not exist. Try using the !squads command to see the squads and their numbers')
        return

    mains = squads_collection.find({'is_main': 1})
    alts = squads_collection.find({'is_main': 0})

    temp = int(arg1) - 1

    if int(arg1) <= mains.count():
        focused_squad = mains[temp]
        myquery = {"_id": focused_squad['_id']}
        squads_collection.delete_one(myquery)
    else:
        focused_squad = alts[temp - mains.count()]
        myquery = {"_id": focused_squad['_id']}
        squads_collection.delete_one(myquery)
    await ctx.channel.send(f'Squad {arg1} has been deleted!')


@bot.command(name='clear', help='Command for clearing all Chrono Hunt Squads not marked permanent.') # Call with !clear')
async def clear(ctx):
    print(f"{ctx.channel}: {ctx.author}: {ctx.author.name}")
    # Make sure this squad number exists
    myquery = {"is_perm": 0}
    print(myquery)

    squads_collection.delete_many(myquery)

    await ctx.channel.send(f'All non permanent squads have been deleted!')


@bot.command(name='squads', help='Command for displaying all Chrono Hunt Squads.') # Call with !squads')
async def squads(ctx):
    cursor = squads_collection.find({'is_main': 1})
    embed = discord.Embed(title=f"__**{ctx.guild.name} Chrono Hunt [MAIN] Squads List:**__", color=0x03f8fc, timestamp=ctx.message.created_at)
    count = 1
    for document in cursor:
        num = str(document['squad_num'])
        m1 = '**' + str(document['member_1']) + '**' if str(document['member_1']) == '[empty]' else str(document['member_1'])
        m2 = '**' + str(document['member_2']) + '**' if str(document['member_2']) == '[empty]' else str(document['member_2'])
        m3 = '**' + str(document['member_3']) + '**' if str(document['member_3']) == '[empty]' else str(document['member_3'])
        embed.add_field(name=f'**Squad {count}**', value=f'> {m1}\n > {m2}\n > {m3}')
        count += 1
    await ctx.channel.send(embed=embed)

    cursor = squads_collection.find({'is_main': 0})
    embed = discord.Embed(title=f"__**{ctx.guild.name} Chrono Hunt [ALT] Squads List:**__", color=0x03f8fc, timestamp=ctx.message.created_at)
    for document in cursor:
        num = str(document['squad_num'])
        m1 = '**' + str(document['member_1']) + '**' if str(document['member_1']) == '[empty]' else str(document['member_1'])
        m2 = '**' + str(document['member_2']) + '**' if str(document['member_2']) == '[empty]' else str(document['member_2'])
        m3 = '**' + str(document['member_3']) + '**' if str(document['member_3']) == '[empty]' else str(document['member_3'])
        embed.add_field(name=f'**Squad {count}**', value=f'> {m1}\n > {m2}\n > {m3}')
        count += 1
    await ctx.channel.send(embed=embed)

    cursor = available_collection.find({'is_main': 1})
    embed = discord.Embed(title=f"__**{ctx.guild.name} Chrono Hunt Available [MAIN] List:**__", color=0x03f8fc, timestamp=ctx.message.created_at)
    for document in cursor:
        m1 = str(document['name'])
        embed.add_field(name=f'> {m1}', value='\u200b', inline=True)
    await ctx.channel.send(embed=embed)

    cursor = available_collection.find({'is_main': 0})
    embed = discord.Embed(title=f"__**{ctx.guild.name} Chrono Hunt Available [ALT] List:**__", color=0x03f8fc, timestamp=ctx.message.created_at)
    for document in cursor:
        m1 = str(document['name'])
        embed.add_field(name=f'> {m1}', value='\u200b', inline=True)
    await ctx.channel.send(embed=embed)


@bot.command(name='availablemain', help='Command for adding character to the Available list') # MUST HAVE AT LEAST 1 MEMBER.') # Call with !new name1 name2 name3')
async def availablemain(ctx, arg1):

    # Make sure none of these members are already in a squad
    if check_if_member_exists_in_squad(arg1):
        await ctx.channel.send(f'{arg1} already belongs to a squad. ')
        return

    # Make sure none of these members are already marked available
    if check_if_member_exists_in_available(arg1):
        await ctx.channel.send(f'{arg1} is already marked as available')
        return

    post = {"name": arg1.lower(), "is_main": 1}
    available_collection.insert_one(post)

    await ctx.channel.send(f'{arg1} has been added to the Available Mains List!')


@bot.command(name='availablealt', help='Command for adding character to the Available list') # MUST HAVE AT LEAST 1 MEMBER.') # Call with !new name1 name2 name3')
async def availablealt(ctx, arg1):

    # Make sure none of these members are already in a squad
    if check_if_member_exists_in_squad(arg1):
        await ctx.channel.send(f'{arg1} already belongs to a squad.')
        return

    # Make sure none of these members are already marked available
    if check_if_member_exists_in_available(arg1):
        await ctx.channel.send(f'{arg1} is already marked as available')
        return

    post = {"name": arg1.lower(), "is_main": 0}
    available_collection.insert_one(post)

    await ctx.channel.send(f'{arg1} has been added to the Available Alts List!')

bot.run(TOKEN)
# headers=['Squad Number', 'Member 1', 'Member 2', 'Member3']
# Need instructions for how to join Chrono hunt
# mark whether queued up or not
# if someone is added to a squad that is in the avialble lists, they should be auto removed from available
# would be nice to have a createsquads option that would take the available lists and make squads out of them
#
# rule 1 - don't accept the gear
# rule 2 - don't take gear unless you're told to
# rule 3 - don't enter on alt that isn't played at all (queue - yes, enter - no)
# rule 4 - queue main squads first
#
# I should add queue status to this, but also need everyone to add their alt lists here
# status to see if someone is in squad or available
#
# remove people from available