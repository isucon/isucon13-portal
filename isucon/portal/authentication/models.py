import os
import datetime
import locale

from django.db import models
from django.contrib.auth.models import AbstractUser
from django.conf import settings
from django.db.models.query import QuerySet
from django.utils import timezone
from django.conf import settings
from stdimage.models import StdImageField

from isucon.portal import utils as portal_utils

locale.setlocale(locale.LC_TIME, 'ja_JP.UTF-8')

class User(AbstractUser):
    team = models.ForeignKey("Team", blank=True, null=True, on_delete=models.SET_NULL)
    icon = StdImageField(upload_to='icons/', blank=True, null=True, variations={
        'thumbnail': (150, 150, True),
    })
    is_student = models.BooleanField('学生フラグ', default=False, blank=True)
    display_name = models.CharField('表示名', max_length=100)

    def __str__(self):
        return self.display_name


class TeamManager(models.Manager):
    def get_queryset(self):
        return super().get_queryset().filter(declined_at__isnull=True, is_active=True)


class Team(models.Model):
    class Meta:
        verbose_name = verbose_name_plural = "チーム"

    created_at = models.DateTimeField("作成日時", auto_now_add=True)
    updated_at = models.DateTimeField("最終更新日時", auto_now=True)
    declined_at = models.DateTimeField("辞退日時", blank=True, null=True)

    owner = models.OneToOneField(User, verbose_name="オーナー", on_delete=models.PROTECT, related_name="+")
    is_active = models.BooleanField("有効", default=True, blank=True)
    name = models.CharField("名前", max_length=100, unique=True)
    password = models.CharField("パスワード", max_length=100, unique=True)

    is_guest = models.BooleanField("ゲストチーム", blank=True, default=False)

    # benchmarker = models.ForeignKey('contest.Benchmarker', verbose_name="ベンチマーカー", on_delete=models.SET_NULL, null=True, blank=True)

    objects = TeamManager()
    original_manager = models.Manager()

    @property
    def participate_at(self):
        return settings.CONTEST_DATE

    def is_playing(self):
        """参加中か(日付が一致し、時刻が範囲内なら)"""

        if os.environ.get("CONTEST", "").lower() == "true":
            # 強制的にコンテスト開催中にする (開発用)
            return True

        now = timezone.now()
        start_time = datetime.datetime.combine(self.participate_at, settings.CONTEST_START_TIME).replace(tzinfo=portal_utils.jst)
        end_time = datetime.datetime.combine(self.participate_at, settings.CONTEST_END_TIME).replace(tzinfo=portal_utils.jst)

        return start_time <= now <= end_time

    def __str__(self):
        return self.name

    def decline(self):
        # チーム辞退処理
        if self.declined_at:
            # すでに処理済み
            return

        self.declined_at = timezone.now()
        self.is_active = False
        User.objects.filter(team=self).update(team=None)

    @property
    def score(self):
        # FIXME: this is a dummy
        return {
            "latest_score": 100,
            "best_score": 2000,
            "latest_status": "Dummy",
            "updated_at": timezone.now(),
        }
