# IMPORT DISCORD.PY. ALLOWS ACCESS TO DISCORD'S API.
# IMPORT GSPREAD, ALLOWS ACCESS TO READ GOOGLE SHEETS.
import discord
from discord.ext import commands
import time
import gspread
from oauth2client.service_account import ServiceAccountCredentials

#setting to read the data of sheet which we assigned

scope = ['https://spreadsheets.google.com/feeds','https://www.googleapis.com/auth/drive']
creds = ServiceAccountCredentials.from_json_keyfile_name('pekodcbot.json',scope)
client = gspread.authorize(creds)
sheet = client.open('21/3月出刀紀錄').sheet1

#prefix of the commands in server.
bot = discord.ext.commands.Bot(command_prefix = "!")

channels = {}
messages = {}

def is_in_channel(ctx, channel_name):
  return ctx.channel.name == channels[channel_name].name

#Confirm message when bot succesfully run.
@bot.event
async def on_ready():

  #817674249699459072 掛樹頻->報刀頻 771259390241669132
  #817829173069348884 刀表->報刀表 818898908407267338
  #818157150232248341 admin->幹部頻 817851835955281930
  #817834334365941761 刀表頻msg->報刀表msg 818901761548746752
  channels["command"] = bot.get_channel(771259390241669132)
  channels["table"] = bot.get_channel(818898908407267338)
  channels["admin"] = bot.get_channel(817851835955281930)

  messages["table"] = await channels["table"].fetch_message(818901761548746752)

  await update_table()
  print(f'佩可機器人準備完成!')

@bot.command()
async def setchannel(ctx, channel_name, channel_mention):
  if not is_in_channel(ctx, "admin"):
    return

  channels[channel_name] = await bot.fetch_channel(channel_mention[2:-1])
  await ctx.send(f'佩可機器人已將 {channel_name} 頻道設為 {channels[channel_name].mention}')

@bot.command()
async def showchannels(ctx):
  if not is_in_channel(ctx, "admin"):
    return
  
  msg = ''
  for name, channel in channels.items():
    msg += f'{name}: {channel.mention}\n'
  await ctx.send(msg)

#Check rest of the num of knife !num
@bot.command()
async def num(ctx):
  if not is_in_channel(ctx, "command"):
    return
  #get the data in (38,17) of first sheet of the google sheets we assigned.
  result = sheet.cell(38,17).value
  await ctx.send(f'目前仍有 {result} 刀未出。')

#BookBoss !book

class KnifeRequest:
  def __init__(self, user, numknife, damage, notice):
    self.user = user
    self.numknife = numknife
    self.damage = damage
    self.notice = notice
  
  def __repr__(self):
    return f'{self.user.display_name}(第{self.numknife}刀/{self.damage}/{self.notice})'

# Requests for each boss
boss_numbers = ['補償', '一王', '二王', '三王', '四王', '五王']
knife_requests = [[] for _ in boss_numbers]

@bot.command()
async def book(ctx, boss, numknife, damage, notice="無"):
  if not is_in_channel(ctx, "command"):
    return

  msg = ''

  try:
    boss = int(boss)
    numknife = int(numknife)
    if numknife > 0 and numknife < 4:
      msg = f'{ctx.author.mention} 預約 {boss_numbers[boss]} , 刀數: {numknife}, 傷害: {damage}, 備注: {notice}'
      #sort the user input into different list base on value of variable boss.
      knife_requests[boss].append(KnifeRequest(ctx.author, numknife, damage, notice))
    else:
      msg = '請按照 !book [幾王] [第幾刀] [傷害] [備注] 的方式報刀'
  except:
    msg = '請按照 !book [幾王] [第幾刀] [傷害] [備注] 的方式報刀'


  await ctx.send(msg)
  await update_table()

#CancelBooking !unbook
@bot.command()
async def unbook(ctx, numknife):
  if not is_in_channel(ctx, "command"):
    return

  def filter_function(knife_request):
    if ctx.author.display_name != knife_request.user.display_name:
      return True # All non-author entries must stay
    return knife_request.numknife != int(numknife) # requests with different numknife stay

  # Loop through all bosses
  for boss in range(len(knife_requests)):
    knife_requests[boss] = list(filter(filter_function, knife_requests[boss]))
  await ctx.send(f'{ctx.author.mention} 已取消所有 第{numknife}刀 的報刀。')
  await update_table()

#CancelBookingforguildmember !unbookfor
@bot.command()
async def unbookfor(ctx, boss, mention):
  if not is_in_channel(ctx, "admin"):
    return

  target_id = mention[3:-1]
  target_user = await bot.fetch_user(target_id)
  def filter_for_non_author(knife_request):
    return target_user.display_name != knife_request.user.display_name
  knife_requests[int(boss)] = list(filter(filter_for_non_author, knife_requests[int(boss)]))
  await ctx.send(f'{ctx.author.mention} 已取消 {boss} 王中 {target_user.mention} 的報刀。')
  await channels['command'].send(f'幹部 {ctx.author.mention} 已取消 {boss} 王中 {target_user.mention} 的報刀。')
  await update_table()

#SeekHelp !sos
class SosPlayer:
  def __init__(self, mention, display_name):
    self.mention = mention
    self.display_name = display_name
  
  def __repr__(self):
    return self.display_name

sos_users = []
@bot.command()
async def sos(ctx):
  if not is_in_channel(ctx, "command"):
    return

  sos_users.append(SosPlayer(ctx.author.mention, ctx.author.display_name))
  await ctx.send(f'{ctx.author.mention} 掛樹了，有人能幫幫他嗎？現時樹上人數: {len(sos_users)}')
  await update_table()

#Nextboss !next
current_boss = 1
last_run_next = time.time()
NEXT_COOLDOWN = 60 # 60s
@bot.command()
async def next(ctx):
  if not is_in_channel(ctx, "command"):
    return

  # Show current/next boss info
  global current_boss, last_run_next
  current_time = time.time()
  print(current_time, " ", last_run_next, " ", NEXT_COOLDOWN)
  if current_time <= last_run_next + NEXT_COOLDOWN:
    await ctx.send(f'此指令還有 {int(NEXT_COOLDOWN - (current_time-last_run_next))} 秒冷卻。')
    return
  last_run_next = current_time
  current_boss = (current_boss % 5) + 1
  next_users = ''
  for request in knife_requests[current_boss]:
    next_users += f'{request.user.mention}({request.damage}, {request.notice}) '
  await ctx.send(f'現在到 {boss_numbers[current_boss]}。 {next_users}')
  
  # Tag all sos users
  user_names = ""
  for user in sos_users:
    user_names += user.mention + ' '
  if user_names != "":
    await ctx.send(f'{user_names} 已經到下一隻王了，可以下樹囉。')
    sos_users.clear()

#Setbossnum !set
@bot.command()
async def set(ctx, bossnum):
  if not is_in_channel(ctx, "admin"):
    return

  try:
      current_boss = int(bossnum)
      if current_boss > 0 and current_boss < 6:
        await channels["command"].send(f'經幹部 {ctx.author.mention} 調整，現在到 {boss_numbers[current_boss]}。')
        await ctx.send(f'{ctx.author.mention} 已強行調整至 {boss_numbers[current_boss]}')
      else:
        await ctx.send(f'請按照 !set [幾王] 的方式調整目前幾王。')
  except:
    await ctx.send(f'請按照 !set [幾王] 的方式調整目前幾王。')

async def update_table():
  #Show the nickname of user, instead of mention the user.
  #Output the table
  def format_list_infos(infos):
    formatted = ''
    for info in infos:
      formatted += f'{info}, '
    return formatted

  table = '```'
  for i in range(1, len(boss_numbers)):
    table += f'{boss_numbers[i]}: {format_list_infos(knife_requests[i])}\n' # 一至五王
  table += '\n'
  table += f'{boss_numbers[0]}: {format_list_infos(knife_requests[0])}\n' # 補償
  table += f'樹上: {format_list_infos(sos_users)}\n'
  table += '```'
  await messages["table"].edit(content=table)

