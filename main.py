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

    if not(available_collection.count_documents({'is_main': 1})):
        cursor = available_collection.find({'is_main': 1})
        embed = discord.Embed(title=f"__**{ctx.guild.name} Chrono Hunt Available [MAIN] List:**__", color=0x03f8fc, timestamp=ctx.message.created_at)
        for document in cursor:
            m1 = str(document['name'])
            embed.add_field(name=f'> {m1}', value='\u200b', inline=True)
        await ctx.channel.send(embed=embed)

    if not (available_collection.count_documents({'is_main': 0})):
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


@bot.command(name='rules', help='Command for listing the rules of the hunt') # MUST HAVE AT LEAST 1 MEMBER.') # Call with !new name1 name2 name3')
async def rules(ctx):

    embed = discord.Embed(title=f"__**{ctx.guild.name} Chrono Hunt Rules List:**__", color=0x03f8fc, timestamp=ctx.message.created_at)
    embed.add_field(name=f'1. DO NOT talk about the hunt to anyone, anywhere, unless it is in Obsolete TS or Discord', value='\u200b', inline=False)
    embed.add_field(name=f'2. DO NOT accept the hunt gear', value='\u200b', inline=False)
    embed.add_field(name=f'3. If a Hunt leader tells you to, you may take the gear', value='\u200b', inline=False)
    embed.add_field(name=f'4. MAIN Squads (as indicated by the !squads command) should be queued before any ALT squads', value='\u200b', inline=False)
    embed.add_field(name=f'5. If your ALT squad is made up of characters that do not get played or you have no plans for end game gear, DO NOT ENTER the hunt on their squads', value='\u200b', inline=False)
    embed.add_field(name=f'> TLDR: For ALT squads (queue - yes, enter - no)', value='\u200b', inline=True)
    embed.add_field(name=f'6. DO NOT refine your crown of apex when you get it, until Drago organizes a time for us to all +12 it together!', value='\u200b', inline=False)
    await ctx.channel.send(embed=embed)


@bot.command(name='howtohunt', help='Command for explaining Chrono Hunt')# MUST HAVE AT LEAST 1 MEMBER.') # Call with !new name1 name2 name3')
async def howtohunt(ctx):
    print("How to Hunt")
    embed = discord.Embed(title=f"__**{ctx.guild.name}: How to Chrono Hunt:**__", color=0x03f8fc, timestamp=ctx.message.created_at)

    embed.add_field(name=f'Chrono Hunt (aka The Hunt) is an instance event that requires 99 characters to be in the queue to trigger so that we can enter.', value='\u200b', inline=False)
    embed.add_field(name=f'To prepare for The Hunt, go to your homestead, or your squad leaders homestead.' , value='\u200b', inline=False)
    embed.add_field(name=f'If you have a set MAIN squad, squad up with them, and let The Hunt leaders know that you are ready' , value='\u200b', inline=False)
    embed.add_field(name=f'If you have an ALT, either squad with your own alts and add the squad to the bot, or mark yourself as an available alt using the bot', value='\u200b', inline=False)
    embed.add_field(name=f'If your main needs a squad, mark yourself as an available main, and we will find you a squad.', value='\u200b', inline=False)
    embed.add_field(name=f'We have 8 set squads that we plan to run with every week, meaning 24 slots for mains to get the Chrono Flux every week (at least that\'s the plan)', value='\u200b', inline=False)
    embed.add_field(name=f'We use a rotational system to ensure that everyone is getting the same number of rewards (every 8 rounds, everyone will have the same rewards), this ensures a fair process to everyone in order to get the gear that can be made with the chrono flux.', value='\u200b', inline=False)
    embed.add_field(name=f'When it is time to queue up (The Chrono Hunt leader will let you know when), ONLY THE SQUAD LEADERS may leave the homestead and go to the NPC at the center of Neverfall to queue up for The Hunt', value='\u200b', inline=False)
    embed.add_field(name=f'Squad leads, please make sure your team is all present, and let them know when you queue them up, they will have 30 seconds for both of them to accept, or you dont get added to the queue.', value='\u200b', inline=False)
    embed.add_field(name=f'Once queued up, you will have a golden compass next to your toolbar (usually in the bottom right of the screen) the leader should go back into their homestead.', value='\u200b', inline=False)
    embed.add_field(name=f'We do not want to crowd around the NPC because we dont want other factions to know we are doing the event, and then we cant ensure that our members get their rewards', value='\u200b', inline=False)
    embed.add_field(name=f'When all 99 characters have entered the queue, the queue will "pop" and it will give you 60 seconds to enter.', value='\u200b', inline=False)
    embed.add_field(name=f'DO NOT ENTER ON YOUR ALTS, ONLY ENTER ON YOUR MAINS', value='\u200b', inline=False)
    embed.add_field(name=f'Once inside, teleport to the K in Kerrod (usually found by all the flags on the map, but it is in the center a bit to the left', value='\u200b', inline=False)
    embed.add_field(name=f'Once we get teleported (2-3 min after entering), we will kill any alts that went in (we try to keep this to a minimum so the process is fast)', value='\u200b', inline=False)
    embed.add_field(name=f'After we kill all the alts, we will kill the "main" alts, which plan to be geared up to endgame.', value='\u200b', inline=False)
    embed.add_field(name=f'Then we will kill squads in the order of the rotation until the last squad remains.', value='\u200b', inline=False)
    embed.add_field(name=f'Once your squad dies, please click the "leave" button on the menu that pops up, and go wait in your homestead.', value='\u200b', inline=False)
    embed.add_field(name=f'After we reach the last squad and everyone leaves, you will receive mail with your reward.', value='\u200b', inline=False)
    embed.add_field(name=f'We ask that unless you are redeeming the chrono sand, please keep the rewards in the bank so that sins can check your inventory and report that we are doing The Hunt (we wanna keep this on the DL/QT)', value='\u200b', inline=False)
    embed.add_field(name=f'There is a 10 minute break to mingle, use the restroom, get snacks, etc in between runs; this is because the alts that didnt enter will have a 10 minute timer before they can requeue', value='\u200b', inline=False)
    embed.add_field(name=f'If you got this far, thank you for reading the rule of The Hunt', value='\u200b', inline=False)

    await ctx.channel.send(embed=embed)

bot.run(TOKEN)
# mark whether queued up or not
# if someone is added to a squad that is in the avialble lists, they should be auto removed from available
# would be nice to have a createsquads option that would take the available lists and make squads out of them
#
# I should add queue status to this, but also need everyone to add their alt lists here
# status to see if someone is in squad or available
#
# Keep track of rotations
# remove people from available
# keep track of late comers