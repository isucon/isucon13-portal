import datetime
import logging

from django.core.management.base import BaseCommand
from django.utils import timezone

from isucon.portal.authentication.models import User

logger = logging.getLogger(__name__)

class Command(BaseCommand):

    def handle(self, *args, **options):
        print("=== Refresh Token ===")
        l = timezone.now()+datetime.timedelta(days=5)
        for user in User.objects.filter(discord_expired_at__lte=l):
            print(user)
            user.refresh_discord_token()

        print("=== Update Information ===")
        for user in User.objects.filter(discord_expired_at__isnull=False):
            print(user)
            try:
                user.update_discord()
            except:
                logger.exception("update_discord error")
