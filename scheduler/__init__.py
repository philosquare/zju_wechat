from apscheduler.schedulers.background import BackgroundScheduler

from .jobs import remind_reserve
from resources import Instrument

scheduler = BackgroundScheduler()

scheduler.add_job(remind_reserve, 'cron', day_of_week='fri', hour=20, args=(Instrument.F20,))
scheduler.add_job(remind_reserve, 'cron', day_of_week='sun', hour=20, args=(Instrument.FIB,))
scheduler.start()
