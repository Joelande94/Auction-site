from __future__ import unicode_literals

import uuid
from django.db import models
from datetime import datetime
from django.utils import timezone
import pytz

from django.contrib import admin


# Create your models here.
def make_uuid():
    return str(uuid.uuid1())


class Auction(models.Model):
    id = models.CharField(primary_key=True, max_length=36, default=make_uuid, editable=False)
    owner = models.CharField(default=make_uuid, max_length=36, editable=True)
    seller = models.CharField(default="username", max_length=30)
    title = models.TextField(max_length=40)
    description = models.TextField(max_length=10000)
    current_bid = models.DecimalField(default=5, max_digits=8, decimal_places=2)
    deadline = models.DateTimeField(default=datetime.now(pytz.utc), editable=True)
    top_bidder = models.CharField(default=make_uuid, max_length=36, editable=True)
    banned = models.BooleanField(default=False)
    state = models.CharField(default="ACTIVE", editable=True, max_length=15)


class Bid(models.Model):
    id = models.CharField(primary_key=True, max_length=36, default=make_uuid, editable=True)
    auction_id = models.CharField(max_length=36, editable=True)
    bidder = models.CharField(max_length=30)
    bid = models.DecimalField(default=5, max_digits=8, decimal_places=2)


