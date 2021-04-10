# IMPORT DISCORD.PY. ALLOWS ACCESS TO DISCORD'S API.
# IMPORT GSPREAD, ALLOWS ACCESS TO READ GOOGLE SHEETS.
import discord
from discord.ext import commands
import time
import gspread
import shelve
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
  channels_test = {}
  messages_test = {}
  channels_test["command"] = bot.get_channel(817674249699459072)
  channels_test["table"] = bot.get_channel(817829173069348884)
  channels_test["admin"] = bot.get_channel(818157150232248341)
  messages_test["table"] = await channels_test["table"].fetch_message(817834334365941761)

  #817674249699459072 掛樹頻->報刀頻 771259390241669132
  #817829173069348884 刀表->報刀表 818898908407267338
  #818157150232248341 admin->幹部頻 817851835955281930
  #817834334365941761 刀表頻msg->報刀表msg 818904471606132767
  channels["command"] = bot.get_channel(771259390241669132)
  channels["table"] = bot.get_channel(818898908407267338)
  channels["admin"] = bot.get_channel(817851835955281930)

  messages["table"] = await channels["table"].fetch_message(818904471606132767)

  # Comment out these lines to use in actual server
  # globals()['channels'] = channels_test
  # globals()['messages'] = messages_test
  #################################################

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
  #let user can use !num in any channel
  #if not is_in_channel(ctx, "command"):
    #return
  #get the data in (38,17) of first sheet of the google sheets we assigned.
  result = sheet.cell(38,17).value
  await ctx.send(f'目前仍有 {result} 刀未出。')

#BookBoss !book

class KnifeRequest:
  def __init__(self, user, numknife, damage, notice):
    self.user = user
    self.user_id = user.id
    self.numknife = numknife
    self.damage = damage
    self.notice = notice
  
  def __repr__(self):
    return f'{self.user.display_name}(第{self.numknife}刀/{self.damage}/{self.notice})'
  
  def __getstate__(self):
    d = dict(self.__dict__)
    del d['user'] # Not serializable
    return d
  
  def __setstate__(self, d):
    self.__dict__ = d # User is not defined after this

  async def fetch_user(self):
    self.user = await bot.fetch_user(self.user_id)

class KnifeRequests:
  def __init__(self):
    self.extras = []
    self.normals = []

  def __repr__(self):
    return f'{self.extras} | {self.normals}'

  def __getstate__(self):
    return self.__dict__
  
  def __setstate__(self, d):
    self.__dict__ = d

  def apply_filter(self, filter_func):
    self.extras = list(filter(filter_func, self.extras))
    self.normals = list(filter(filter_func, self.normals))

  def add(self, request, is_extra):
    if is_extra:
      self.extras.append(request)
    else:
      self.normals.append(request)

  async def fetch_users(self):
    for request in self.extras:
      await request.fetch_user()

    for request in self.normals:
      await request.fetch_user()

# Requests for each boss
boss_numbers = ['補償', '一王', '二王', '三王', '四王', '五王']
knife_requests = [[]] + [KnifeRequests() for _ in range(len(boss_numbers)-1)]

@bot.command()
async def b(ctx, boss, numknife, damage, notice="無", extra=False):
  if not is_in_channel(ctx, "command"):
    return

  msg = ''

  try:
    boss = int(boss)
    numknife = int(numknife)
    if numknife > 0 and numknife < 4:
      msg = f'{ctx.author.mention} ' + ('補償刀' if bool(extra) else '') + f'預約 {boss_numbers[boss]} , 刀數: {numknife}, 傷害: {damage}, 備注: {notice}'
    else:
      raise ValueError
      #sort the user input into different list base on value of variable boss.
    if boss > 0:
      knife_requests[boss].add(KnifeRequest(ctx.author, numknife, damage, notice), bool(extra))
    else:
      knife_requests[boss].append(KnifeRequest(ctx.author, numknife, damage, notice))
  except Exception as err:
    # for debug only
    from traceback import print_stack
    print_stack()

    msg = '請按照 !book [幾王] [第幾刀] [傷害] [備注] 的方式報刀'

  await ctx.send(msg)
  await update_table()

# Requests for each boss (long make up time) !extra
@bot.command()
async def eb(ctx, boss, numknife, damage, notice="無"):
  await b(ctx, boss, numknife, damage, notice, True)

#CancelBooking !unbook
@bot.command()
async def ub(ctx, numknife):
  if not is_in_channel(ctx, "command"):
    return

  def filter_function(knife_request):
    if ctx.author.display_name != knife_request.user.display_name:
      return True # All non-author entries must stay
    return knife_request.numknife != int(numknife) # requests with different numknife stay

  # Loop through all bosses
  for boss in range(len(knife_requests)):
    if boss == 0:
      knife_requests[boss] = list(filter(filter_function, knife_requests[boss]))
    else:
      knife_requests[boss].apply_filter(filter_function)
  await ctx.send(f'{ctx.author.mention} 已取消所有 第{numknife}刀 的報刀。')
  await update_table()

#CancelBookingforguildmember !unbookfor
@bot.command()
async def ubf(ctx, boss, mention):
  if not is_in_channel(ctx, "admin"):
    return

  target_id = mention[3:-1]
  target_user = await ctx.guild.fetch_member(target_id)
  def filter_for_non_author(knife_request):
    return target_user.display_name != knife_request.user.display_name
  
  boss = int(boss)

  if boss == 0:
    knife_requests[boss] = list(filter(filter_for_non_author, knife_requests[boss]))
  else:
    knife_requests[boss].apply_filter(filter_for_non_author)
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

  def __hash__(self):
    return hash((self.mention, self.display_name))

  def __eq__(self, other):
    if not isinstance(other, type(self)): return NotImplemented
    return self.mention == other.mention and self.display_name == other.display_name

sos_users = set()
@bot.command()
async def sos(ctx):
  if not is_in_channel(ctx, "command"):
    return
  sos_users.add(SosPlayer(ctx.author.mention, ctx.author.display_name))
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
  if current_time <= last_run_next + NEXT_COOLDOWN:
    await ctx.send(f'此指令還有 {int(NEXT_COOLDOWN - (current_time-last_run_next))} 秒冷卻。')
    return
  last_run_next = current_time
  current_boss = (current_boss % 5) + 1
  next_users = ''
  # print(type(knife_requests))
  for request in knife_requests[current_boss].normals + knife_requests[current_boss].extras:
    next_users += f'{request.user.mention}({request.damage}, {request.notice}) '
  await ctx.send(f'現在到 {boss_numbers[current_boss]}。 {next_users}')

  # Tag all sos users
  user_names = ""
  for user in sos_users:
    user_names += user.mention + ' '
  if user_names != "":
    await ctx.send(f'{user_names} 已經到下一隻王了，可以下樹囉。')
    sos_users.clear()
    print(sos_users)
  
  await update_table()

#Setbossnum !set
@bot.command()
async def set(ctx, bossnum):
  if not is_in_channel(ctx, "admin"):
    return

  try:
      if int(bossnum) > 0 and int(bossnum) < 6:
        global current_boss
        current_boss = int(bossnum)
        await channels["command"].send(f'經幹部 {ctx.author.mention} 調整，現在到 {boss_numbers[current_boss]}。')
        await ctx.send(f'{ctx.author.mention} 已強行調整至 {boss_numbers[current_boss]}')
        await update_table()
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

  table = '```diff\n'
  for i in range(1, len(boss_numbers)):
    if i == current_boss:
      table += f'->{boss_numbers[i]}: {knife_requests[i]}<-\n'
    else:
      table += f'{boss_numbers[i]}: {knife_requests[i]}\n' # 一至五王
  table += '\n'
  table += f'{boss_numbers[0]}: {format_list_infos(knife_requests[0])}\n' # 補償
  table += f'樹上: {format_list_infos(sos_users) if len(sos_users)>0 else ""}\n'
  table += '```'
  await messages["table"].edit(content=table)

# Save and Load everything in the table (knife_requests and sos_users)
var_to_save = ['knife_requests', 'sos_users']
def save_data(filename):
  shelf = shelve.open(filename, 'n')
  for key in var_to_save:
    shelf[key] = globals()[key]
  shelf.close()

def load_data(filename):
  shelf = shelve.open(filename)
  for key in shelf:
    globals()[key] = shelf[key]
  shelf.close()

@bot.command()
async def save(ctx, filename=''):
  if not is_in_channel(ctx, 'admin'):
    return
  save_data(f'./backup/states_{filename}.dir')
  await ctx.send(f'已將刀表儲存至backup/states_{filename}')
  
@bot.command()
async def load(ctx, filename=''):
  if not is_in_channel(ctx, 'admin'):
    return
  msg = await ctx.send('讀取刀表中..')
  load_data(f'./backup/states_{filename}.dir')
  # Fetch back the user objects
  for i in range(1, len(knife_requests)):
    await knife_requests[i].fetch_users()
    await msg.edit(content=msg.clean_content + '.') # Simulate loading
  await update_table()
  await msg.edit(content=msg.clean_content + '已完成')