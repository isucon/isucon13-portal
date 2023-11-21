import time
import logging
import pprint
from django.core.management.base import BaseCommand

from isucon.portal.authentication.models import Team
from isucon.portal.contest.models import Job, Server
from isucon.portal.contest.exceptions import DuplicateJobError


logger = logging.getLogger("test_run_jobs")

class Command(BaseCommand):

    def handle(self, *args, **options):
        for team in Team.objects.filter(is_active=True):
            try:
                job = Job.objects.enqueue(team=team, is_test=True)
                print(team, job)
            except Server.DoesNotExist:
                print(team, "Server was not set")
            except DuplicateJobError:
                print(team, "Already running")
