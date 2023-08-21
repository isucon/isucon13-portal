import datetime

from django.test import TestCase
from django.conf import settings

from isucon.portal.authentication import factories as auth_factories
from isucon.portal.authentication.decorators import is_registration_available
from isucon.portal import utils as portal_utils

class TimeTest(TestCase):

    def setUp(self):
        self.owner = auth_factories.UserFactory()


    def test_is_playing_time(self):
        """ is_playing() 時刻チェックのテスト"""
        # チームを作成 (日付一致前提)
        now = datetime.datetime.now()
        team = auth_factories.TeamFactory(owner=self.owner, participate_at=now.date())

        # 開催期間内の場合 True
        settings.CONTEST_START_TIME = portal_utils.get_utc_time(now.hour-1, 0, 0)
        settings.CONTEST_END_TIME = portal_utils.get_utc_time(now.hour+1, 0, 0)
        self.assertTrue(team.is_playing())

        # 開催期間外の場合 False
        settings.CONTEST_START_TIME = portal_utils.get_utc_time(now.hour+1, 0, 0)
        settings.CONTEST_END_TIME = portal_utils.get_utc_time(now.hour+2, 0, 0)
        self.assertFalse(team.is_playing())

    def test_is_registration_available(self):
        """登録期間のテスト"""
        now = datetime.datetime.now()

        # 期間内の場合 True
        settings.REGISTRATION_START_AT = portal_utils.get_utc_datetime(
            now.year,
            now.month,
            now.day,
            now.hour-1,
            now.minute,
            now.second,
        )
        settings.REGISTRATION_END_AT = portal_utils.get_utc_datetime(
            now.year,
            now.month,
            now.day,
            now.hour+1,
            now.minute,
            now.second,
        )
        self.assertTrue(is_registration_available())

        # 期間外の場合 False
        settings.REGISTRATION_START_AT = portal_utils.get_utc_datetime(
            now.year,
            now.month,
            now.day,
            now.hour+1,
            now.minute,
            now.second,
        )
        settings.REGISTRATION_END_AT = portal_utils.get_utc_datetime(
            now.year,
            now.month,
            now.day,
            now.hour+2,
            now.minute,
            now.second,
        )
        self.assertFalse(is_registration_available())
