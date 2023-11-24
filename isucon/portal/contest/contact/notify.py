from django.urls import reverse
import requests

from django.conf import settings

from isucon.portal.authentication.models import *
from isucon.portal.contest.contact.models import Ticket


def notify_contact(req, ticket: Ticket, message: str):
    """Slackに問い合わせ内容を通知する"""

    accepted_ticket_count = Ticket.objects.filter(status='accepted').count()
    url = req.build_absolute_uri(
        reverse('admin:contact_ticket_change', args=(ticket.id,))
    )

    blocks = [
      {
        "type": "section",
        "text": {
          "type": "mrkdwn",
          "text": "{}\n\n{}".format(message, url),
        }
      },
      {
        "type": "section",
        "fields": [
          {
            "type": "mrkdwn",
            "text": "*チケットID:* {}".format(ticket.id),
          },
          {
            "type": "mrkdwn",
            "text": "*チーム:* {} ({})".format(ticket.owner.team.id, ticket.owner.team.name),
          },
          {
            "type": "mrkdwn",
            "text": "*ジャンル:* {}".format(ticket.get_genre_display()),
          },
          {
            "type": "mrkdwn",
            "text": "*受付済みチケット:*\n{}件".format(accepted_ticket_count),
          },
        ]
      },
      {
        "type": "section",
        "fields": [
          {
            "type": "mrkdwn",
            "text": "*タイトル:* {}".format(ticket.title),
          },
        ]
      }
    ]

    data = {'text': message, 'blocks': blocks}

    # setup channel webhook
    webhook_url = settings.SLACK_ENDPOINT_URL

    # send it
    requests.post(webhook_url, json=data)
