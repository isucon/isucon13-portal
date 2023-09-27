from django.db import models

class EnvCheckResult(models.Model):

    class Meta:
        ordering = ("-created_at", )
    
    created_at = models.DateTimeField("作成日時", auto_now_add=True)

    team = models.ForeignKey("authentication.team", on_delete=models.CASCADE)
    name = models.CharField("テスト名", max_length=100)
    passed = models.BooleanField("成功", blank=True, default=False)
    ip_address = models.CharField("IPアドレス", max_length=100)
    message = models.TextField("メッセージ", blank=True)
    admin_message = models.TextField("管理メッセージ", blank=True)
    raw_data = models.TextField("RAWデータ", blank=True)

