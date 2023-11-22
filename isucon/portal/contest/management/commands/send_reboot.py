import logging
import boto3
import json
import uuid

from django.core.management.base import BaseCommand
from django.conf import settings

from isucon.portal.authentication.models import Team
from isucon.portal.contest.models import Server

logger = logging.getLogger("send_reboot")

class Command(BaseCommand):

    def add_arguments(self, parser):
        parser.add_argument('--team', nargs='?', type=int)

    def handle(self, *args, **options):

        queryset = Team.objects.filter(is_active=True)
        if options["team"]:
            queryset = queryset.filter(id=options["team"])

        for team in queryset:
            print(team)
            servers = Server.objects.of_team(team)

            if not servers.exists():
                print("対象なし")
            else:
                data = {
                    "action": "reboot",
                    "team": team.id,
                    "servers":[s.global_ip for s in servers],
                }
                sqs_client = boto3.client("sqs")
                response = sqs_client.send_message(
                    QueueUrl=settings.SQS_JOB_URLS[team.aws_az],
                    MessageBody=json.dumps(data),
                    MessageGroupId=team.aws_az,
                    MessageDeduplicationId=str(uuid.uuid4()),
                )
                print(data, response)


