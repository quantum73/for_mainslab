from rest_framework import serializers

from main_app.models import Client, Organization, Bill


class ClientSerializer(serializers.ModelSerializer):
    organizations_count = serializers.IntegerField()
    all_sums = serializers.IntegerField()

    class Meta:
        model = Client
        fields = ("name", "organizations_count", "all_sums")


class OrganizationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Organization
        fields = "__all__"


class BillSerializer(serializers.ModelSerializer):
    client = serializers.StringRelatedField(read_only=True)
    organization = serializers.StringRelatedField(read_only=True)

    class Meta:
        model = Bill
        fields = "__all__"
