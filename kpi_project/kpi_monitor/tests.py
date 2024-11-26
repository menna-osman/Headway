from django.test import TestCase

# Create your tests here.
from django.test import TestCase
from rest_framework.test import APITestCase
from rest_framework import status
from .models import KPI, AssetKPI

class KPITests(APITestCase):
    def test_create_kpi(self):
        """Test KPI creation"""
        data = {
            'name': 'Test KPI',
            'expression': 'ATTR+50',
            'description': 'Test description'
        }
        response = self.client.post('/api/kpis/', data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(KPI.objects.count(), 1)

    def test_list_kpis(self):
        """Test KPI listing"""
        KPI.objects.create(name='Test KPI', expression='ATTR+50')
        response = self.client.get('/api/kpis/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)

class AssetKPITests(APITestCase):
    def setUp(self):
        self.kpi = KPI.objects.create(
            name='Test KPI',
            expression='ATTR+50'
        )

    def test_link_asset_to_kpi(self):
        """Test linking asset to KPI"""
        data = {
            'asset_id': '123',
            'kpi': self.kpi.id
        }
        response = self.client.post('/api/asset-kpis/', data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(AssetKPI.objects.count(), 1)