from contextlib import contextmanager
import datetime
import pickle

from django.conf import settings
import redis

from isucon.portal import utils as portal_utils
from isucon.portal.authentication.models import Team
from isucon.portal.contest.models import Job, Score
from isucon.portal.contest.redis.color import iter_colors


@contextmanager
def lock_with_redis(conn, lock_name, use_lock=True):
    if use_lock:
        try:
            lock = conn.lock(lock_name)
            lock.acquire(blocking=True)
            yield lock
        finally:
            lock.release()
    else:
        yield None


class LineChart:
    """折れ線グラフの座標情報"""

    def __init__(self):
        self.data = []

    def append(self, job):
        if job is None:
            raise ValueError('折れ線グラフに追加するジョブがNoneです: {}'.format(job))

        if not isinstance(job, Job):
            raise ValueError('jobではない値がLineChart.appendされました: {}'.format(job))

        team = job.team
        if team is None:
            raise ValueError('jobにチームが紐づいていません: {}'.format(job))

        self.data.append(dict(
            x=portal_utils.normalize_for_graph_label(job.finished_at),
            y=job.score
        ))

class TeamGraphData:
    """あるチームのグラフデータ"""

    def __init__(self, team):
        self.label = '{} ({})'.format(team.name, team.id)
        self.color = None
        self.hoverColor = None

        # partial_graphはラストスパートまでのデータしかない部分的なグラフ
        self.partial_graph = LineChart()
        # all_chartはラストスパート以後のデータも含む全体のグラフ
        self.all_graph = LineChart()

        self.team_id = team.id
        self.participate_at = team.participate_at

    def append(self, job):
        is_last_spurt = portal_utils.is_last_spurt(job.finished_at, job.team.participate_at)
        if is_last_spurt:
            self.all_graph.append(job)
        else:
            self.partial_graph.append(job)
            self.all_graph.append(job)

    def assign_color(self, color, hover_color):
        """TeamGraphDataをRedisから取得した際、表示するチーム一覧を考慮して色を割り当てる"""
        self.color = color
        self.hover_color = hover_color

    def to_dict(self, partial=False):
        if self.color is None or self.hover_color is None:
            raise ValueError('color、もしくはhover_colorが未設定です: color={}, hover_color={}'.format(color, hover_color))

        d = dict(
            label=self.label,
            backgroundColor=self.color,
            borderColor=self.color,
            hoverBackgroundColor=self.hover_color,
            hoverBorderColor=self.hover_color,
            pointHoverBorderWidth=5,
            lineTension=0,
            borderWidth=1,
            pointRadius=2,
            fill=False,
            spanGaps=True,
        )

        if partial:
            d['data'] = self.partial_graph.data
        else:
            d['data'] = self.all_graph.data

        return d


class RedisClient:
    LOCK = "lock"
    GRAPH_DATA = "team:{team_id}:graph-data"

    def __init__(self):
        self.conn = redis.StrictRedis(host=settings.REDIS_HOST)

    def load_cache_from_db(self, use_lock=False):
        # 全ジョブを再スキャン (team_id => team_graph_data の辞書で計算結果を持っておく)
        teams = dict()
        for job in Job.objects.filter(status=Job.DONE).order_by('finished_at').select_related("team"):
            if job.team.id not in teams:
                teams[job.team.id] = TeamGraphData(job.team)

            teams[job.team.id].append(job)

        with lock_with_redis(self.conn, self.LOCK, use_lock=use_lock):
            with self.conn.pipeline() as pipeline:
                for team_id, team_graph_data in teams.items():
                    pipeline.set(self.GRAPH_DATA.format(team_id=team_id), pickle.dumps(team_graph_data))
                pipeline.execute()

    def update_team_cache(self, job):
        # チームのジョブを再スキャン
        team_graph_data = TeamGraphData(job.team)
        for job in Job.objects.filter(status=Job.DONE, team=job.team).order_by('finished_at').select_related("team"):
            team_graph_data.append(job)

        with lock_with_redis(self.conn, self.LOCK):
            self.conn.set(self.GRAPH_DATA.format(team_id=job.team.id), pickle.dumps(team_graph_data))

    @staticmethod
    def get_graph_minmax(participate_at):
        graph_min = datetime.datetime.combine(participate_at, settings.CONTEST_START_TIME) - datetime.timedelta(minutes=10)
        graph_min = graph_min.replace(tzinfo=portal_utils.jst)

        graph_max = datetime.datetime.combine(participate_at, settings.CONTEST_END_TIME) + datetime.timedelta(minutes=10)
        graph_max = graph_max.replace(tzinfo=portal_utils.jst)

        return portal_utils.normalize_for_graph_label(graph_min), portal_utils.normalize_for_graph_label(graph_max)

    def get_graph_data(self, target_team, ranking, is_last_spurt=False):
        color_iterator = iter_colors()
        datasets = []
        for team_graph_bytes in self.conn.mget([self.GRAPH_DATA.format(team_id=team_id) for team_id in ranking]):
            if team_graph_bytes is None:
                # FIXME: 空データにする
                raise ValueError('ランキングに存在するチームがまだ得点していません')

            team_graph_data = pickle.loads(team_graph_bytes)
            if team_graph_data is None:
                raise ValueError('team_graph_dataをpickle.loadsできませんでした: {}'.format(team_graph_bytes))

            if team_graph_data.participate_at != target_team.participate_at:
                # グラフには同じ日にちの参加者情報しか出さない(スタッフである場合は除く)
                continue

            # グラフの彩色
            color, hover_color = next(color_iterator)
            team_graph_data.assign_color(color, hover_color)

            if not is_last_spurt:
                # ラストスパートでない場合、ラストスパート以後は更新しないグラフ
                datasets.append(team_graph_data.to_dict(partial=True))
            elif team_graph_data.team_id == target_team.id:
                # ラストスパートで自チームの場合、ラストスパート以後も更新するグラフ
                datasets.append(team_graph_data.to_dict(partial=False))
            else:
                # ラストスパートの場合、自チーム以外はラストスパート以後は更新しないグラフ
                datasets.append(team_graph_data.to_dict(partial=True))

        graph_min, graph_max = self.get_graph_minmax(target_team.participate_at)

        return datasets, graph_min, graph_max

    def get_graph_data_for_staff(self, participate_at, ranking):
        color_iterator = iter_colors()
        datasets = []
        for team_graph_bytes in self.conn.mget([self.GRAPH_DATA.format(team_id=team_id) for team_id in ranking]):
            if team_graph_bytes is None:
                # FIXME: 空データにする
                raise ValueError('ランキングに存在するチームがまだ得点していません')

            team_graph_data = pickle.loads(team_graph_bytes)
            if team_graph_data is None:
                raise ValueError('team_graph_dataをpickle.loadsできませんでした: {}'.format(team_graph_bytes))

            if team_graph_data.participate_at != participate_at:
                # スタッフは、指定の日の参加者しか出さない
                continue

            # グラフの彩色
            color, hover_color = next(color_iterator)
            team_graph_data.assign_color(color, hover_color)

            # 全てのグラフデータを取得
            datasets.append(team_graph_data.to_dict(partial=False))

        graph_min, graph_max = self.get_graph_minmax(participate_at)

        return datasets, graph_min, graph_max