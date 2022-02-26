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
            value="set your location and time ur available for so others can gank u\n[Parameter: minutes]\n (shortcut - l)",
            inline=False)
        help_embed.add_field(
            name="ungank",
            value="stop yourself from being ganked\n (shortcut - u)",
            inline=False)
        help_embed.add_field(
            name="gank",
            value="view a list of possible targets\n (shortcut - g)",
            inline=False)
    await ctx.channel.send(embed=help_embed)


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
            "History": {},
            "Extra": []
        }
        db[userid] = userstats

        intro_embed = discord.Embed(
            title="Welcome, " + userstats["Name"],
            description="",
            color=discord.Color.blue())
        intro_embed.add_field(
            name="Info",
            value="The goal of this bot is to display gank availability")
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
        profile_embed.add_field(
            name="Target",
            value=str(userstats["Target"]),
            inline=False)
        await ctx.channel.send(embed=profile_embed)
    else:
        await ctx.channel.send("Use " + prefix + "enroll to begin")


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
            description="suspicious",
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
                db[str(userid)]["Time"] = "Indefinite"
                receipt_embed.add_field(
                    name="Location timer has been set to",
                    value="Indefinite",
                    inline=False
                )
            elif arg.isnumeric():
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
                    value="The time you set is invalid, please enter an integer of minutes",
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
async def gank(ctx, arg=""):
    # gets user id
    userid = ctx.message.author.id
    # checks if user is in database
    if str(userid) in db.keys():
        player_list = db.keys()
        server_player_dict = {}
        for i in player_list:
            check_gank_time(str(i))
            if ctx.guild.get_member(int(i)) is not None and db[str(i)]["Gankable"]:
                name = db[str(i)]["Name"]
                location = db[str(i)]["Location"]
                time = db[str(i)]["Time"]
                server_player_dict[i] = [location, name, time]
        # make embed with gank list
        server_players = discord.Embed(
            title="Gank List",
            description="noobs who can be ganked",
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

            server_players.add_field(
                name=server_player_dict[user][1],
                value="**Location:** " + str(server_player_dict[user][0]) + "\n**Available for:** " + time_available,
                inline=False
            )
        await ctx.channel.send(embed=server_players)
    else:
        await ctx.channel.send("Use " + prefix + "enroll to begin")

###################################################################################################

@bot.command()
# TESTING delete user key
async def unenroll(ctx):
    # gets user id
    userid = ctx.message.author.id
    del db[str(userid)]
    await ctx.channel.send("progress deleted")


keep_alive.keep_alive()

bot.run(os.environ['TOKEN'])