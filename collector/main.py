import logging
import os
import sys
from datetime import datetime, timezone

from apscheduler.schedulers.blocking import BlockingScheduler
from apscheduler.triggers.cron import CronTrigger

from collector.clients import qbittorrent
from collector.db import init_db, insert_snapshots, already_collected_today

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(message)s",
)
log = logging.getLogger(__name__)


def collect() -> None:
    now = datetime.now(timezone.utc)
    today = now.date().isoformat()

    if already_collected_today("qbittorrent", today):
        log.info("qBittorrent: already collected today, skipping")
        return

    captured_at = now.isoformat()
    log.info("Collection started at %s", captured_at)

    try:
        torrents = qbittorrent.get_upload_stats()
        insert_snapshots("qbittorrent", torrents, captured_at)
        log.info("qBittorrent: %d torrents saved", len(torrents))
    except Exception as e:
        log.error("qBittorrent collection failed: %s", e)


def main() -> None:
    version = os.getenv("APP_VERSION", "dev")
    log.info("qBittorrent Dashboard collector v%s starting", version)

    init_db()

    if "--now" in sys.argv:
        log.info("Manual collection triggered via --now")
        collect()
        return

    scheduler = BlockingScheduler(timezone="UTC")
    scheduler.add_job(collect, CronTrigger(hour=0, minute=0), misfire_grace_time=3600)

    log.info("Scheduler running. Next collection at midnight UTC.")
    scheduler.start()


if __name__ == "__main__":
    main()
