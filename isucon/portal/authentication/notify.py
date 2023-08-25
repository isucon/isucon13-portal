import requests
import json

from django.conf import settings

from isucon.portal.authentication.models import *


def notify_registration(user, message):
    """Slackに登録状況を出力する"""

    users = User.objects.filter(team__isnull=False)
    users_count = users.count()
    students_count = users.filter(is_student=True).count()

    team_count = Team.objects.count()

    blocks = [
		{
			"type": "section",
			"text": {
				"type": "mrkdwn",
				"text": message
			}
		},
		{
			"type": "section",
			"fields": [
				{
					"type": "mrkdwn",
					"text": "*チームID:*\n{}".format(user.team.id)
				},
				{
					"type": "mrkdwn",
					"text": "*チーム名:*\n{}".format(user.team.name)
				},
				{
					"type": "mrkdwn",
					"text": "*ユーザー名:*\n{}".format(user.display_name)
				}
			]
		},
		{
			"type": "section",
			"fields": [
				{
					"type": "mrkdwn",
					"text": "*参加者数:*\n{}人".format(users_count),
				},
				{
					"type": "mrkdwn",
					"text": "*学生数:*\n{}人".format(students_count),
				},
				{
					"type": "mrkdwn",
					"text": "*チーム数:*\n{}チーム".format(team_count),
				}
			]
		}
	]

    data = {'text': message, 'blocks': blocks}

    # setup channel webhook
    webhook_url = settings.SLACK_ENDPOINT_URL

    # send it
    requests.post(webhook_url, json=data)
