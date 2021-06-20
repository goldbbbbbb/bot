# IMPORT DISCORD.PY. ALLOWS ACCESS TO DISCORD'S API.
import discord
from discord.enums import Status
from discord.ext import commands
import time
import shelve


#prefix of the commands in server.
bot = discord.ext.commands.Bot(command_prefix = "!")

channels = {}
messages = {}

def is_in_channel(ctx, channel_name):
  return ctx.channel.name == channels[channel_name].name

#Set variable of round
round = 1

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
  channels["discuss"] = bot.get_channel(815937067342888960)
  channels["group"] = bot.get_channel(815937067342888960)

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

class KnifeRequest:
  def __init__(self, user, boss, damage, notice):
    self.user = user
    self.user_id = user.id
    self.boss = boss
    self.damage = damage
    self.notice = notice
  
  def __repr__(self):
    return f'{self.user.display_name}({self.damage}/{self.notice})'
  
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
    return f'長補: {self.extras}\n\n---------------\n\n正刀: {self.normals}'

  def __getstate__(self):
    return self.__dict__
  
  def __setstate__(self, d):
    self.__dict__ = d

  def remove_user_first_occ(self, target_username):
    for request in self.extras:
      if request.user.display_name == target_username:
        self.extras.remove(request)
        break
    for request in self.normals:
      if request.user.display_name == target_username:
        self.normals.remove(request)
        break

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
boss_numbers = ['短補', '一王', '二王', '三王', '四王', '五王']
knife_requests = [[]] + [KnifeRequests() for _ in range(len(boss_numbers)-1)]

# HP for each boss
stage12 = [0,6000000,8000000,10000000,12000000,15000000]
stage3 = [0,7000000,9000000,13000000,15000000,20000000]
stage4 = [0,17000000,18000000,20000000,21000000,23000000]
stage5 = [0,85000000,90000000,95000000,100000000,110000000]
bosshp = 0
remainhp = 6000000

@bot.command()
async def b(ctx, boss, damage, notice="無", extra=False):
  if not is_in_channel(ctx, "command"):
    return

  await b_content(ctx, boss, damage, notice, extra)

async def b_content(ctx, boss, damage, notice="無", extra=False):

  msg = ''

  try:
    boss = int(boss)
    if (bool(extra)):
      msg = f'{ctx.author.mention} ' + ('補償刀' if bool(extra) else '') + f'預約 {boss_numbers[boss]} , 秒數: {damage}秒, 備注: {notice}'
    else:
      msg = f'{ctx.author.mention} ' + f'預約 {boss_numbers[boss]} , 傷害: {damage}, 備注: {notice}'
    if boss > 0:
      knife_requests[boss].add(KnifeRequest(ctx.author, boss, damage, notice), bool(extra))
    else:
      knife_requests[boss].append(KnifeRequest(ctx.author, boss, damage, notice))
  except:
    #raise ValueError
    msg = '請按照 !book [幾王] [傷害] [備注] 的方式報刀'
    #sort the user input into different list base on value of variable boss.

  #except Exception as err:
    # for debug only
    #from traceback import print_stack
    #print_stack()


  await ctx.send(msg)
  await update_table()

# Requests for each boss (long make up time) !extra
@bot.command()
async def eb(ctx, boss, damage, notice="無"):
  await b_content(ctx, boss, damage, notice, extra=True)

#CancelBooking !unbook
@bot.command()
async def ub(ctx, bossnum):
  if not is_in_channel(ctx, "command"):
    return

  await ub_content(ctx, int(bossnum))

async def ub_content(ctx, bossnum):

  target_username = ctx.author.display_name
  bossnum = int(bossnum)
  if bossnum == 0: # knife_requests[0] is a list
    for request in knife_requests[bossnum]:
      if request.user.display_name == target_username:
        knife_requests[bossnum].remove(request)
        break
  else: # knife_requests[boss] is a KnifeRequests object
    knife_requests[bossnum].remove_user_first_occ(target_username)
  await ctx.send(f'{ctx.author.mention} 已取消所有 {bossnum}王 的報刀。')
  await update_table()

#CancelBookingforguildmember !unbookfor
@bot.command()
async def ubf(ctx, bossnum, mention):
  if not is_in_channel(ctx, "admin"):
    return

  target_id = mention[3:-1]
  target_user = await ctx.guild.fetch_member(target_id)
  def filter_for_non_author(knife_request):
    return target_user.display_name != knife_request.user.display_name
  
  # boss = int(boss)

  # Loop through all bosses
  target_username = ctx.author.display_name
  bossnum = int(bossnum)
  if bossnum == 0: # knife_requests[0] is a list
    for request in knife_requests[bossnum]:
      if request.user == target_username:
        knife_requests[bossnum].remove(request)
        break
  else: # knife_requests[boss] is a KnifeRequests object
    knife_requests[bossnum].remove_user_first_occ(target_username)

  #if boss == 0:
    #knife_requests[boss] = list(filter(filter_for_non_author, knife_requests[boss]))
  #else:
    #knife_requests[boss].apply_filter(filter_for_non_author)
  await ctx.send(f'{ctx.author.mention} 已取消 {bossnum} 王中 {target_user.mention} 的報刀。')
  await channels['command'].send(f'幹部 {ctx.author.mention} 已取消 {bossnum} 王中 {target_user.mention} 的報刀。')
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
  #if not is_in_channel(ctx, "command"):
    #return
  sos_users.add(SosPlayer(ctx.author.mention, ctx.author.display_name))
  await channels["discuss"].send(f'{ctx.author.mention} 掛樹了，有人能幫幫他嗎？現時樹上人數: {len(sos_users)}')
  await update_table()

#Nextboss !next
current_boss = 1
last_run_next = time.time()
NEXT_COOLDOWN = 1 # 60s

@bot.command()
async def next(ctx):
  if not is_in_channel(ctx, "command"):
    return

  await next_content(ctx)

async def next_content(ctx):
  # Show current/next boss info
  global current_boss, last_run_next, round
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
  await channels["discuss"].send(f'現在到 {boss_numbers[current_boss]}。 {next_users}')
  # increase the round when current_boss back to 1
  if current_boss == 1:
    round = round + 1
  await update_table()

reports = {}
remainknife = {}
namelist = {}
resetknife = {}
extraknife = {}

#Register as guild member
@bot.command()
async def reg(ctx, gameid):
  if remainknife.__contains__(ctx.author.id):
    await ctx.send(f'{ctx.author.mention} 你已經登錄過了，不需要再登錄一次。')
  else:
    remainknife[ctx.author.id] = 3
    resetknife[ctx.author.id] = 3
    namelist[ctx.author.id] = gameid
    await ctx.send(f'{ctx.author.mention} 已登錄完成，登錄ID為：{gameid}。')

#Unregister for change the id
@bot.command()
async def unreg(ctx):
  if remainknife.__contains__(ctx.author.id):
    del remainknife[ctx.author.id]
    await ctx.send(f'{ctx.author.mention} 已取消登錄。')
  else:
    await ctx.send(f'{ctx.author.mention} 你並未有登錄紀錄。')

#reset the num of knife(when 5:00)
@bot.command()
async def reset(ctx):

  if not is_in_channel(ctx, "admin"):
    return
  
  remainknife.update(resetknife)

#Check the remain knife real time
@bot.command()
async def 查刀(ctx):
  remain = f'```目前剩餘刀數\n\n'
  for dcid, num in remainknife.items():
    dcname = namelist[dcid]
    remain += f'剩餘{num}刀         {dcname}\n'
  remain += f'\n'
  remain += f'還剩 {sum(remainknife.values())} 刀'
  remain += '```'
  await ctx.send(remain)

#Check the remain extra knife real time
@bot.command()
async def 殘刀(ctx):
  extraremain = f'```補償刀清單\n\n'
  for dcid, time in extraknife.items():
    dcname = namelist[dcid]
    extraremain += f'{time}秒         {dcname}\n'
  extraremain += '```'
  await ctx.send(extraremain)

#Tell the control field that you are going into the fight
@bot.command()
async def 進(ctx):
  if not is_in_channel(ctx, "group"):
    return

  #check if the user used this function in same boss or not
  if (ctx.author.display_name in reports):
    await ctx.send(f'{ctx.author.mention} 你已經報過進刀了，不用再報一次。')

  elif (remainknife[ctx.author.id] == 0):
    await ctx.send(f'{ctx.author.mention}你已經出完三刀了，無法再報出/尾刀。')

  #import user display name into the list
  else:
    reports[ctx.author.display_name] = ''
    await ctx.send(f'{ctx.author.mention} 已進場打 {boss_numbers[current_boss]}。')

@bot.command()
async def 報(ctx, msg):
  if not is_in_channel(ctx, "group"):
    return

  #check if the user used 進 function or not
  if (ctx.author.display_name not in reports):
    await ctx.send(f'{ctx.author.mention} 你還沒報進刀，是要怎麼報正式戰狀況？')

  #check if the user registered or not
  if (ctx.author.id not in namelist):
    await ctx.send(f'{ctx.author.mention} 你仍未登錄於查刀表，因此無法進刀。')

  else:
    reports[ctx.author.display_name] = msg
    print(reports)
    await ctx.send(f'{ctx.author.mention} 已回報：{msg}')

#check the status of guild member
@bot.command()
async def 控刀(ctx):
  stat = f'```目前進刀狀況：\n\n'
  for user, msg in reports.items():
    stat += f'{user} 已進場，報：{msg}\n'
  stat += '```'
  await ctx.send(stat)

#for guild member report damage
@bot.command()
async def 出(ctx, damage):
  if not is_in_channel(ctx, "group"):
    return

  global current_boss, last_run_next, round, remainhp, bosshp, reports
  if round < 11:
    bosshp = int(stage12[current_boss])
  elif round < 35:
    bosshp = int(stage3[current_boss]) 
  elif round < 45:
    bosshp = int(stage4[current_boss]) 
  else:
    bosshp = int(stage5[current_boss])

  if remainhp <= 0:
    await ctx.send(f'{ctx.author.mention}王已經倒了，你沒辦法造成傷害。')
  else:
    if (remainknife[ctx.author.id] == 0):
      await ctx.send(f'{ctx.author.mention}你已經出完三刀了，無法再報出/尾刀。')
    elif remainhp == bosshp:
      remainhp = bosshp - int(damage)
    else:
      remainhp = remainhp - int(damage)

    if (remainknife[ctx.author.id] != 0):
      if (remainhp > 0):  
        await ctx.send(f'{ctx.author.mention} 已出場，對 {boss_numbers[current_boss]} 造成了{damage}點傷害，目前王還剩 {remainhp} 點血。')
        if extraknife.__contains__(ctx.author.id):
          #run the ub function
          await ub_content(ctx, current_boss)

          #remove the user from report list
          del reports[ctx.author.display_name]

          #remove the user from extraknife list
          del extraknife[ctx.author.id]
        else:
          #numknife of that guild member minus 1
          remainknife[ctx.author.id] = remainknife[ctx.author.id] - 1
        
          #run the ub function
          await ub_content(ctx, current_boss)

          #remove the user from report list
          del reports[ctx.author.display_name]
      else:
        # show the bossisdead msg
        await ctx.send(f'{ctx.author.mention} 已出場，對 {boss_numbers[current_boss]} 造成了{damage}點傷害並收王。')
        await ctx.send(f'{ctx.author.mention} 請使用指令 !尾 <秒數> <幾王>，若使用補償刀收王請輸入 !尾 0 0')
  
  await update_table()

#for guild member report the extra second
@bot.command()
async def 尾(ctx, time, bossnum=0):
  if not is_in_channel(ctx, "group"):
    return

  global reports, remainhp

  #run the eb function if the collecter is 正刀
  time = int(time)
  bossnum = int(bossnum)
  if (remainknife[ctx.author.id] == 0):
    await ctx.send(f'{ctx.author.mention}你已經出完三刀了，無法再報出/尾刀。')
  elif (bossnum < 0 or bossnum > 5):
    await ctx.send(f'{ctx.author.mention} 請按照 !尾 <秒數> <幾王> 的格式使用指令')

  #情境一：非補償刀收王，非短補
  elif (time != 0 and bossnum != 0):
    #numknife of that guild member minus 1
    remainknife[ctx.author.id] = remainknife[ctx.author.id] - 1

    #run the b function
    await b_content(ctx, bossnum, time, extra=True)

    #run the ub function
    await ub_content(ctx, current_boss)

    #add user into extraknife list
    extraknife[ctx.author.id] = time

    # run the next function
    # Show current/next boss info
    await next_content(ctx)

    # reset the remain hp
    if round < 11:
      remainhp = int(stage12[current_boss])
    elif round < 35:
      remainhp = int(stage3[current_boss]) 
    elif round < 45:
      remainhp = int(stage4[current_boss]) 
    else:
      remainhp = int(stage5[current_boss])
    stat = f'```目前進刀狀況：\n\n'
    stat += '```'
    reports = {}

    await update_table()

  #情境二：非補償刀收王，屬短補
  elif (time != 0 and bossnum == 0):
    #numknife of that guild member minus 1
    remainknife[ctx.author.id] = remainknife[ctx.author.id] - 1

    #run the b function
    await b_content(ctx, 0, time, extra=True)

    #run the ub function
    await ub_content(ctx, current_boss)


    #add user into extraknife list
    extraknife[ctx.author.id] = time

    # run the next function
    # Show current/next boss info
    await next_content(ctx)

    # reset the remain hp
    if round < 11:
      remainhp = int(stage12[current_boss])
    elif round < 35:
      remainhp = int(stage3[current_boss]) 
    elif round < 45:
      remainhp = int(stage4[current_boss]) 
    else:
      remainhp = int(stage5[current_boss])
    print(remainhp)

    stat = f'```目前進刀狀況：\n\n'
    stat += '```'
    reports = {}

    await update_table()

  #情境三：補償刀收王
  else:
    #run the ub function
    await ub_content(ctx, current_boss)

    # run the next function
    # Show current/next boss info
    await next_content(ctx)

    #remove the user from extraknife list
    del extraknife[ctx.author.id]

    # reset the remain hp
    if round < 11:
      remainhp = int(stage12[current_boss])
    elif round < 35:
      remainhp = int(stage3[current_boss]) 
    elif round < 45:
      remainhp = int(stage4[current_boss]) 
    else:
      remainhp = int(stage5[current_boss])
    print(remainhp)

    stat = f'```目前進刀狀況：\n\n'
    stat += '```'
    reports = {}

    await update_table()

#Setbossnum !set
@bot.command()
async def set(ctx, roundnum, bossnum):
  if not is_in_channel(ctx, "admin"):
    return

  global round, remainhp

  try:
      if int(bossnum) > 0 and int(bossnum) < 6:
        global current_boss
        current_boss = int(bossnum)
        round = int(roundnum)
        await channels["command"].send(f'經幹部 {ctx.author.mention} 調整，現在到 {round}周{boss_numbers[current_boss]}。')
        await ctx.send(f'{ctx.author.mention} 已強行調整至 {round}周{boss_numbers[current_boss]}')
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

  table = f'**目前到 {round}周{boss_numbers[current_boss]}**\n\n==============================\n'
  for i in range(1, len(boss_numbers)):
    if i == current_boss:
      table += f'\n> **>>>>>  {boss_numbers[i]}，剩餘血量 {remainhp}  <<<<<**\n```fix\n{knife_requests[i]}\n```\n'
    else:
      table += f'\n{boss_numbers[i]}\n```{knife_requests[i]}\n```\n' # 一至五王
  table += ''
  table += f'\n{boss_numbers[0]}: {format_list_infos(knife_requests[0])}\n' # 補償
  table += f'\n樹上: {format_list_infos(sos_users) if len(sos_users)>0 else ""}\n'
  table += ''
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