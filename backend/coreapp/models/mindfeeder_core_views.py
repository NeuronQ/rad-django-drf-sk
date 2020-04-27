from django.db import models
from django import forms

from django.contrib.postgres.fields import ArrayField, JSONField


# # EXAMPLE: exposing an SQL view as a fake-model to show in Django admin
# class VTableCountsTotals(models.Model):
#     count = models.IntegerField()

#     # _db = "mindfeeder_core"

#     class Meta:
#         managed = False
#         db_table = "view_table_counts_totals"
#         verbose_name = "[SQL View] Table Counts Totals"
#         verbose_name_plural = verbose_name

