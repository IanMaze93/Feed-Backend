from apscheduler.schedulers.background import BackgroundScheduler

from src.cron.handlers.refresh_stories import refresh_stories

scheduler = BackgroundScheduler()


def getScheduler() -> BackgroundScheduler:
    ## Register jobs
    scheduler.add_job(refresh_stories, trigger="cron", day=1)

    return scheduler
