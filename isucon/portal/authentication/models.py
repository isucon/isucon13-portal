import os
import datetime
import locale
import random
import requests

from django.db import models
from django.contrib.auth.models import AbstractUser
from django.conf import settings
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

    discord_id = models.CharField("Discord ID", max_length=200, blank=True)
    discord_username = models.CharField("Discord Username", max_length=200, blank=True)
    discord_access_token = models.CharField("Discord Token", max_length=200, blank=True)
    discord_refresh_token = models.CharField("Discord Token", max_length=200, blank=True)
    discord_expired_at = models.DateTimeField("Discord 有効期限", blank=True, null=True)

    def __str__(self):
        return self.display_name

    @property
    def authorized_keys(self):
        url = "https://github.com/{}.keys".format(self.username)
        resp = requests.get(url)
        return resp.text

    def join_discord(self):
        """Discordサーバへ参加する"""
        # ユーザー名等の取得
        r = requests.get("https://discord.com/api/oauth2/@me", headers={
            "Authorization": "Bearer {}".format(self.discord_access_token),
        })
        r.raise_for_status()
        data = r.json()
        self.discord_id = data["user"]["id"]
        self.discord_username = data["user"]["username"]

        join_data = {
            "access_token": self.discord_access_token,
        }
        r = requests.put("https://discord.com/api/guilds/{}/members/{}".format(settings.DISCORD_SERVER_ID, self.discord_id), headers={
            "Authorization": "Bot {}".format(settings.DISCORD_BOT_ACCESS_TOKEN),
        }, json=join_data)
        r.raise_for_status()
        self.save()

    def refresh_discord_token(self):
        data = {
            'client_id': settings.DISCORD_OAUTH_CLIENT_ID,
            'client_secret': settings.DISCORD_OAUTH_CLIENT_SECRET,
            'grant_type': 'refresh_token',
            'refresh_token': self.discord_refresh_token,
        }
        headers = {
            'Content-Type': 'application/x-www-form-urlencoded'
        }
        r = requests.post("https://discord.com/api/oauth2/token", data=data, headers=headers)
        r.raise_for_status()
        data = r.json()

        self.discord_access_token = data["access_token"]
        self.discord_refresh_token = data["refresh_token"]
        self.discord_expired_at = timezone.now() + datetime.timedelta(seconds=data["expires_in"])
        self.save()

    def update_discord(self):
        if self.is_staff:
            return

        # ユーザー名等の取得
        r = requests.get("https://discord.com/api/oauth2/@me", headers={
            "Authorization": "Bearer {}".format(self.discord_access_token),
        })
        r.raise_for_status()
        data = r.json()
        self.discord_id = data["user"]["id"]
        self.discord_username = data["user"]["username"]


        # ニックネーム等を設定
        roles = [settings.DISCORD_USER_ROLE_ID]
        if not self.team or not self.team.is_active:
            roles = []

        if self.team:
            nick = "{} ({})".format(self.display_name, self.team.name)
        else:
            nick = self.display_name
        r = requests.patch("https://discord.com/api/guilds/{}/members/{}".format(settings.DISCORD_SERVER_ID, self.discord_id), headers={
            "Authorization": "Bot {}".format(settings.DISCORD_BOT_ACCESS_TOKEN),
        }, json={
            "nick": nick[:31],
            "roles": roles,
        })
        r.raise_for_status()

        self.save()


def generate_envcheck_token():
    return ''.join(random.choice(settings.PASSWORD_LETTERS) for i in range(64))


class TeamManager(models.Manager):
    def get_queryset(self):
        return super().get_queryset().filter(declined_at__isnull=True, is_active=True)


class Team(models.Model):
    class Meta:
        verbose_name = verbose_name_plural = "チーム"

    created_at = models.DateTimeField("作成日時", auto_now_add=True)
    updated_at = models.DateTimeField("最終更新日時", auto_now=True)
    declined_at = models.DateTimeField("辞退日時", blank=True, null=True)
    banned_at = models.DateTimeField("失格日時", blank=True, null=True)

    owner = models.OneToOneField(User, verbose_name="オーナー", on_delete=models.PROTECT, related_name="+")
    is_active = models.BooleanField("有効", default=True, blank=True)
    name = models.CharField("名前", max_length=100, unique=True)
    password = models.CharField("パスワード", max_length=100, unique=True)

    is_guest = models.BooleanField("ゲストチーム", blank=True, default=False)

    # benchmarker = models.ForeignKey('contest.Benchmarker', verbose_name="ベンチマーカー", on_delete=models.SET_NULL, null=True, blank=True)

    envcheck_token = models.CharField("envcheck向けトークン", max_length=100, default=generate_envcheck_token)
    envchecked_at = models.DateTimeField("envcheck完了時刻", blank=True, null=True)

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
        self.save()
        User.objects.filter(team=self).update(team=None)

    def ban(self):
        # 失格処理
        if self.banned_at:
            # すでに処理済み
            return

        self.banned_at = timezone.now()
        self.is_active = False
        self.save()

    @property
    def score(self):
        # FIXME: this is a dummy
        return {
            "latest_score": 100,
            "best_score": 2000,
            "latest_status": "Dummy",
            "updated_at": timezone.now(),
        }

def default_register_coupon_token():
    return ''.join(random.choice(settings.COUPON_LETTERS) for i in range(settings.COUPON_LENGTH))


class RegisterCoupon(models.Model):
    class Meta:
        verbose_name = verbose_name_plural = "登録クーポン"
        ordering = ("-created_at",)

    created_at = models.DateTimeField("作成日時", auto_now_add=True)
    updated_at = models.DateTimeField("最終更新日時", auto_now=True)
    used_at = models.DateTimeField("利用日時", blank=True, null=True)

    name = models.CharField("送付先", max_length=200)
    team = models.OneToOneField(Team, verbose_name="チーム", blank=True, null=True, on_delete=models.SET_NULL)
    token = models.CharField("トークン", max_length=100, unique=True, default=default_register_coupon_token)

    def use(self, team):
        if self.used_at:
            raise ValueError("Already used")
        self.used_at = timezone.now()
        self.team = team
        self.save()
