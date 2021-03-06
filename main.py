# IMPORT DISCORD.PY. ALLOWS ACCESS TO DISCORD'S API.
import discord
from discord.ext import commands

intents = discord.Intents.all()

#指令前綴
bot = discord.ext.commands.Bot(command_prefix = "!")

#BOT開始運作的確認訊息
@bot.event
async def on_ready():
	print(f'佩可機器人準備完成!')

#BookBoss !book
@bot.command()
async def book(ctx, boss, damage, notice):
	await ctx.send(f'{ctx.author.mention} 預約 {boss} 王, 傷害: {damage}, 備注: {notice}')

#CancelBooking !unbook
@bot.command()
async def unbook(ctx, boss):
	await ctx.send(f'{ctx.author.mention} 已取消 {boss} 王 的報刀。')

#SeekHelp !sos
sos_users = []
@bot.command()
async def sos(ctx):
  sos_users.append(ctx.author)
  await ctx.send(f'{ctx.author.mention} 掛樹了，有人能幫幫他嗎？現時死亡人數: {len(sos_users)}')

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

# EXECUTES THE BOT WITH THE SPECIFIED TOKEN. TOKEN HAS BEEN REMOVED AND USED JUST AS AN EXAMPLE.
bot.run("ODE2ODk0ODc0OTY3MzQzMTU0.YEBmow.sx1h53VnHvzK3ACP-N5kgTW8gjU") 