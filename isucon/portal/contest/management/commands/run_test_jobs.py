import time
import logging
import pprint
from django.core.management.base import BaseCommand

from isucon.portal.authentication.models import Team
from isucon.portal.contest.models import Job, Server
from isucon.portal.contest.exceptions import DuplicateJobError


logger = logging.getLogger("test_run_jobs")

class Command(BaseCommand):

    def add_arguments(self, parser):
        parser.add_argument('--team', nargs='?', type=int)

    def handle(self, *args, **options):
        queryset = Team.objects.filter(is_active=True)
        if options["team"]:
            queryset = queryset.filter(id=options["team"])

        for team in queryset:
            try:
                job = Job.objects.enqueue(team=team, is_test=True)
                print(team, job)
            except Server.DoesNotExist:
                print(team, "Server was not set")
            except DuplicateJobError:
                print(team, "Already running")
