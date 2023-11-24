import datetime
from django.db import models
from django.utils import timezone

class Ticket(models.Model):
    class Meta:
        verbose_name = verbose_name_plural = "チケット"
        ordering = ()

    owner = models.ForeignKey("authentication.User", on_delete=models.CASCADE)
    title = models.CharField('タイトル', max_length=255)
    description = models.TextField('本文')
    STATUS = [
        ('accepted', '受付済み'),
        ('waiting', '参加者対応待ち'),
        ('closed', 'クローズ済み'),
    ]
    status = models.CharField('ステータス', max_length=10, choices=STATUS, default='accepted')
    GENRE = [
        ('code', '競技用コード'),
        ('infra', '参加者インフラ'),
        ('regulation', 'レギュレーション'),
        ('benchmark', 'ベンチマーク'),
        ('env', '環境チェック'),
        ('other', 'その他'),
    ]
    genre = models.CharField('ジャンル', max_length=10, choices=GENRE, default='other')
    VISIBILITY = [
        ('public', '公開'),
        ('summary', '要約のみ公開'),
        ('private', '非公開'),
    ]
    visibility = models.CharField('公開範囲', max_length=10, choices=VISIBILITY, default='private')
    summary = models.TextField('回答要約', blank=True)
    created_at = models.DateTimeField("作成日時", auto_now_add=True)
    updated_at = models.DateTimeField("最終更新日時", auto_now=True)

    def __str__(self):
        return f"#{self.id}: {self.title}"

    def is_recent(self):
        return self.created_at > timezone.now() - datetime.timedelta(minutes=10)

    def is_closed(self):
        if self.status == "closed":
            return True
        return False

    def only_team_query_set(team):
        return Ticket.objects.filter(owner__team=team)
    
    def public_query_set():
        return Ticket.objects.filter(models.Q(visibility="public") | models.Q(visibility="summary"))

    def visible_query_set(team):
        return Ticket.objects.filter(models.Q(owner__team=team) | models.Q(visibility="public") | models.Q(visibility="summary"))

class TicketComment(models.Model):
    class Meta:
        verbose_name = verbose_name_plural = "チケットコメント"
        ordering = ()

    ticket = models.ForeignKey("Ticket", on_delete=models.CASCADE)
    owner = models.ForeignKey("authentication.User", on_delete=models.CASCADE)
    description = models.TextField('本文')
    created_at = models.DateTimeField("作成日時", auto_now_add=True)
    updated_at = models.DateTimeField("最終更新日時", auto_now=True)
