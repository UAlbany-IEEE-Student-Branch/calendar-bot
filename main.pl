import discord 
from discord.ext import commands
from discord.ext.commands.bot import Bot
from dotenv import load_dotenv
import os


load_dotenv('.env')
TOKEN = os.getenv("IEEE_Bot")