'''Rest stuff'''
from datetime import datetime
import pytz
from YAAS.models import make_uuid
from django.db import models
from rest_framework import serializers



class AuctionSerializer(serializers.Serializer):
    id = models.CharField(primary_key=True, max_length=36, default=make_uuid, editable=False)
    owner = models.CharField(default=make_uuid, max_length=36, editable=True)
    seller = models.CharField(default="username", max_length=30)
    title = models.TextField(max_length=40)
    description = models.TextField(max_length=10000)
    current_bid = models.IntegerField(default=5)
    deadline = models.DateTimeField(default=datetime.now(pytz.utc), editable=True)
    top_bidder = models.CharField(default=make_uuid, max_length=36, editable=True)
    banned = models.BooleanField(default=False)