# IMPORT DISCORD.PY. ALLOWS ACCESS TO DISCORD'S API.
import discord
from discord.ext import commands

from ready import *
from booking import *

#prefix of the commands in server.
bot = discord.ext.commands.Bot(command_prefix = "!")

#Confirm message when bot succesfully run.
@bot.event
async def on_ready():
	welcome()

#BookBoss !book

#List for store the variable boss,damage and notice.
booked1_members = []
booked2_members = []
booked3_members = []
booked4_members = []
booked5_members = []

damage1_members = []
damage2_members = []
damage3_members = []
damage4_members = []
damage5_members = []

notice1_members = []
notice2_members = []
notice3_members = []
notice4_members = []
notice5_members = []


@bot.command()
async def book(ctx, boss, damage, notice):

  bossi = int(boss)

  msg = ''
  if valid_book_input(boss, damage):
    msg = f'{ctx.author.mention} 預約 {boss} 王, 傷害: {damage}, 備注: {notice}'
  else:
    msg = '請按照 !book [幾王] [傷害] [備注] 的方式報刀'
  await ctx.send(msg)

  #sort the user input into different list base on value of variable boss.
  if bossi == 1:
    booked1_members.append(ctx.author)
    damage1_members.append(damage)
    notice1_members.append(notice)
  elif bossi == 2:
    booked2_members.append(ctx.author)
    damage2_members.append(damage)
    notice2_members.append(notice)
  elif bossi == 3:
    booked3_members.append(ctx.author)
    damage3_members.append(damage)
    notice3_members.append(notice)
  elif bossi == 4:
    booked4_members.append(ctx.author)
    damage4_members.append(damage)
    notice4_members.append(notice)
  else:
    booked5_members.append(ctx.author)
    damage5_members.append(damage)
    notice5_members.append(notice)

#CancelBooking !unbook (not finished yet)
@bot.command()
async def unbook(ctx, boss):
	await ctx.send(f'{ctx.author.mention} 已取消 {boss} 王 的報刀。')

#SeekHelp !sos
sos_users = []
@bot.command()
async def sos(ctx):
  sos_users.append(ctx.author)
  await ctx.send(f'{ctx.author.mention} 掛樹了，有人能幫幫他嗎？現時樹上人數: {len(sos_users)}')

#Nextboss !next
@bot.command()
async def next(ctx):
  # Show current/next boss info
  pass
  # Tag all sos users
  user_names = ""
  for user in sos_users:
    user_names += user.mention + ' '
  await ctx.send(f'{user_names} 已經到下一隻王了，可以下樹囉。')
  sos_users.clear()

#ShowTable !table
@bot.command()
async def table(ctx):

  #Get namelist of member which booked 1-5 boss.
  member1_names = ""
  member2_names = ""
  member3_names = ""
  member4_names = ""
  member5_names = ""

  #Show the nickname of user, instead of mention the user.
  for member1 in booked1_members:
    member1_names += member1.display_name + ' '

  for member2 in booked2_members:
    member2_names += member2.display_name + ' '

  for member3 in booked3_members:
    member3_names += member3.display_name + ' '

  for member4 in booked4_members:
    member4_names += member4.display_name + ' '

  for member5 in booked5_members:
    member5_names += member5.display_name + ' '

  #Output the table(draft)
  await ctx.send(f'``一王：{member1_names}/{damage1_members}/{notice1_members}\n二王：{member2_names}/{damage2_members}/{notice2_members}\n三王：{member3_names}/{damage3_members}/{notice3_members}\n四王：{member4_names}/{damage4_members}/{notice4_members}\n五王：{member5_names}/{damage5_members}/{notice5_members}``')
