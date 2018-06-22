'''
All database models here for records app
'''

import datetime
from django.contrib.auth.models import User
from django.db import models



class YellowUserToken(models.Model):
    """
        Parent table for the database(contains the primary key).
    """
    user = models.IntegerField()
    yellowant_token = models.CharField(max_length=100)
    yellowant_id = models.IntegerField(default=0)
    yellowant_integration_invoke_name = models.CharField(max_length=100)
    yellowant_integration_id = models.IntegerField(default=0)
    webhook_id = models.CharField(max_length=100, default="")
    webhook_last_updated = models.DateTimeField(default=datetime.datetime.utcnow)

class YellowAntRedirectState(models.Model):
    """
        Child table
    """
    user = models.IntegerField()
    state = models.CharField(max_length=512, null=False)

class AppRedirectState(models.Model):
    """
        Child table
    """
    user_integration = models.ForeignKey(YellowUserToken, on_delete=models.CASCADE)
    state = models.CharField(max_length=512, null=False)

class DropBoxUserToken(models.Model):
    """
        Child table
    """
    user_integration = models.ForeignKey(YellowUserToken, on_delete=models.CASCADE)
    accessToken = models.CharField(max_length=512, null=False, default="")
    account_id = models.TextField(max_length=512,default="")



