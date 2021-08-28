import asyncio
import discord
from discord.ext import commands, tasks
from discord.ext.commands.bot import Bot
from dotenv import load_dotenv
import os.path
import json
import GoogleCalendar as gc
import scheduling as sc


def create_bot_instance():
    """Main method used for bot life cycle, may change later since the structure could be better"""
    load_dotenv()
    TOKEN = os.getenv('BOT_TOKEN')
    GUILD = os.getenv('DISCORD_GUILD')
    intents = discord.Intents.all()
    bot = commands.Bot(command_prefix='!', intents=None)

    sc.run_continuously(bot)

    return bot, TOKEN


async def process_weekly_schedule(channel_name='bot-spam'):
    service = gc.access_google_calendar()
    file_name = gc.process_weekly_events(service)
    channel = discord.utils.get(bot.get_all_channels(), name=channel_name)
    if file_name:
        os.chdir("./json_weekly_files")
        text = None
        with open(file_name, 'r') as f:
            text = "UALBANY IEEE WEEKLY SCHEDULE:\n\n"
            data = json.load(f)
            for i in range(len(data)):
                text += "Event: " + data[f"Event No.{i + 1}"]['event_name'] + '\n' + "Summary: " + \
                        data[f"Event No.{i + 1}"]['description'] + '\n' + "Start time: " + \
                        data[f"Event No.{i + 1}"]['start_time'] + '\n' + "End time: " + \
                        data[f"Event No.{i + 1}"]['end_time'] + '\n' + "Location: " + \
                        data[f"Event No.{i + 1}"]['location'] + '\n'
                if 0 <= i < len(data) - 1:
                    text += '\n'
            f.close()
        os.chdir('..')
        channel.send(f"```{text}```")


# def post_message(text: str, bot, channel_name='bot-spam'):
#     channel = discord.utils.get(bot.get_all_channels(), name=channel_name)
#     if text:
#         asyncio.run(channel.send(f"```{text}```"))


def main():
    bot_instance, bot_token = create_bot_instance()
    bot_instance.run(bot_token)


if __name__ == '__main__':
    main()


# TODO: FIGURE OUT A GOOD WAY TO PARSE AND HANDLE THE HTML LINK HREF IN THE DESCRIPTION
# TODO: ORGANIZE THIS SHIT A LOT MORE, LOOKS AWFUL RIGHT NOW