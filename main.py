import discord, random, asyncio
from aiohttp import ClientSession
from discord.ext import commands
from random import randint
from discord.utils import get
from discord import Member
from discord.ext.commands import has_permissions, MissingPermissions
from keep_alive import keep_alive
import json
import os
import youtube_dl
import requests
import io
import aiohttp

filtered_words = ["Replace This","Replace this"]

client = commands.Bot(command_prefix=">")
#hello
@client.command()
async def hello(ctx):
    await ctx.send(f"Whats up? {ctx.author.mention}")

#dog
@client.command()
async def dog(ctx):
   async with aiohttp.ClientSession() as session:
      request = await session.get('https://some-random-api.ml/img/dog')
      dogjson = await request.json()
      request2 = await session.get('https://some-random-api.ml/facts/dog')
      factjson = await request2.json()

   embed = discord.Embed(title="Doggo!", color=discord.Color.purple())
   embed.set_image(url=dogjson['link'])
   embed.set_footer(text=factjson['fact'])
   await ctx.send(embed=embed)
#cat
@client.command()
async def cat(ctx):
   async with aiohttp.ClientSession() as session:
      request = await session.get('https://some-random-api.ml/img/cat')
      dogjson = await request.json()
      request2 = await session.get('https://some-random-api.ml/facts/cat')
      factjson = await request2.json()

   embed = discord.Embed(title="Cats!", color=discord.Color.purple())
   embed.set_image(url=dogjson['link'])
   embed.set_footer(text=factjson['fact'])
   await ctx.send(embed=embed)


#startup
@client.event
async def on_ready():
    await client.change_presence(activity=discord.Game('>help'))
    print("------------------------------------\n           Bot is Running:  \n------------------------------------")

#New Member Joining
@client.event
async def on_member_join(member):
    role = discord.utils.get(member.guild.roles, name = "Member")
    await member.add_roles(role)

#ping
@client.command()
async def ping(ctx):
    await ctx.send(f'Bot Response Time: {round(client.latency * 1000)}ms')


#Kick
@client.command(name="kick", pass_context = True)
@commands.has_permissions(kick_members=True)
async def kick(ctx, member: discord.Member):
    await member.kick()
    await ctx.send("User " + member.display_name + " has been kicked")
	
#Errors
@client.event
async def on_command_error(ctx, error):
    if isinstance(error, commands.MissingRequiredArgument):
        await ctx.send('Please pass in all requirements :rolling_eyes:.')
    if isinstance(error, commands.MissingPermissions):
        await ctx.send("You dont have all the Perms :angry:")
    #if isinstance(error, discord.ext.commands.CommandInvokeError):
        #await ctx.send("I dont have all the Perms to do that :angry:")
#automod
@client.event
async def on_message(msg):
  for word in filtered_words:
    if word in msg.content:
      await msg.delete()

  await client.process_commands(msg)

#Ban
@client.command(name="ban", pass_context=True)
@commands.has_permissions(ban_members = True)
async def ban(ctx, member : discord.Member, *, reason =None):
    await member.ban(reason=reason)
    await ctx.send("User " + member.display_name + " has been Banned")

#Unban
@client.command()
@commands.has_permissions(ban_members = True)
async def unban(ctx, user: discord.User):
    guild = ctx.guild
    mbed = discord.Embed(
        title = "Success!",
        description = f"{user} has been successfully unbanned"
    )
    if ctx.author.guild_permissions.ban_members:
        await ctx.send(embed=mbed)
        await guild.unban(user=user)

#mute
@client.command()
@commands.has_permissions(manage_messages=True)
async def mute(ctx, member: discord.Member, *, reason=None):
    guild = ctx.guild
    mutedRole = discord.utils.get(guild.roles, name="Muted")

    if not mutedRole:
        mutedRole = await guild.create_role(name="Muted")

        for channel in guild.channels:
            await channel.set_permissions(mutedRole, speak=False, send_messages=False, read_message_history=True, read_messages=False)
    embed = discord.Embed(title="Muted", description=f"{member.mention} was muted ", colour=discord.Colour.light_gray())
    embed.add_field(name="reason:", value=reason, inline=False)
    await ctx.send(embed=embed)
    await member.add_roles(mutedRole, reason=reason)
    await member.send(f" You have been muted from: {guild.name} reason: {reason}")

#unmute
@client.command()
@commands.has_permissions(manage_messages=True)
async def unmute(ctx, member: discord.Member):
   mutedRole = discord.utils.get(ctx.guild.roles, name="Muted")

   await member.remove_roles(mutedRole)
   await member.send(f" You have unmuted from: - {ctx.guild.name}")
   embed = discord.Embed(title="Unmuted", description=f" unmuted-{member.mention}",colour=discord.Colour.light_gray())
   await ctx.send(embed=embed)

#clear
@client.command()
@commands.has_permissions(manage_messages=True)
async def clear(ctx, amount=5):
	await ctx.channel.purge(limit=amount)
#8ball
@client.command(aliases=['8ball'])
async def _8ball(ctx, *, question):
  responses = [
  discord.Embed(title='It is certain.'),
  discord.Embed(title='It is decidedly so.'),
  discord.Embed(title='Without a doubt.'),
  discord.Embed(title='Yes - definitely.'),
  discord.Embed(title='You may rely on it.'),
  discord.Embed(title='Most likely.'),
  discord.Embed(title='Outlook good.'),
  discord.Embed(title='Yes.'),
  discord.Embed(title='Signs point to yes.'),
  discord.Embed(title='Reply hazy, try again.'),
  discord.Embed(title='Ask again later.'),
  discord.Embed(title='Better not tell you now.'),
  discord.Embed(title='Cannot predict now.'),
  discord.Embed(title='Concentrate and ask again.'),
  discord.Embed(title="Don't count on it."),
  discord.Embed(title='My reply is no.'),
  discord.Embed(title='My sources say no.'),
  discord.Embed(title='Outlook not very good.'),
  discord.Embed(title='Very doubtful.')
    ]
  responses = random.choice(responses)
  await ctx.send(content=f'Question: {question}\nAnswer:', embed=responses)

#servercount
@client.command(pass_context = True)
async def servercount(ctx):
  await ctx.send(f"I'm in {len(client.guilds)} servers!") 
#make role
@client.command(aliases=['make_role'])
@commands.has_permissions(manage_roles=True) 
async def create_role(ctx, *, name):
	guild = ctx.guild
	await guild.create_role(name=name)
	await ctx.send(f'Role `{name}` has been created')

  #delete role
@client.command(name="delete_role", pass_context=True)
async def delete_role(ctx, role_name):
    role_object = discord.utils.get(ctx.message.guild.roles, name=role_name)
    await role_object.delete()
    
keep_alive()
client.run("Token")

