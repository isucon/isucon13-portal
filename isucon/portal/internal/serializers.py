from django.utils import timezone
from rest_framework import serializers

from isucon.portal.contest.models import Job


class JobResultSerializer(serializers.ModelSerializer):

    class Meta:
        model = Job
        fields = ('id', 'status', 'score', 'resolved_count', 'language', 'is_passed', 'reason', 'stdout', 'stderr', 'finished_at')
        read_only_fields = ('id', )
