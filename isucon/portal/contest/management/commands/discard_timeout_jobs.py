import time
import logging
import pprint
from django.core.management.base import BaseCommand

from isucon.portal.contest.models import Job


logger = logging.getLogger("discard_timeout_job")


class Command(BaseCommand):

    def discard_timeout_jobs(self):
        try:
            jobs = Job.objects.discard_timeout_jobs()
            if len(jobs) > 0:
                logger.info("discard jobs")
                pprint.pprint(jobs)
        except Exception as e:
            # through exception
            print(e)

    def handle(self, *args, **options):
        while True:
            self.discard_timeout_jobs()
            time.sleep(1)
