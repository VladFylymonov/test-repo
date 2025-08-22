from __future__ import annotations
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger
from apscheduler.triggers.interval import IntervalTrigger
from typing import Callable, Optional
from .models import ScheduleConfig


class RunnerScheduler:
	def __init__(self):
		self.scheduler = BackgroundScheduler(timezone="UTC")

	def start(self) -> None:
		if not self.scheduler.running:
			self.scheduler.start()

	def shutdown(self) -> None:
		if self.scheduler.running:
			self.scheduler.shutdown(wait=False)

	def schedule(self, schedule_cfg: ScheduleConfig, func: Callable[[], None]) -> None:
		if schedule_cfg.cron:
			self.scheduler.add_job(func, CronTrigger.from_crontab(schedule_cfg.cron))
		elif schedule_cfg.interval_minutes:
			self.scheduler.add_job(func, IntervalTrigger(minutes=schedule_cfg.interval_minutes))
		else:
			raise ValueError("ScheduleConfig must have either cron or interval_minutes")