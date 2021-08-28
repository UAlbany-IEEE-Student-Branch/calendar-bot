import datetime
import threading
import time
import schedule
import quickstart as qs
import GoogleCalendar as gc


def run_continuously(bot, interval=1):
    """Continuously run, while executing pending jobs at each
    elapsed time interval.
    @return cease_continuous_run: threading. Event which can
    be set to cease continuous run. Please note that it is
    *intended behavior that run_continuously() does not run
    missed jobs*. For example, if you've registered a job that
    should run every minute and you set a continuous run
    interval of one hour then your job won't be run 60 times
    at each interval but only once.
    """

    def schedule_reminders():
        pass

    def job():
        qs.process_weekly_schedule(bot)
        schedule_reminders()

    class ScheduleThread(threading.Thread):

        # schedule.every().sunday.at("00:00").do(job)
        schedule.every(3).seconds.do(job)
        while True:
            schedule.run_pending()
            time.sleep(interval)

    continuous_thread = ScheduleThread()
    continuous_thread.start()



# TODO: NOW THAT THE JOB CAN BE SCHEDULED, FIGURE OUT SENDING THE SCHEDULE AND REMINDER SENDING