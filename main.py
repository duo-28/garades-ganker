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
            "Location": ["None", "None"],
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
            value="The goal of this bot is to display gank availability"
        )
        intro_embed.set_footer(text="use " + prefix + "help to learn more")
        await ctx.channel.send(embed=intro_embed)
    else:
        await ctx.channel.send("You have already enrolled")


@bot.command()
# profile info command
async def profile(ctx):
    # gets user id
    userid = ctx.message.author.id
    # checks if user is in database
    if str(userid) in db.keys():
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
            name="Building | Room",
            value=str(userstats["Location"][0]) + " | " + str(userstats["Location"][1]),
            inline=False)
        profile_embed.add_field(
            name="Target",
            value=str(userstats["Target"]),
            inline=False)
        await ctx.channel.send(embed=profile_embed)
    else:
        await ctx.channel.send("Use " + prefix + "enroll to begin")


@bot.command()
# toggle gankable info command
async def gankable(ctx):
    # gets user id
    userid = ctx.message.author.id
    # checks if user is in database
    if str(userid) in db.keys():
        # get user info
        userstats = db[str(userid)].value
        # status message
        status_message = ""
        # boolean switch
        if userstats["Gankable"]:
            db[str(userid)]["Gankable"] = False
            status_message = "Not Gankable"
        else:
            db[str(userid)]["Gankable"] = True
            status_message = "Gankable"
        # toggled gankability message
        gankable_embed = discord.Embed(
            title="Gankable?",
            description="Your status has been toggled to **"+status_message+"**",
            color=discord.Color.blue()
        )
        await ctx.channel.send(embed=gankable_embed)        
    else:
        await ctx.channel.send("Use " + prefix + "enroll to begin")


@bot.command()
# gank check command
async def gank(ctx):
    # gets user id
    userid = ctx.message.author.id
    # checks if user is in database
    if str(userid) in db.keys():
        player_list = db.keys()
        server_player_dict = {}
        for i in player_list:
            if ctx.guild.get_member(int(i)) is not None and db[str(i)]["Gankable"]:
                name = db[str(i)]["Name"]
                location = db[str(i)]["Location"]
                server_player_dict[i] = [location, name]
        # make embed with gank list
        server_players = discord.Embed(
            title="Gank List",
            description="noobs who can be ganked",
            color=discord.Color.blue()
        )
        for user in server_player_dict:
            server_players.add_field(
                name=server_player_dict[user][1],
                value="Location: " + str(server_player_dict[user][0][0]) + " | " + str(server_player_dict[user][0][1]),
                inline=False
            )
        await ctx.channel.send(embed=server_players)
    else:
        await ctx.channel.send("Use " + prefix + "enroll to begin")

###################################################################################################

@bot.command()
# TESTING delete user key
async def delkey(ctx):
    # gets user id
    userid = ctx.message.author.id
    del db[str(userid)]
    await ctx.channel.send("progress deleted")


keep_alive.keep_alive()

bot.run(os.environ['TOKEN'])