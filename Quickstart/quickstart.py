import asyncio
import time
import discord
from discord.ext import commands, tasks
from dotenv import load_dotenv
import os.path
import json
from datetime import datetime
import GoogleCalendar as gc


async def process_weekly_schedule():
    """This function is used to access google calendar, process events for the week and return the file path"""
    service = gc.access_google_calendar()
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
            for i in range(len(data)):
                text += "Event: " + data[f"Event No.{i + 1}"]['event_name'] + '\n' + "Summary: " + \
                        data[f"Event No.{i + 1}"]['description'] + '\n' + "Start time: " + \
                        data[f"Event No.{i + 1}"]['start_time'] + '\n' + "End time: " + \
                        data[f"Event No.{i + 1}"]['end_time'] + '\n' + "Location: " + \
                        data[f"Event No.{i + 1}"]['location'] + '\n'
                if 0 <= i < len(data) - 1:
                    text += '\n'
            f.close()

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


    @tasks.loop(hours=168)  # This can serve to be promising, think about using this
    async def my_task(channel_name='bot-spam'):
        """This function schedules the posting of the general schedule and the reminders for IEEE events; loops
        every week at the same time"""
        channels = bot.get_all_channels()
        channel = None
        for i in channels:
            channel = i if i.name == channel_name else channel
        file_path = await process_weekly_schedule()
        if file_path:
            await post_weekly_schedule(file_path, channel)
            with open(file_path, 'r') as f:
                data = json.load(f)
                time_format = "%U:%w:%H:%M:%S"
                seconds_before = 10 * 60
                for i, event in enumerate(data):
                    start_time = data[f'Event No.{i+1}']['start_time_parsable']
                    now = datetime.strftime(datetime.now(), time_format)
                    diff = (datetime.strptime(start_time, time_format) -
                            datetime.strptime(now, time_format)).total_seconds()
                    await asyncio.sleep(diff - seconds_before)
                    await post_reminder(file_path, i + 1, channel)


    @my_task.before_loop
    async def before_my_task():
        """Kind of like a preprocessing function to do before the loop"""
        time_format = "%U:%w:%H:%M:%S"
        week_num = time.strftime('%U')
        await bot.wait_until_ready()
        now = datetime.strftime(datetime.now(), time_format)
        diff = (datetime.strptime(f'{int(week_num) + 1}:0:00:00:00', time_format) -
                datetime.strptime(now, time_format)).total_seconds()
        await asyncio.sleep(diff)

    my_task.start()


    bot.run(TOKEN)


bot()

















# # TODO: FIGURE OUT A GOOD WAY TO PARSE AND HANDLE THE HTML LINK HREF IN THE DESCRIPTION
# # TODO: ORGANIZE THIS SHIT A LOT MORE, LOOKS AWFUL RIGHT NOW

