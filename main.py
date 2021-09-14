import ScreenshotHelper
from config import *
import atexit
from apscheduler.schedulers.blocking import BlockingScheduler
from datetime import datetime


sched = BlockingScheduler()
ss = ScreenshotHelper.Screenshotter()


@atexit.register
def close_script():
    ss.driver.close()
    ss.driver.quit()
    print("Closing script")


@sched.scheduled_job('interval', hours=1)
def scheduled_job():
    print('running screenshot job at {}'.format(datetime.now().strftime('%m/%d/%Y %I:%M %p')))
    ss.take_screenshot(subreddit_list)


def main():
    sched.add_job(scheduled_job)
    sched.start()


if __name__ == "__main__":
    main()
