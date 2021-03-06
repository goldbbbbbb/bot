# IMPORT DISCORD.PY. ALLOWS ACCESS TO DISCORD'S API.
import discord
from discord.ext import commands

#prefix of the commands in server.
bot = discord.ext.commands.Bot(command_prefix = "!")

channels = {}
messages = {}

#Confirm message when bot succesfully run.
@bot.event
async def on_ready():
  channels["command"] = bot.get_channel(817674249699459072)
  channels["table"] = bot.get_channel(817829173069348884)

  messages["table"] = await channels["table"].fetch_message(817834334365941761)

  print(f'佩可機器人準備完成!')

#BookBoss !book

class KnifeRequest:
  def __init__(self, username, damage, notice):
    self.username = username
    self.damage = damage
    self.notice = notice
  
  def __repr__(self):
    return f'{self.username}({self.damage}, {self.notice})'

# Requests for each boss
boss_numbers = ['補償', '一王', '二王', '三王', '四王', '五王']
knife_requests = [[] for _ in boss_numbers]

@bot.command()
async def book(ctx, boss, damage, notice):
  msg = ''

  try:
    boss = int(boss)
    msg = f'{ctx.author.mention} 預約 {boss_numbers[boss]} , 傷害: {damage}, 備注: {notice}'
    #sort the user input into different list base on value of variable boss.
    knife_requests[boss].append(KnifeRequest(ctx.author.display_name, damage, notice))
  except:
    msg = '請按照 !book [幾王] [傷害] [備注] 的方式報刀'

  await ctx.send(msg)
  await update_table()

#CancelBooking !unbook (not finished yet)
@bot.command()
async def unbook(ctx, boss):
  def filter_for_non_author(knife_request):
    return ctx.author.display_name != knife_request.username
  knife_requests[int(boss)] = list(filter(filter_for_non_author, knife_requests[int(boss)]))
  await ctx.send(f'{ctx.author.mention} 已取消 {boss} 王 的報刀。')
  await update_table()

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

async def update_table():
  #Show the nickname of user, instead of mention the user.
  #Output the table
  table = '```'
  for i in range(len(boss_numbers)):

    knife_requests_formatted = ''
    for request in knife_requests[i]:
      knife_requests_formatted += f'{request}, '

    table += f'{boss_numbers[i]}: {knife_requests_formatted}\n'
  table += '```'
  await messages["table"].edit(content=table)

