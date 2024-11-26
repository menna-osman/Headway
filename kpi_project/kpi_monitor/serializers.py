from rest_framework import serializers
from .models import KPI, AssetKPI

class KPISerializer(serializers.ModelSerializer):
    class Meta:
        model = KPI
        fields = ['id', 'name', 'expression', 'description', 'created_at']

class AssetKPISerializer(serializers.ModelSerializer):
    class Meta:
        model = AssetKPI
        fields = ['id', 'asset_id', 'kpi']