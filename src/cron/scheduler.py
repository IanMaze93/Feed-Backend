from apscheduler.schedulers.background import BackgroundScheduler

from src.cron.handlers.refresh_stories import refresh_stories

scheduler = BackgroundScheduler()


def getScheduler() -> BackgroundScheduler:
    ## Register jobs
    scheduler.add_job(
        refresh_stories,
        trigger="interval",
        minutes=10,
        max_instances=1,
        coalesce=True,
    )

    return scheduler
