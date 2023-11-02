import logging
import csv

from django.core.management.base import BaseCommand
from isucon.portal.authentication.models import Team

logger = logging.getLogger(__name__)

class Command(BaseCommand):

    def add_arguments(self, parser):
        parser.add_argument('cloud', type=str)
        parser.add_argument('filename', type=str)

    def handle(self, *args, **options):
        cloud = options["cloud"]
        filename = options["filename"]

        if cloud not in ["sacloud", "aws"]:
            raise ValueError("Invalid cloud type")
    
        with open(filename, "r") as f:
            reader = csv.reader(f)
            for row in reader:
                code = row[0]
                if cloud == "aws" and not code.startswith("PC"):
                    continue
                if cloud == "sacloud" and (not code.isdigit() or not len(code) == 16):
                    continue

                fieldname = "{}_coupon".format(cloud)

                cond = {}
                cond[fieldname] = code
                if Team.objects.filter(**cond).exists():
                    continue

                try:
                    cond = {
                        "is_active": True,
                    }
                    cond[fieldname] = ""
                    team = Team.objects.filter(**cond).order_by("id")[0]
                except IndexError:
                    return
                
                setattr(team, fieldname, code)
                team.save()
                print(code, team)
