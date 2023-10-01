import datetime

from django.core.management.base import BaseCommand
from django.utils import timezone

from isucon.portal.authentication.models import User

class Command(BaseCommand):

    def handle(self, *args, **options):
        l = timezone.now()+datetime.timedelta(days=5)
        for user in User.objects.filter(discord_expired_at__lte=l):
            print(user)
            user.refresh_discord_token()
