import asyncio
import time
import discord
from discord.ext import commands, tasks
from dotenv import load_dotenv
import os.path
import json
from datetime import datetime
import dateutil.parser as parser
import GoogleCalendar as gc


async def process_weekly_schedule():
    """This function is used to access google calendar, process events for the week and return the file path"""
    try:
        service = gc.access_google_calendar()
    except Exception:
        print(Exception.__cause__)
        exit(1)
    file_path = gc.process_weekly_events(service)
    return file_path


def bot():
    """This is the main bot loop; runs throughout the bot life cycle"""
    load_dotenv()
    TOKEN = os.getenv('BOT_TOKEN')
    GUILD = os.getenv('DISCORD_GUILD')
    intents = discord.Intents.all()
    bot = commands.Bot(command_prefix='!', intents=None)


    @bot.event
    async def on_ready():
        """Prints message to the console when bot connects to discord"""
        print(f"{bot.user.name} has connected to Discord!")


    @bot.command(name=f'Hello', help='Responds with a greeting from Calendar-bot')
    async def greeting(ctx):
        await ctx.send(f"Hello, {ctx.message.author.mention}\nMy name is {bot.user.name}!")


    async def post_weekly_schedule(file_path: str, channel):
        """Posts weekly schedule for IEEE at sunday at 12 AM each week"""

        await bot.wait_until_ready()

        text = None
        with open(file_path, 'r') as f:
            text = "UALBANY IEEE WEEKLY SCHEDULE:\n\n"
            data = json.load(f)
            for i in range(1, len(data) + 1):
                # print(data)
                text += "Event: " + str(data[f"Event No.{i}"]['event_name']) + '\n' + "Summary: " +\
                        str(data[f"Event No.{i}"]['description']) + '\n' + "Date: " + \
                        str(data[f"Event No.{i}"]['date']) + '\n' + "Start time: " + \
                        str(data[f"Event No.{i}"]['start_time']) + '\n' + "End time: " + \
                        str(data[f"Event No.{i}"]['end_time']) + '\n' + "Location: " + \
                        str(data[f"Event No.{i}"]['location']) + '\n'
                if 1 <= i < len(data):
                    text += '\n'

        await channel.send(f"```{text}```")


    async def post_reminder(file_path: str, event_idx: int, channel):
        """Posts reminders for IEEE events in discord"""

        await bot.wait_until_ready()

        text = None
        with open(file_path, 'r') as f:
            data = json.load(f)
            text = "Reminder"
            text = f"@everyone Reminder that we will be hosting {data[f'Event No.{event_idx}']['event_name']} " \
                   f"at {data[f'Event No.{event_idx}']['start_time']}!!!"
            f.close()

        await channel.send(f"{text}")


    @tasks.loop(seconds=10) # TODO: Make sure to change the seconds variable here
    async def check_weekly_schedule(channel_name='bot-spam'):
        """This function schedules the posting of the general schedule and the reminders for IEEE events; loops
        every week at the same time"""
        channels = bot.get_all_channels()
        channel = None
        for i in channels:
            channel = i if i.name == channel_name else channel
        file_path = await process_weekly_schedule()
        if file_path:
            refresh_access_token.start() # This will be used to automatically refresh token
            await post_weekly_schedule(file_path, channel)
            with open(file_path, 'r') as f:
                data = json.load(f)
                time_format = "%U:%w:%H:%M:%S"
                seconds_before = 10 * 60
                for i, event in enumerate(data):
                    start_time = data[f'Event No.{i+1}']['start_time_parse']
                    now = datetime.strftime(datetime.now(), time_format)
                    diff = (datetime.strptime(start_time, time_format) -
                            datetime.strptime(now, time_format)).total_seconds()
                    await asyncio.sleep(diff - seconds_before)
                    await post_reminder(file_path, i + 1, channel)


    @check_weekly_schedule.before_loop
    async def before_check_weekly_schedule():
        """Kind of like a preprocessing function to do before the loop"""
        time_format = "%U:%w:%H:%M:%S"
        week_num = time.strftime('%U')
        await bot.wait_until_ready()
        now = datetime.strftime(datetime.now(), time_format)
        diff = (datetime.strptime(f'{int(week_num) + 1}:0:00:00:00', time_format) -
                datetime.strptime(now, time_format)).total_seconds()
        diff = 5
        await asyncio.sleep(diff)

    @tasks.loop(seconds=1) 
    async def refresh_access_token():
        """This function serves to refresh access 10 seconds before it is set to expire"""
        time_format = "%m/%d/%Y, %H:%M:%S"
        seconds_before_expiry = 10
        with open("token.json") as f:
            data = json.load(f)
            expiry = data['expiry']
            time_of_expiry = (parser.parse(expiry)).strftime(time_format)
            time_of_expiry = datetime.strptime(time_of_expiry, time_format)
            now = (datetime.now()).strftime(time_format)
            now = datetime.strptime(now, time_format)
            time_unitl_expiry = (time_of_expiry - now).total_seconds()
            await asyncio.sleep(time_unitl_expiry - seconds_before_expiry)
            gc.refresh_token()


    check_weekly_schedule.start()


    bot.run(TOKEN)


bot()

# TODO: Test the bot once more using the standard process of saving the weekly schedule to a local directory. If it
#  fails, consider using mongoDB

# TODO: Create a task that dynamically refreshes the auth token once it expires, use dummy task as a template

# TODO: Figure out how to dynamically receive access tokens via refreshing with repeated user consent, or find another
#  mode of getting access