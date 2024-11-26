from django.shortcuts import render

# Create your views here.
from rest_framework import viewsets
from .models import KPI, AssetKPI
from .serializers import KPISerializer, AssetKPISerializer
from drf_yasg.utils import swagger_auto_schema

class KPIViewSet(viewsets.ModelViewSet):
    queryset = KPI.objects.all()
    serializer_class = KPISerializer

    @swagger_auto_schema(
        operation_description="List all KPIs",
        responses={200: KPISerializer(many=True)}
    )
    def list(self, request):
        return super().list(request)

    @swagger_auto_schema(
        operation_description="Create a new KPI",
        request_body=KPISerializer,
        responses={201: KPISerializer()}
    )
    def create(self, request):
        return super().create(request)

class AssetKPIViewSet(viewsets.ModelViewSet):
    queryset = AssetKPI.objects.all()
    serializer_class = AssetKPISerializer

    @swagger_auto_schema(
        operation_description="Link an asset to a KPI",
        request_body=AssetKPISerializer,
        responses={201: AssetKPISerializer()}
    )
    def create(self, request):
        return super().create(request)