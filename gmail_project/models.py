from django.contrib.auth.models import User
from django.db import models
from django.contrib import admin

from oauth2client.contrib.django_util.models import CredentialsField


class CredentialsModel(models.Model):
    id = models.ForeignKey(User, unique=True, primary_key=True)
    credential = CredentialsField()


class CredentialsAdmin(admin.ModelAdmin):
    pass

admin.site.register(CredentialsModel, CredentialsAdmin)
