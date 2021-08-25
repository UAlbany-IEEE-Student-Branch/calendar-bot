import time
import discord
from discord.ext import commands, tasks
from discord.ext.commands.bot import Bot
from dotenv import load_dotenv
import os.path
import json
import GoogleCalendar as gc


def main():
    """Main method used for bot life cycle, may change later since the structure could be better"""
    load_dotenv()
    TOKEN = os.getenv('BOT_TOKEN')
    GUILD = os.getenv('DISCORD_GUILD')
    # intents = discord.Intents.all()
    bot = commands.Bot(command_prefix='!', intents=None)

    service = gc.access_google_calendar()

    class TaskManager(commands.Cog):
        """Inner-class TaskManager which used a Cog to carry out scheduled tasks behind the scenes"""
        def __init__(self):
            self.time_check.start()

        @tasks.loop(seconds=1.0)
        async def time_check(self):
            current_time = time.localtime()
            if current_time.tm_wday == 6 and current_time.tm_hour == 0 and current_time.tm_min == 0 \
                    and current_time.tm_sec == 0:
                await process_weekly_schedule()


    task_manager = TaskManager()  # Making an instance of the Cog class TaskManager


    @bot.event
    async def process_weekly_schedule(given_name='bot-spam'):
        """Bot event that is called via the TaskManager instance, interacts with the google calendar API, processes
        a .json file with the week's events, reads from the generated file and posts the weekly schedule in general
        text channel"""
        channel = discord.utils.get(bot.get_all_channels(), name=given_name)
        # all_channels = bot.get_all_channels()
        # channel = filter(lambda x: x == 'bot-spam', all_channels)
        file_name = gc.process_weekly_events(service)
        if file_name:
            os.chdir("./json_weekly_files")
            text = None
            with open(file_name, 'r') as f:
                text = "UALBANY IEEE WEEKLY SCHEDULE:\n\n"
                data = json.load(f)
                for i in range(len(data)):
                    text += "Event: " + data[f"Event No.{i+1}"]['event_name'] + '\n' + "Summary: " + \
                            data[f"Event No.{i+1}"]['description'] + '\n' + "Start time: " + \
                            data[f"Event No.{i+1}"]['start_time'] + '\n' + "End time: " + \
                            data[f"Event No.{i+1}"]['end_time'] + '\n' + "Location: " + \
                            data[f"Event No.{i+1}"]['location'] + '\n'
                    if 0 <= i < len(data) - 1:
                        text += '\n'
                f.close()
            await channel.send(f"```{text}```", )
        else:
            print("There seems to have been no schedule for this coming week. Disregard if this is not a problem, "
                  "otherwise please attend to the schedule.")
            await channel.send('null')


    bot.run(TOKEN)


if __name__ == '__main__':
    main()

#TODO: FIGURE OUT A GOOD WAY TO PARSE AND HANDLE THE HTML LINK HREF IN THE DESCRIPTION
#TODO: ORGANIZE THIS SHIT A LOT MORE, LOOKS AWFUL RIGHT NOW