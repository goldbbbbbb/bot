# IMPORT DISCORD.PY. ALLOWS ACCESS TO DISCORD'S API.
import discord
from discord.ext import commands

def valid_book_input(boss, damage):

    # Validate boss

    bossi = int(boss)

    if bossi < 1 and bossi > 5:
        return False

    return True