from django.db import models


class CommonModel(models.Model):
    db_status_choice = [
        (1, 'active'),
        (2, 'delete'),
    ]
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    db_status = models.PositiveIntegerField(
        choices=db_status_choice, default=1)

    class Meta:
        abstract = True
# Create your models here.
