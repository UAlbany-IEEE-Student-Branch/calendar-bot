import discord
from discord.ext import commands, tasks
from discord.ext.commands.bot import Bot
from dotenv import load_dotenv
import os.path
import GoogleCalendar as gc


def main():
    load_dotenv()
    TOKEN = os.getenv('BOT_TOKEN')
    GUILD = os.getenv('DISCORD_GUILD')
    # intents = discord.Intents.all()
    bot = commands.Bot(command_prefix='!', intents=None)

    service = gc.access_google_calendar()

    @bot.event
    async def on_ready():
        """
        :return:
        """
        print(f"{bot.user.name} has connected to Discord!")

    @bot.command(name='Hello', help=f'Responds with a greeting from this bot')
    async def greeting(ctx):
        """
        :param ctx:
        :return:
        """
        await ctx.send(f"Hello, {ctx.message.author.mention}\nMy name is {bot.user.name}!")

    @bot.event
    async def process_weekly_schedule(ctx, given_name='general'):
        channel = discord.utils.get(ctx.guild.channels, name=given_name)
        file_name = gc.process_weekly_events(service)
        os.chdir("./json_weekly_files")
        text = None
        with open(file_name, 'r') as f:
            text = f.read()
            f.close()
            os.chdir('..')
        await channel.send(text)


    bot.run(TOKEN)


if __name__ == '__main__':
    main()

#TODO: FIGURE OUT HOW TO CONFIGURE TIMED EVENTS FOR BOT EVENTS LIKE PROCESS_WEEKLY_SCHEDULE