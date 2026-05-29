from django.conf import settings
from django.db import models
from apps.core.models import BaseModel


class Desk(BaseModel):
    """Trading desk — organizational unit owning one or more trading books."""

    name = models.CharField(max_length=100)
    head_trader = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='+',
    )
    # commodities M2M added in Section 10 once trade_capture.Commodity exists
    is_active = models.BooleanField(default=True)
    cost_centre = models.CharField(max_length=50, blank=True)

    def __str__(self):
        return self.name
