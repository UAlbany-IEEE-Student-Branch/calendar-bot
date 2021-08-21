import json

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

    @bot.command(name='test')
    async def process_weekly_schedule(ctx, given_name='bot-spam'):
        channel = discord.utils.get(ctx.guild.channels, name=given_name)
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
            await channel.send(f"```{text}```")
        else:
            print("There seems to have been no schedule for this coming week. Disregard if this is not a problem, "
                  "otherwise please attend to the schedule.")


    bot.run(TOKEN)


if __name__ == '__main__':
    main()

#TODO: FIGURE OUT HOW TO CONFIGURE TIMED EVENTS FOR BOT EVENTS LIKE PROCESS_WEEKLY_SCHEDULE
#TODO: FIGURE OUT A GOOD WAY TO PARSE AND HANDLE THE HTML LINK HREF IN THE DESCRIPTION