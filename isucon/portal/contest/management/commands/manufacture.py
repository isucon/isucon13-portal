import random
from django.core.management.base import BaseCommand

from isucon.portal.authentication.factories import TeamFactory, UserFactory
from isucon.portal.contest.models import Server
from isucon.portal.contest.factories import ServerFactory, JobFactory, InformationFactory

class Command(BaseCommand):

    def generate_informations(self, info_num):
        InformationFactory.create_batch(info_num)

    def generate_teams(self, team_num):
        teams = []
        for _ in range(team_num):
            # ユーザ作成 -> チーム登録
            owner = UserFactory.create()
            team = TeamFactory.create(owner=owner)

            # チームがownerに設定される
            owner.team = team
            owner.save()

            teams.append(team)

        return teams

    def generate_team_users(self, team):
        user_num = random.randint(0, 2) # 追加メンバは 0 ~ 2
        UserFactory.create_batch(user_num, team=team)

    def generate_servers(self, team, server_num):
        for _ in range(server_num):
            ServerFactory.create(team=team)

    def generate_jobs(self, team):
        history_num = random.randint(5, 10) # 履歴は0 ~ 10
        for _ in range(history_num):
            job = JobFactory.create(team=team)
            job.target = Server.objects.get_bench_target(team)
            job.target_ip = job.target.global_ip
            job.save()

    def add_arguments(self, parser):
        parser.add_argument('-t', '--teams', default=10, type=int, help='Number of servers')
        parser.add_argument('-s', '--servers', default=3, type=int, help='Number of servers per team')
        parser.add_argument('-i', '--informations', default=3, type=int, help='Number of informations')

    def handle(self, *args, **options):
        team_num = options['teams']
        server_num = options['servers']
        info_num = options['informations']

        self.generate_informations(info_num)
        teams = self.generate_teams(team_num)
        for team in teams:
            self.generate_team_users(team)
            self.generate_servers(team, server_num)
            self.generate_jobs(team)
