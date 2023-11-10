import datetime
import logging
import time

from django.core.management.base import BaseCommand
from django.utils import timezone

from isucon.portal.authentication.models import User

logger = logging.getLogger(__name__)

class Command(BaseCommand):

    def handle(self, *args, **options):
        print("=== Refresh Token ===")
        l = timezone.now()+datetime.timedelta(days=5)
        for user in User.objects.filter(discord_expired_at__lte=l).order_by("discord_expired_at"):
            print(user)
            try:
                user.refresh_discord_token()
            except:
                logger.warning("refresh_discord_token error")
            time.sleep(0.5)

        print("=== Update Information ===")
        for user in User.objects.filter(discord_expired_at__isnull=False):
            print(user)
            try:
                user.update_discord()
            except:
                logger.warning("update_discord error")
            time.sleep(0.5)
