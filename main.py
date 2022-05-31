import discord
import os
import random
import asyncio
import datetime
import keep_alive
from discord.ext import commands
from replit import db

###################################################################################################

prefix = "g!"
intents = discord.Intents.default()
intents.members = True  # Subscribe to the privileged members intent.
bot = commands.Bot(command_prefix=prefix, intents=intents)
bot.remove_command('help')  # removes the default help command

###################################################################################################

@bot.event
async def on_ready():
    print('Bot online.')
    print('------')
    servers = list(bot.guilds)
    print(f"Connected on {str(len(servers))} servers:")
    print('\n'.join(server.name for server in servers))
    print('------')
    print('Logged in as (testing bot)')
    print(bot.user.name)
    print(bot.user.id)
    print('------')

###################################################################################################

def check_gank_time(userid):
    userstats = db[str(userid)].value
    if userstats["Time"] != "Indefinite" and userstats["Time"] != "None":
        # gets time till user leaves location
        time_now = datetime.datetime.now()
        initial_time = datetime.datetime.strptime(userstats["Time"][1], "%m/%d/%Y %H:%M:%S")
        delta_time = time_now - initial_time
        delta_time_seconds = delta_time.total_seconds()
        time_left_sec = int(userstats["Time"][0]) * 60 - delta_time_seconds  # in seconds
        # reset time, gankability, location if timer is over
        if time_left_sec <= 0:
            db[str(userid)]["Gankable"] = False
            db[str(userid)]["Location"] = "None"
            db[str(userid)]["Time"] = "None"
            db[str(userid)]["Ganked"] = []

"""
def check_target_time(userid):
    userstats = db[str(userid)].value
    targetid = str(userstats["Target"])
    targetstats = db[targetid].value
    if targetstats["Time"] != "Indefinite" and targetstats["Time"] != "None":
        # gets time till target leaves location
        time_now = datetime.datetime.now()
        initial_time = datetime.datetime.strptime(targetstats["Time"][1], "%m/%d/%Y %H:%M:%S")
        delta_time = time_now - initial_time
        delta_time_seconds = delta_time.total_seconds()
        time_left_sec = int(targetstats["Time"][0]) * 60 - delta_time_seconds  # in seconds
        # reset target
        if time_left_sec <= 0:
            db[str(userid)]["Target"] = "None"
"""  

###################################################################################################

@bot.command()
# help command
async def help(ctx, arg=""):
    if arg == "":
        help_embed = discord.Embed(
            title="Help Menu",
            description="noob"
        )
        help_embed.add_field(
            name="enroll",
            value="enroll in the gank program",
            inline=False)
        help_embed.add_field(
            name="profile",
            value="view your profile\n (shortcut - p)",
            inline=False)
        help_embed.add_field(
            name="location",
            value="set your location and time ur available for\n[Parameter: minutes]\n (shortcut - l)\n(eg. g!l 69, which sets your location for 69min)",
            inline=False)
        help_embed.add_field(
            name="ungank",
            value="stop yourself from being ganked\n (shortcut - u)",
            inline=False)
        help_embed.add_field(
            name="gank",
            value="view a list of possible targets\n[Parameter: target]\n (shortcut - g)",
            inline=False)
        help_embed.add_field(
            name="cancel",
            value="cancels your gank\n (shortcut - c)",
            inline=False)
        help_embed.add_field(
            name="map",
            value="view campus map\n (shortcut - m)",
            inline=False)
    await ctx.channel.send(embed=help_embed)


@bot.command()
# updates command
async def updates(ctx):
    update_embed = discord.Embed(
        title="Announcement",
        description="yes",
        color=discord.Color.blue())
    update_embed.add_field(
        name="Updates",
        value="- Location command has been changed for ease of use\n - Indefinite locations no longer exists to prevent false info\n - The cap for time at a location has been set to 24 hrs\n - Everyone has been unenrolled for this update")
    update_embed.set_footer(text="For feedback or suggestions, please spam this channel or ping **garade#7409**")
    await ctx.channel.send(embed=update_embed)


@bot.command()
# enroll command
async def enroll(ctx):
    # gets user id
    userid = ctx.message.author.id
    username = str(ctx.message.author)
    # checks if the user is already in database
    if str(userid) not in db.keys():
        userstats = {
            "Name": username,
            "Gankable": False,
            "Location": "None",
            "Status": "None",
            "Time": "None",
            "Target": "None",
            "Ganked": [],
            "History": {},
            "Extra": []
        }
        db[str(userid)] = userstats

        intro_embed = discord.Embed(
            title="Welcome, " + userstats["Name"],
            description="",
            color=discord.Color.blue())
        intro_embed.add_field(
            name="Info",
            value="The goal of this bot is to display gank availability and promote ganking")
        intro_embed.add_field(
            name="Consent",
            value="This program promotes **Affirmative Consent**, however we do not take responsibility for coincidental ganks ¯\_(ツ)_/¯")
        intro_embed.set_footer(text="use " + prefix + "help to learn more")
        await ctx.channel.send(embed=intro_embed)
    else:
        await ctx.channel.send("You have already enrolled")


@bot.command(aliases=['p'])
# profile info command
async def profile(ctx):
    # gets user id
    userid = ctx.message.author.id
    # checks if user is in database
    if str(userid) in db.keys():
        check_gank_time(userid)
        # get user info
        userstats = db[str(userid)].value
        avatar_url = ctx.message.author.avatar_url
        # make profile embed
        profile_embed = discord.Embed(title=userstats["Name"] + "'s Profile",
                                      description="sus",
                                      color=discord.Color.blue())
        profile_embed.set_thumbnail(url=avatar_url)
        profile_embed.add_field(
            name="Gankable?",
            value=str(userstats["Gankable"]),
            inline=False)
        profile_embed.add_field(
            name="Location",
            value=str(userstats["Location"]),
            inline=False)
        if userstats["Time"] == "Indefinite" or userstats["Time"] == "None":
            profile_embed.add_field(
                name="Location Timer",
                value=userstats["Time"],
                inline=False)
        else:
            # gets time till user leaves location
            time_now = datetime.datetime.now()
            initial_time = datetime.datetime.strptime(userstats["Time"][1], "%m/%d/%Y %H:%M:%S")
            delta_time = time_now - initial_time
            delta_time_seconds = delta_time.total_seconds()
            time_left_sec = int(userstats["Time"][0]) * 60 - delta_time_seconds  # in seconds
            time_left_min = divmod(time_left_sec, 60)
            time_left_hour = divmod(time_left_min[0], 60)
            time_left_final = str(round(time_left_hour[0])) + "hr " + str(round(time_left_hour[1])) + "min " + str(round(time_left_min[1])) + "s"
            
            profile_embed.add_field(
                name="Location Timer",
                value=time_left_final,
                inline=False)
        if userstats["Ganked"] != []:
            profile_embed.add_field(
                name="Ganked by",
                value=str(", ".join(userstats["Ganked"])),
                inline=False)
        else:
            profile_embed.add_field(
                name="Ganked by no one",
                value="L + no maidens",
                inline=False)
        
        await ctx.channel.send(embed=profile_embed)
    else:
        await ctx.channel.send("Use " + prefix + "enroll to begin")

"""
        if userstats["Target"] == "None":
            profile_embed.add_field(
                name="Target",
                value=str(userstats["Target"]),
                inline=False)
        else:
            print(userstats)
            check_gank_time(userstats["Target"])
            
            if db[str(userstats["Target"])]["Gankable"]:
                target = userstats["Target"]
                name = db[str(target)]["Name"]
                location = db[str(target)]["Location"]
                time = db[str(target)]["Time"]
                if time == "Indefinite" or time == "None":
                    time_available = "Indefinite"
                else:
                    # gets time till user leaves location
                    time_now = datetime.datetime.now()
                    initial_time = datetime.datetime.strptime(time[1], "%m/%d/%Y %H:%M:%S")
                    delta_time = time_now - initial_time
                    delta_time_seconds = delta_time.total_seconds()
                    time_left_sec = int(time[0]) * 60 - delta_time_seconds  # in seconds
                    time_left_min = divmod(time_left_sec, 60)
                    time_left_hour = divmod(time_left_min[0], 60)
                    time_available = str(round(time_left_hour[0])) + "hr " + str(round(time_left_hour[1])) + "min " + str(round(time_left_min[1])) + "s"
                profile_embed.add_field(
                    name="Target",
                    value="**- "+ name +" -**\n **Location:** " + str(location) + "\n**Available for:** " + time_available,
                    inline=False)
            else:
                db[str(userid)]["Target"] = "None"
                profile_embed.add_field(
                name="Target",
                value="None",
                inline=False)
"""
        


@bot.command(aliases=['l'])
# location check command
async def location(ctx, arg=""):
    # gets user id
    userid = ctx.message.author.id
    # checks if user is in database
    if str(userid) in db.keys():
        # ask for location
        location_embed = discord.Embed(
            title="Where are you right now?",
            description="Enter where you will be",
            color=discord.Color.purple()
        )
        await ctx.channel.send(embed=location_embed)
        # get user answer
        def check(m):
            return m.author == ctx.message.author and m.channel == ctx.channel
        try:
            msg = await bot.wait_for('message', timeout=10.0, check=check)
        except asyncio.TimeoutError:
            await ctx.channel.send(
                "*-- Command timeout: You were too slow --*"
            )
        else:
            # storing location
            location = msg.content
            db[str(userid)]["Location"] = location
            db[str(userid)]["Gankable"] = True            
            # receipt ig
            receipt_embed = discord.Embed(
                title="Details confirmed",
                description="",
                color=discord.Color.green()
            )
            receipt_embed.add_field(
                name="Your location has been set to",
                value=db[str(userid)]["Location"],
                inline=False
            )
            # storing + displaying time
            if arg == "":
                # ask for time
                time_embed = discord.Embed(
                    title="How long will you be there?",
                    description="Enter time in minutes [Max 1440 min]",
                    color=discord.Color.purple()
                )
                await ctx.channel.send(embed=time_embed)
                # get user answer
                def check(m):
                    return m.author == ctx.message.author and m.channel == ctx.channel
                try:
                    msg = await bot.wait_for('message', timeout=10.0, check=check)
                except asyncio.TimeoutError:
                    await ctx.channel.send(
                        "*-- Command timeout: You were too slow --*"
                    )
                else:
                    # storing time
                    time = msg.content
                    if time.isnumeric():
                        # max time to 24hr
                        if int(time) > 1440:
                            time = "1440"
                        time_now = datetime.datetime.now()
                        time_now = time_now.strftime('%m/%d/%Y %H:%M:%S')
                        # sets time to a tuple with timer and initial time
                        db[str(userid)]["Time"] = (int(time), time_now)
                        receipt_embed.add_field(
                            name="Location timer has been set to",
                            value=str(db[str(userid)]["Time"][0])+" minutes",
                            inline=False
                        )
                    else:
                        db[str(userid)]["Time"] = "Indefinite"
                        receipt_embed.add_field(
                            name="Sus",
                            value="The time you set is invalid, please enter an integer of minutes\n Location will be reset in 1 minute",
                            inline=False
                        )
            elif arg.isnumeric():
                # max time to 24hr
                if int(arg) > 1440:
                    arg = "1440"
                time_now = datetime.datetime.now()
                time_now = time_now.strftime('%m/%d/%Y %H:%M:%S')
                # sets time to a tuple with timer and initial time
                db[str(userid)]["Time"] = (int(arg), time_now)
                receipt_embed.add_field(
                    name="Location timer has been set to",
                    value=str(db[str(userid)]["Time"][0])+" minutes",
                    inline=False
                )
            else:
                db[str(userid)]["Time"] = "Indefinite"
                receipt_embed.add_field(
                    name="Sus",
                    value="The time you set is invalid, please enter an integer of minutes\n Location will be reset in 1 minute",
                    inline=False
                )
            receipt_embed.set_footer(text="you are now gankable 😉")
            await ctx.channel.send(embed=receipt_embed)
    else:
        await ctx.channel.send("Use " + prefix + "enroll to begin")


@bot.command(aliases=['u'])
# ungank command
async def ungank(ctx):
    # gets user id
    userid = ctx.message.author.id
    # checks if user is in database
    if str(userid) in db.keys():
        # not gankable anymore + location/time reset
        db[str(userid)]["Gankable"] = False
        db[str(userid)]["Location"] = "None"
        db[str(userid)]["Time"] = "None"
        db[str(userid)]["Ganked"] = []
        # gankability message
        gankable_embed = discord.Embed(
            title="Ungankable",
            description="You can't be ganked anymore and your location has been cleared!",
            color=discord.Color.green()
        )
        await ctx.channel.send(embed=gankable_embed)
    else:
        await ctx.channel.send("Use " + prefix + "enroll to begin")


@bot.command(aliases=['g'])
# gank check command
async def gank(ctx, *, arg: discord.User = None):
    # gets user id
    userid = ctx.message.author.id
    # checks if user is in database
    if str(userid) in db.keys():
        if arg == None:
            player_list = db.keys()
            server_player_dict = {}
            for i in player_list:
                check_gank_time(str(i))
                # if target is in the server and is gankable
                if ctx.guild.get_member(int(i)) is not None and db[str(i)]["Gankable"]:
                    name = db[str(i)]["Name"]
                    location = db[str(i)]["Location"]
                    time = db[str(i)]["Time"]
                    server_player_dict[i] = [location, name, time]
            if server_player_dict == {}:
                description = "no one is gankable rn 😔"
            else:
                description = "noobs who can be ganked"
            # make embed with gank list
            server_players = discord.Embed(
                title="Gank List",
                description=description,
                color=discord.Color.blue()
            )
            for user in server_player_dict:
                if server_player_dict[user][2] == "Indefinite" or server_player_dict[user][2] == "None":
                    time_available = "Indefinite"
                else:
                    # gets time till user leaves location
                    time_now = datetime.datetime.now()
                    initial_time = datetime.datetime.strptime(server_player_dict[user][2][1], "%m/%d/%Y %H:%M:%S")
                    delta_time = time_now - initial_time
                    delta_time_seconds = delta_time.total_seconds()
                    time_left_sec = int(server_player_dict[user][2][0]) * 60 - delta_time_seconds  # in seconds
                    time_left_min = divmod(time_left_sec, 60)
                    time_left_hour = divmod(time_left_min[0], 60)
                    time_available = str(round(time_left_hour[0])) + "hr " + str(round(time_left_hour[1])) + "min " + str(round(time_left_min[1])) + "s"
                gankers = db[user]["Ganked"]
                if gankers == []:
                    gankers = ""
                else:
                    gankers = "**Ganked by:** " + ", ".join(gankers) + "\n"
                server_players.add_field(
                    name=server_player_dict[user][1],
                    value="**Location:** " + str(server_player_dict[user][0]) + "\n**Available for:** " + time_available + "\n"+gankers,
                    inline=False
                )
            await ctx.channel.send(embed=server_players)
        
        else:
            target = arg
            if str(target.id) in db.keys() and ctx.guild.get_member(int(target.id)) is not None:
                check_gank_time(target.id)
                # if target is in the server and is gankable
                if db[str(target.id)]["Gankable"]:
                    location = db[str(target.id)]["Location"]
                    name = db[str(target.id)]["Name"]
                    time = db[str(target.id)]["Time"]
                    db[str(userid)]["Target"] = target.id
                    # add ganker to target's ganked list
                    ganked_list = db[str(target.id)]["Ganked"]
                    ganked_list.append(str(db[str(userid)]["Name"]))
                    db[str(target.id)]["Ganked"] = ganked_list
                    if time == "Indefinite" or time == "None":
                        time_available = "Indefinite"
                    else:
                        # gets time till user leaves location
                        time_now = datetime.datetime.now()
                        initial_time = datetime.datetime.strptime(time[1], "%m/%d/%Y %H:%M:%S")
                        delta_time = time_now - initial_time
                        delta_time_seconds = delta_time.total_seconds()
                        time_left_sec = int(time[0]) * 60 - delta_time_seconds  # in seconds
                        time_left_min = divmod(time_left_sec, 60)
                        time_left_hour = divmod(time_left_min[0], 60)
                        time_available = str(round(time_left_hour[0])) + "hr " + str(round(time_left_hour[1])) + "min " + str(round(time_left_min[1])) + "s"
        
                    target_embed = discord.Embed(
                        title="Your target has been set to "+name,
                        description="**Location:** " + str(location) + "\n**Available for:** " + time_available,
                        color=discord.Color.red()
                    )
                    await ctx.channel.send(embed=target_embed)
                else:
                    await ctx.channel.send("*-- Target cannot be ganked --*")
                
                    
                
            else:
                await ctx.channel.send("*-- This user is not enrolled --*")
    else:
        await ctx.channel.send("Use " + prefix + "enroll to begin")


@bot.command(aliases=['c'])
# cancel target command
async def cancel(ctx):
    # gets user id
    userid = ctx.message.author.id
    # checks if user is in database
    if str(userid) in db.keys():
        if db[str(userid)]["Target"] != "None":
            targetid = str(db[str(userid)]["Target"])
            ganked_list = db[targetid]["Ganked"]
            ganked_list.remove(str(db[str(userid)]["Name"]))
            db[targetid]["Ganked"] = ganked_list
            cancel_embed = discord.Embed(
                title="Cancelled",
                description="You are no longer ganking anyone",
                color=discord.Color.blue()
            )
            await ctx.channel.send(embed=cancel_embed)
        else:
            await ctx.channel.send("*-- You do not have a target --*")
    else:
        await ctx.channel.send("Use " + prefix + "enroll to begin")


@bot.command(aliases=['m'])
# map command
async def map(ctx):
    file = discord.File("./campus-map.png", filename="map.png")
    embed = discord.Embed(title="Campus Map", color=discord.Color.blue())
    embed.set_image(url="attachment://map.png")
    await ctx.channel.send(file=file, embed=embed)
        
###################################################################################################

@bot.command()
# TESTING delete user key
async def unenroll(ctx):
    # gets user id
    userid = ctx.message.author.id
    del db[str(userid)]
    db.clear()
    await ctx.channel.send("progress deleted")


keep_alive.keep_alive()

bot.run(os.environ['TOKEN'])