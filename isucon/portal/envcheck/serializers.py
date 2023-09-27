from rest_framework import serializers

from isucon.portal.envcheck.models import EnvCheckResult


class EnvCheckResultSerializer(serializers.ModelSerializer):
    class Meta:
        model = EnvCheckResult
        fields = (
            "name", "passed", "ip_address", "message", "admin_message", "raw_data"
        )

    def create(self, validated_data):
        validated_data["team"] = self.context["team"]
        return super().create(validated_data=validated_data)
