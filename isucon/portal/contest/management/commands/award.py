import logging
import datetime

from django.db.models import F, OuterRef, Func, Subquery
from django.db.models.functions import Abs
from django.core.management.base import BaseCommand
from django.conf import settings

from isucon.portal import utils as portal_utils
from isucon.portal.authentication.models import Team
from isucon.portal.contest.models import Score, Job


logger = logging.getLogger("award")

class Command(BaseCommand):

    def handle(self, *args, **options):
        
        funcs = [
            self.arkedge,
            self.iiseikatsu,
            self.tenx,
            self.hatena,
            self.newrelic,
            self.carta_holdings,
            self.tver,
            self.wantedly,
            self.line_yahoo,
        ]

        for func in funcs:
            print("====================================")
            func()

        print("====================================")


    def print_score(self, score, note=""):
        print(score.team, ":", score.latest_score, "点", note)


    def iiseikatsu(self):
        """
        いい生活
        11位のチーム
        """
        print("いい生活 (11位のチーム)")
        try:
            score = Score.objects.active().order_by("-latest_score")[11]
            self.print_score(score)
        except IndexError:
            print("該当なし")


    def tenx(self):
        """
        10X
        最終ベンチマークスコアがGo言語の初回のベンチマークスコアの10倍に一番近いチーム
        """

        target_score = 1000 * 10

        print("10X (最終スコアが{}に一番近いチーム)".format(target_score))

        try:
            score = Score.objects.active().annotate(
                score_diff=Abs(F("latest_score") - target_score),
            ).order_by("score_diff")[0]
            self.print_score(score)
        except IndexError:
            print("該当なし")


    def hatena(self):
        """
        はてな
        
        上位3チーム
        """

        print("はてな (上位3チーム)")

        if not Score.objects.active().exists():
            print("該当なし")
            return

        for score in Score.objects.active().order_by("-latest_score")[:3]:
            self.print_score(score)


    def newrelic(self):
        """
        NewRelic
        
        上位2チーム
        """

        print("NewRelic (上位2チーム)")

        if not Score.objects.active().exists():
            print("該当なし")
            return

        for score in Score.objects.active().order_by("-latest_score")[:2]:
            self.print_score(score)


    def carta_holdings(self):
        """
        CARTA HOLDINGS

        最終スコアの下四桁が7900に最も近いチーム
        """

        target_score = 7900
        print("CARTA HOLDINGS (最終スコアの下四桁が{}に最も近いチーム)".format(target_score))

        try:
            score = Score.objects.active().annotate(
                score_diff=Abs((F("latest_score") % 10000) - 7900),
            ).order_by("score_diff")[0]
            self.print_score(score)
        except IndexError:
            print("該当なし")


    def tver(self):
        """
        TVer

        上位30チーム (失格を除く) のうち、大会中、一番Failの数が多い3チーム
        """

        print("TVer (上位30チーム (失格を除く) のうち、一番Failの数が多い3チーム)")

        score_ids = [s.id for s in  Score.objects.active().order_by("-latest_score")[:30]]

        if not score_ids:
            print("該当なし")
            return

        fail_count_queryset = Job.objects.filter(
            team_id=OuterRef("team_id"),
            status=Job.DONE,
            is_active=True,
            is_test=False,
            is_passed=False,
        ).order_by().annotate(fail_count=Func(F('id'), function='Count')).values('fail_count')

        queryset = Score.objects.filter(
            id__in=score_ids,
        ).annotate(
            fail_count=Subquery(fail_count_queryset),
        ).order_by("-fail_count")

        for score in queryset[:3]:
            self.print_score(score, "{}回".format(score.fail_count))


    def arkedge(self):
        """
        アークエッジ・スペース
        
        今回のスコア / これまでの最高のスコア x 100 [%] が一番大きかったチーム
        """

        print("アークエッジ・スペース (今回のスコア / これまでの最高のスコア x 100 [%] が一番大きかったチーム)")

        target_team = None
        target_team_rate = 0

        for team in Team.objects.filter(is_active=True):
            best_job = None
            job_queryset = Job.objects.filter(
                team=team,
                is_passed=True, is_test=False, is_active=True,
            ).order_by("finished_at")

            for job in job_queryset:
                if not best_job:
                    best_job = job
                    continue
                
                rate = float(job.score) / float(best_job.score) * 100.0
                if target_team_rate < rate:
                    target_team = team
                    target_team_rate = rate
                    
                if best_job.score < job.score:
                    best_job = job

        if target_team is None:
            print("該当なし")
            return

        target_score = Score.objects.get(team=target_team)
        self.print_score(target_score, "{}%".format(target_team_rate))


    def wantedly(self):
        """
        Wantedly
        
        ランキングが隠れてから、最終結果のスコアが一番上がったチーム
        """

        target_score = None
        target_score_diff = 0

        finished_at_lt = (
            datetime.datetime.combine(settings.CONTEST_DATE, settings.CONTEST_END_TIME) - datetime.timedelta(hours=1)
        ).replace(tzinfo=portal_utils.jst)

        for score in Score.objects.active():
            try:
                # 隠れる前の最高スコア
                job1 = Job.objects.filter(
                    team=score.team,
                    is_test=False, is_active=True, is_passed=True,
                    finished_at__lt=finished_at_lt,
                ).order_by("-score")[0]
            except IndexError:
                continue
            
            print(job1)

            diff = score.latest_score - job1.score

            if target_score is None or target_score_diff < diff:
                target_score = score
                target_score_diff = diff

        if target_score is None:
            print("該当なし")
            return

        self.print_score(target_score, "{}点増加".format(target_score_diff))


    def line_yahoo(self):
        """
        LINEヤフー
        
        30位のチーム
        """

        print("LINEヤフー (30位のチーム)")
        try:
            score = Score.objects.active().order_by("-latest_score")[30]
            self.print_score(score)
        except IndexError:
            print("該当なし")
