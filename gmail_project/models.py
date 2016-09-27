from django.contrib.auth.models import User
from django.db import models
from oauth2client.contrib.django_util.models import CredentialsField
from django.contrib import admin


class CredentialsModel(models.Model):
    id = models.ForeignKey(User, unique=True, primary_key=True)
    credential = CredentialsField()


class CredentialsAdmin(admin.ModelAdmin):
    pass

admin.site.register(CredentialsModel, CredentialsAdmin)
