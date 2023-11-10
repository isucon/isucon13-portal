from django.shortcuts import get_object_or_404

from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.routers import SimpleRouter
from rest_framework import exceptions
from ipware import get_client_ip

from isucon.portal.contest.models import Job
from isucon.portal.internal.serializers import JobSerializer, JobResultSerializer
from isucon.portal.contest import exceptions as contest_exceptions


router = SimpleRouter()


class JobViewSet(viewsets.GenericViewSet):
    serializer_class = JobSerializer

router.register("job", JobViewSet, base_name="job")


class JobResultViewSet(viewsets.GenericViewSet):
    serializer_class = JobResultSerializer

    @action(methods=['post'], detail=True)
    def report(self, request, pk=None):
        """ベンチマーカーからの結果報告を受け取り、ジョブを更新します"""
        instance = get_object_or_404(Job.objects.all(), pk=pk)
        serializer = self.get_serializer(data=request.data, partial=True)
        try:
            serializer.is_valid(raise_exception=True)

            if not "score" in serializer.validated_data:
                raise RuntimeError()

            data = {
                "is_passed": False,
            }
            data.update(serializer.validated_data)

            instance.done(**data)
        except RuntimeError:
            return Response({"error":'Invalid format'}, status=status.HTTP_400_BAD_REQUEST)

        return Response(serializer.data)


router.register("job", JobResultViewSet, base_name="job-result")
