import logging

from django.db.models.signals import post_save
from django.dispatch import receiver

from isucon.portal.authentication.models import Team
from isucon.portal.contest.models import Server, Job, Score
from isucon.portal.contest.redis.client import RedisClient
from isucon.portal.contest.notify import notify_abort

__all__ = ("create_score", "update_score", "set_default_benchmark_target_server")

logger = logging.getLogger('isucon.portal.contest.signals')

@receiver(post_save, sender=Job)
def update_score(sender, instance, created, **kwargs):
    """Jobが更新されたら、集計スコアを更新する"""

    try:
        notify_abort(instance)
    except:
        pass

    if not Score.objects.filter(team=instance.team).exists():
        # 念のためなかったら作る
        score = Score.objects.create(team=instance)
    else:
        score = instance.team.score

    score.update()

# @receiver(post_save, sender=Job)
# def update_redis_cache(sender, instance, created, **kwargs):
#     if instance.status == Job.DONE:
#         client = RedisClient()
#         client.update_team_cache(instance)

@receiver(post_save, sender=Server)
def set_default_benchmark_target_server(sender, instance, created, **kwargs):
    """サーバ追加時、ベンチマークのターゲットとするかどうか設定する"""
    if created:
        queryset = Server.objects.filter(team=instance.team)\
                                        .exclude(pk=instance.pk)
        if queryset.exists():
            # すでに他のサーバが存在するならば、ベンチマーク対象は既に存在する
            return

        instance.is_bench_target = True
        instance.save()
