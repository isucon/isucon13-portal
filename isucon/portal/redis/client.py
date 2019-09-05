from contextlib import contextmanager
import datetime
import pickle
from pytz import timezone

from django.conf import settings
import redis

from isucon.portal import utils as portal_utils
from isucon.portal.authentication.models import Team
from isucon.portal.contest.models import Job, Score


jst = timezone('Asia/Tokyo')


class TeamDict:
    """チーム情報を格納するデータ構造"""

    def __init__(self, team, labels=None, scores=None):
        self.id = team.id
        self.name = team.name
        self.participate_at = team.participate_at
        self.labels = [] if labels is None else labels
        self.scores = [] if scores is None else scores

        self._team = team

    @property
    def label(self):
        return '{} ({})'.format(self.name, self.id)

    @property
    def data(self):
        return zip(self.labels, self.scores)

    @property
    def unique_labels(self):
        return set(self.labels)

    @property
    def last_label(self):
        if len(self.labels) == 0:
            return None
        return self.labels[-1]

    @staticmethod
    def _normalize_finished_at(finished_at):
        return finished_at.strftime('%Y-%m-%d %H:%M:%S')

    def append_job(self, job):
        finished_at = self._normalize_finished_at(job.finished_at.astimezone(jst))

        self.labels.append(finished_at)
        self.scores.append(job.score)

    def __add__(self, other):
        labels = self.labels[:]
        labels.extend(other.labels)
        scores = self.scores[:]
        scores.extend(other.scores)

        return TeamDict(team=self._team, labels=labels, scores=scores)


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

# FIXME: teams_dict -> team_dicts

class RedisClient:
    # `RedisClientによる操作` の排他制御用ロック
    LOCK = "lock"
    # チーム情報(スコア履歴、ラベル一覧含む)
    TEAM_DICT = "team-dict"
    # チームごとの情報であるteam-dictを、チームIDとの対応表で保持する辞書
    TEAMS_DICT = "teams-dict"
    LASTSPURT_TEAMS_DICT = "lastspurt-teams-dict"
    # グラフ描画の際に用いるラベル (finished_at を正規化した文字列)
    LABELS = "labels"
    LASTSPURT_LABELS = "lastspurt-labels"


    def __init__(self):
        self.conn = redis.StrictRedis(host=settings.REDIS_HOST)

    def get_teams_dict(self, retry=False):
        team_bytes = self.conn.get(self.TEAMS_DICT)
        if team_bytes is None and retry:
            # NOTE: manufacture でシードデータを投入する場合、ここを通る
            #       デプロイ先だと、team_dict は必ずentrypoint.shで作成されるのでここを通らない
            self.load_cache_from_db()
            team_bytes = self.conn.get(self.TEAMS_DICT)

        if team_bytes is None:
            return None

        return pickle.loads(team_bytes)

    def load_cache_from_db(self, use_lock=False):
        """起動時、DBに保存された完了済みジョブをキャッシュにロードします"""
        with lock_with_redis(self.conn, self.LOCK, use_lock=use_lock):
            # 全てのpassedなジョブデータを元にteam_dictを再構成する
            teams_dict, lastspurt_teams_dict = dict(), dict()
            labels, lastspurt_labels = set(), set()
            for job in Job.objects.filter(status=Job.DONE).order_by('finished_at').select_related('team'):

                if not portal_utils.is_last_spurt(job.finished_at):
                    if job.team.id not in teams_dict:
                        teams_dict[job.team.id] = TeamDict(job.team)
                    teams_dict[job.team.id].append_job(job)
                    labels.add(teams_dict[job.team.id].last_label)
                else:
                    if job.team.id not in lastspurt_teams_dict:
                        lastspurt_teams_dict[job.team.id] = TeamDict(job.team)
                    lastspurt_teams_dict[job.team.id].append_job(job)
                    lastspurt_labels.add(lastspurt_teams_dict[job.team.id].last_label)

            with self.conn.pipeline() as pipeline:
                pipeline.set(self.LABELS, pickle.dumps(labels))
                pipeline.set(self.LASTSPURT_LABELS, pickle.dumps(lastspurt_labels))

                for team_id, team_dict in teams_dict.items():
                    pipeline.set(self.TEAM_DICT.format(team_id=team_id), pickle.dumps(team_dict))

                pipeline.set(self.TEAMS_DICT, pickle.dumps(teams_dict))
                pipeline.set(self.LASTSPURT_TEAMS_DICT, pickle.dumps(lastspurt_teams_dict))

                pipeline.execute()

    def update_team_cache(self, job):
        """ジョブ追加に伴い、キャッシュデータを更新します"""
        # ジョブに紐づくチームの情報を用意
        target_team_dict = TeamDict(job.team)
        for job in Job.objects.filter(status=Job.DONE, team=job.team).order_by('finished_at'):
            target_team_dict.append_job(job)

        with lock_with_redis(self.conn, self.LOCK):
            # チーム情報を取得
            teams_dict = self.get_teams_dict(retry=True)
            if teams_dict is None:
                return

            # チームの情報を丸ごと更新
            teams_dict['all_labels'].update(target_team_dict.unique_labels)
            teams_dict[job.team.id] = target_team_dict

            self.conn.set(self.TEAM_DICT.format(team_id=job.team.id), pickle.dumps(target_team_dict))
            self.conn.set(self.TEAMS_DICT, pickle.dumps(teams_dict))

    def get_graph_data(self, target_team, ranking, is_last_spurt=False):
        """Chart.js によるグラフデータをキャッシュから取得します"""
        # pickleで保存してあるRedisキャッシュを取得
        teams_dict = self.get_teams_dict()
        if teams_dict is None:
            return [], []

        # ラストスパート前は、topNのチームについてグラフ描画を行う
        all_labels = list(sorted(team_dict['all_labels']))

        # ラストスパートに入ったならば、自チームのみグラフに表示する
        if is_last_spurt:
            if target_team.id in team_dict:
                return all_labels, [dict(
                    label=team_dict[target_team.id].labels,
                    data=team_dict[target_team.id].data
                )]
            else:
                # ラストスパート時、未得点者はグラフに何も描画されない
                return all_labels, [dict(
                    label='{} ({})'.format(target_team.name, target_team.id),
                    data=zip([], [])
                )]

        datasets = []
        for team_id, target_team_dict in teams_dict.items():
            if team_id not in ranking:
                #  グラフにはtopNに含まれる参加者情報しか出さない
                continue
            if target_team_dict.participate_at != target_team.participate_at:
                # グラフには同じ日にちの参加者情報しか出さない
                continue

            datasets.append(dict(label=target_team_dict.label, data=target_team_dict.data))

        # 自分がランキングに含まれない場合、自分のdataも追加
        if target_team.id not in ranking and target_team.id in teams_dict:
            datasets.append(dict(label=teams_dict[target_team.id].label, data=teams_dict[target_team.id].data))

        return all_labels, datasets

    def get_graph_data_for_staff(self, participate_at, ranking):
        """Chart.js によるグラフデータをキャッシュから取得します"""
        # FIXME: 現在の仕様に合わせる(TEAMS_DICTなど)

        # pickleで保存してあるRedisキャッシュを取得
        team_bytes = self.conn.get(self.TEAM_DICT)
        if team_bytes is None:
            return [], []
        team_dict = pickle.loads(team_bytes)

        # topNのチームについてグラフ描画を行う
        datasets = []
        for team_id, team in team_dict.items():
            if team_id not in ranking:
                #  グラフにはtopNに含まれる参加者情報しか出さない
                continue
            if team['participate_at'] != participate_at:
                # グラフには指定した日にちの参加者情報しか出さない
                continue

            datasets.append(dict(
                label='{} ({})'.format(team['name'], team_id),
                data=zip(team['labels'], team['scores'])
            ))

        return list(sorted(team_dict['all_labels'])), datasets
