import time
import logging
import boto3
import json

from django.core.management.base import BaseCommand
from django.conf import settings
from django.db import transaction

from isucon.portal.contest.models import Job
from isucon.portal.internal.serializers import JobResultSerializer


logger = logging.getLogger("receive_job_result")


class Command(BaseCommand):

    def receive_job_results(self, wait_time_seconds=20):
        sqs_client = boto3.client("sqs")
        response = sqs_client.receive_message(
            QueueUrl=settings.SQS_JOB_RESULT_URL,
            AttributeNames=["SentTimestamp"],
            MaxNumberOfMessages=1,
            VisibilityTimeout=0,
            WaitTimeSeconds=wait_time_seconds,
        )

        if "Messages" not in response:
            return None

        for message in response["Messages"]:
            try:
                body = json.loads(message["Body"])

                if body:
                    print("Receive ID:", body["id"])
                    with transaction.atomic():
                        # DBを更新する
                        try:
                            instance = Job.objects.get(pk=body["id"])
                        except Job.DoesNotExist:
                            continue

                        if instance.status in (Job.WAITING, Job.RUNNING):
                            serializer = JobResultSerializer(instance=instance, data=body, partial=True)
                            if serializer.is_valid(raise_exception=False):
                                serializer.save()
                            else:
                                print(serializer.errors)

                # 正常に終了したらキューから消す
                receipt_handle = message["ReceiptHandle"]
                sqs_client.delete_message(
                    QueueUrl=settings.SQS_JOB_RESULT_URL,
                    ReceiptHandle=receipt_handle
                )
            except Exception:
                logger.exception("process message error")

        return True

    def handle(self, *args, **options):
        while True:
            if not self.receive_job_results():
                time.sleep(5)
