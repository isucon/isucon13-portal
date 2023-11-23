from django.db import models
from isucon.portal.models import LogicalDeleteMixin

class Ticket(LogicalDeleteMixin, models.Model):
    class Meta:
        verbose_name = verbose_name_plural = "チケット"
        ordering = ()

    owner = models.ForeignKey("authentication.User", on_delete=models.CASCADE)
    title = models.CharField('タイトル', max_length=255)
    description = models.TextField('本文')
    STATUS = [
        ('accepted', '受付済み'),
        ('progress', '進行中'),
        ('waiting', '参加者対応待ち'),
        ('closed', 'クローズ済み'),
    ]
    status = models.CharField('ステータス', max_length=10, choices=STATUS, default='accepted')

    def __str__(self):
        return f"#{self.id}: {self.title}"

class TicketComment(LogicalDeleteMixin, models.Model):
    class Meta:
        verbose_name = verbose_name_plural = "チケットコメント"
        ordering = ()

    ticket = models.ForeignKey("Ticket", on_delete=models.CASCADE)
    owner = models.ForeignKey("authentication.User", on_delete=models.CASCADE)
    description = models.TextField('本文')
