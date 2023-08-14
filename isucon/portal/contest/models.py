import datetime
import json

from django.db import models
from django.db.models import Max, Sum
from django.forms.models import model_to_dict
from django.utils import timezone

from isucon.portal import settings
from isucon.portal.models import LogicalDeleteMixin, CommaSeparatedDateField
from isucon.portal.contest import exceptions

# FIXME: ベンチマーク対象のサーバを変更する機能
# https://github.com/isucon/isucon8-final/blob/d1480128c917f3fe4d87cb84c83fa2a34ca58d39/portal/lib/ISUCON13/Portal/Web/Controller/API.pm#L32

class InformatioManager(models.Manager):

    def of_team(self, team):
        return self.get_queryset().filter(is_enabled=True, allowed_participate_at__icontains=str(team.participate_at))



class Information(LogicalDeleteMixin, models.Model):
    class Meta:
        verbose_name = verbose_name_plural = "お知らせ"

    title = models.CharField("タイトル", max_length=100)
    description = models.TextField('本文')

    is_enabled = models.BooleanField("表示", blank=True)
    allowed_participate_at = CommaSeparatedDateField("対象日", max_length=512, choices=[])

    objects = InformatioManager()

class Benchmarker(LogicalDeleteMixin, models.Model):
    class Meta:
        verbose_name = verbose_name_plural = "ベンチマーカー"

    # TODO: ベンチマーカーを管理する上で必要な情報を追加
    ip = models.CharField("ベンチマーカーのIPアドレス", max_length=100)

    def __str__(self):
        return self.ip


class ServerManager(models.Manager):

    def of_team(self, team):
        """チームが持つサーバ一覧を取得"""
        return self.get_queryset().filter(team=team)

    def get_bench_target(self, team):
        """チームのベンチマーク対象を取得"""
        return self.get_queryset().get(team=team, is_bench_target=True)

    # FIXME: WAITING状態でenqueueされていても、変更ができる.
    # このことのテストを追加


class Server(LogicalDeleteMixin, models.Model):
    """参加者の問題サーバー"""
    class Meta:
        verbose_name = verbose_name_plural = "サーバ"
        unique_together = (("team", "hostname"),)

    # NOTE: パスワード、鍵認証とかにすればいい気がしたのでまだ追加してない
    # FIXME: デフォルトのベンチマーク対象を設定

    team = models.ForeignKey('authentication.Team', verbose_name="チーム", on_delete=models.PROTECT, related_name="servers")
    hostname = models.CharField("ホスト名", max_length=100)

    global_ip = models.CharField("グローバルIPアドレス", max_length=100, unique=True)
    private_ip = models.CharField("プライベートIPアドレス", max_length=100)

    is_bench_target = models.BooleanField("ベンチマークターゲットであるかのフラグ", default=False)

    objects = ServerManager()

    def set_bench_target(self):
        # 現在のベンチ対象を、ベンチ対象から外す
        current_bench_target = ServerManager.objects.get_bench_target(self.team)
        current_bench_target.is_bench_target = False
        current_bench_target.save()

        # 自分をベンチ対象にする
        self.is_bench_target = True
        self.save(using=self._db)

    def __str__(self):
        return self.hostname

class JobManager(models.Manager):

    def of_team(self, team):
        return self.get_queryset().filter(team=team)

    def get_latest_score(self, team):
        """指定チームの最新スコアを取得"""
        # NOTE: orderingにより最新順に並んでいるので、LIMITで取れば良い
        return self.of_team(team).filter(status=Job.DONE).order_by('-finished_at').first()

    def enqueue(self, team):
        # 重複チェック
        if self.check_duplicated(team):
            raise exceptions.DuplicateJobError

        # 追加
        job = self.model(team=team)
        job.save(using=self._db)

        return job

    def dequeue(self, benchmarker=None):
        if benchmarker is not None:
            # ベンチマーカーが自身にひもづくチームのサーバにベンチマークを行う場合
            # 報告したベンチマーカの紐づいているチーム、かつWAITING状態のジョブを取得
            queryset = self.get_queryset().select_for_update().filter(status=Job.WAITING, team__benchmarker=benchmarker)
        else:
            # ベンチマーカーが割り当てられてないチームのベンチマークを行う場合
            queryset = self.get_queryset().select_for_update().filter(status=Job.WAITING, team__benchmarker__isnull=True)

        job = queryset.order_by("created_at").first()
        if job is None:
            raise exceptions.JobDoesNotExistError

        # 状態を処理中にする
        job.status = Job.RUNNING
        job.target = Server.objects.get(team=job.team, is_bench_target=True)
        job.target_ip = job.target.global_ip
        job.save(using=self._db)

        return job

    def discard_timeout_jobs(self, timeout_sec=settings.BENCHMARK_ABORT_TIMEOUT_SEC):
        # FIXME: Celeryタスクで定期的に実行させる

        # タイムアウトの締め切り
        deadline = timezone.now() - datetime.timedelta(seconds=timeout_sec)

        # タイムアウトした(=締め切りより更新時刻が古い) ジョブを aborted にしていく
        jobs = Job.objects.filter(status=Job.RUNNING, updated_at__lt=deadline)
        for job in jobs:
            job.abort(reason="Benchmark timeout", stdout='', stderr='')

        return list(map(model_to_dict, jobs))

    def check_duplicated(self, team):
        """重複enqueue防止"""
        return self.get_queryset().filter(team=team, status__in=[
            Job.WAITING,
            Job.RUNNING,
        ]).exists()


class Job(models.Model):
    class Meta:
        verbose_name = verbose_name_plural = "ジョブ"
        ordering=('-created_at',)

    # 進捗の選択肢
    WAITING = 'waiting'
    RUNNING = 'running'
    DONE = 'done'
    ABORTED = 'aborted'
    CANCELED = 'canceled'
    STATUS_CHOICES = (
        (WAITING, WAITING), # 処理待ち
        (RUNNING, RUNNING), # 処理中
        (DONE, DONE), # 処理完了
        (ABORTED, ABORTED), # 異常終了
        (CANCELED, CANCELED), # 意図的なキャンセル
    )

    # 対象情報
    team = models.ForeignKey('authentication.Team', verbose_name="チーム", on_delete=models.CASCADE)
    target = models.ForeignKey('Server', verbose_name="対象サーバ", blank=True, null=True, on_delete=models.SET_NULL)
    target_ip = models.CharField("対象サーバIPアドレス", blank=True, max_length=100)
    benchmarker = models.ForeignKey('Benchmarker', verbose_name="ベンチマーカ", blank=True, null=True, on_delete=models.SET_NULL)

    # Choice系
    status = models.CharField("進捗", max_length=100, choices=STATUS_CHOICES, default=WAITING)
    is_passed = models.BooleanField("正答フラグ", default=False)

    reason = models.TextField("結果メッセージ", blank=True)
    score = models.IntegerField("獲得スコア", default=0, null=False)

    # ベタテキスト
    stdout = models.TextField("ログ標準出力", blank=True)
    stderr = models.TextField("ログ標準エラー出力", blank=True)

    # 日時
    created_at = models.DateTimeField("作成日時", auto_now_add=True)
    updated_at = models.DateTimeField("最終更新日時", auto_now=True)
    finished_at = models.DateTimeField("確定時刻", blank=True, null=True)

    objects = JobManager()

    DuplicateJobError = exceptions.DuplicateJobError

    @property
    def is_finished(self):
        return self.status in [
            self.DONE,
            self.ABORTED,
            self.CANCELED,
        ]

    @property
    def pretty_stdout(self):
        try:
            d = json.loads(self.stdout)
            return json.dumps(d, ensure_ascii=False, indent=4, sort_keys=True, separators=(',', ': '))
        except:
            pass
        return self.stdout

    @property
    def stdout_dict(self):
        try:
            d = json.loads(self.stdout)
            return d
        except:
            pass
        return {}

    def done(self, score, is_passed, stdout, stderr, reason, status=DONE):
        # ベンチマークが終了したらログを書き込む
        self.stdout = stdout
        self.stderr = stderr

        self.score = score
        self.is_passed = is_passed
        self.status = status

        self.reason = reason
        self.finished_at = timezone.now()
        self.save()

    def abort(self, reason, stdout, stderr):
        self.status = Job.ABORTED
        self.reason = reason
        self.stdout = stdout
        self.stderr = stderr
        self.score = 0
        self.is_passed = False
        self.save()

class ScoreManager(models.Manager):

    def passed(self):
        return self.get_queryset().filter(latest_is_passed=True)

    def failed(self):
        return self.get_queryset().filter(latest_is_passed=False)


# NOTE: Scoreは、Django signals を用いることで、チーム登録時に作成され、得点履歴が追加されるごとに更新されます
class Score(LogicalDeleteMixin, models.Model):
    class Meta:
        verbose_name = verbose_name_plural = "チームスコア"
        ordering = ("-latest_score", "-best_score", "best_scored_at", "team")

    team = models.OneToOneField("authentication.Team", on_delete=models.CASCADE)
    best_score = models.IntegerField('ベストスコア', default=0)
    best_scored_at = models.DateTimeField('ベストスコア日時', blank=True, null=True)
    latest_score = models.IntegerField('最新スコア', default=0)
    latest_scored_at = models.DateTimeField('最新スコア日時', blank=True, null=True)
    latest_is_passed = models.BooleanField('最新のベンチマーク成否フラグ', default=False, blank=True)

    objects = ScoreManager()

    def update(self):
        """Jobから再計算します"""
        try:
            latest_job = Job.objects.filter(team=self.team, status=Job.DONE).order_by("-finished_at")[0]
            self.latest_score = latest_job.score
            self.latest_scored_at = latest_job.finished_at
            self.latest_is_passed = latest_job.is_passed
        except IndexError:
            pass

        try:
            best_score_job = Job.objects.filter(team=self.team, status=Job.DONE, is_passed=True).order_by("-score")[0]
            self.best_score = best_score_job.score
            self.best_scored_at = best_score_job.finished_at
        except IndexError:
            pass

        self.save()
