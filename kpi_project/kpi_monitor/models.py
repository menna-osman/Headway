from django.db import models

# Create your models here.
from django.db import models

class KPI(models.Model):
    name = models.CharField(max_length=100)
    expression = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)



class AssetKPI(models.Model):
    asset_id = models.CharField(max_length=100)
    kpi = models.ForeignKey(KPI, on_delete=models.CASCADE)

    class Meta:
        unique_together = ('asset_id', 'kpi')
    