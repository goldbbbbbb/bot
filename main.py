# IMPORT DISCORD.PY. ALLOWS ACCESS TO DISCORD'S API.
import discord
from discord.ext import commands

intents = discord.Intents.all()

#指令前綴
bot = discord.ext.commands.Bot(command_prefix = "!");

#BOT開始運作的確認訊息
@bot.event
async def on_ready():
	print(f'佩可機器人準備完成!')

#報刀功能 !book
@bot.command()
async def book(ctx, boss, damage, notice):
	await ctx.send(f'{ctx.author.mention} 預約 {boss} 王, 傷害: {damage}, 備注: {notice}')

#取消報刀功能 !unbook
@bot.command()
async def unbook(ctx, boss, damage, notice):
	await ctx.send(f'{ctx.author.mention} 已取消 {boss} 王 的報刀。')

#掛樹求救功能 !sos
@bot.command()
async def sos(ctx):
   await ctx.send(f'{ctx.author.mention} 掛樹了，有人能幫幫他嗎？')

@bot.event
async def on_raw_reaction_add(payload):
    message_id = payload.message_id
    if message_id == 817683128855691266:
      guild_id = payload.guild_id
      guild = discord.utils.find(lambda g: g.id == guild_id, bot.guilds)

      if payload.emoji.name == 'happy':
        role = discord.utils.get(guild.roles, name='TREE')
        print("first part done.")
      else:
        role = discord.utils.get(guild.roles, name=payload.emoji.name)
        
      if role is not None:
        member = payload.member
        print('second part done')
        if member is not None:
          await member.add_roles(role)
          print("Done")
        else:
          print("Member not found.")
      else:
        print("Role not found")

# EXECUTES THE BOT WITH THE SPECIFIED TOKEN. TOKEN HAS BEEN REMOVED AND USED JUST AS AN EXAMPLE.
bot.run("ODE2ODk0ODc0OTY3MzQzMTU0.YEBmow.sx1h53VnHvzK3ACP-N5kgTW8gjU") 