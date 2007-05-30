#
# $Id$
#
from django.db import models

# System imports
#
from datetime import datetime, timedelta

# django model imports
#
from django.contrib.auth.models import User
from django.contrib.auth.models import RowLevelPermission
from django.contrib.contenttypes import generic

# Wowzer model imports
#
from wowzer.main.models import TaggedItem

#############################################################################
#
class Topic(models.Model):
    author = models.ForeignKey(User, db_index = True, editable = False)
    title = models.CharField(maxlength=255, db_index=True)
    path= models.CharField(maxlength=255, db_index=True, core=True)
    created = models.DateTimeField(auto_now_add = True, editable = False,
                                   db_index = True)
    slug = models.SlugField(db_index = True, unique = True, blank = False)
    content = models.ForeignKey("Content")
    views = models.IntegerField(default = 0, editable = False)
    revision = models.IntegerField(default = 0, editable = False)
    #notify = models.BooleanField(default = True)
    locked = models.BooleanField(default = False, editable = False)
    tags = generic.GenericRelation(TaggedItem)

    class Meta:
        get_latest_by = 'created'
        ordering = ['created']
        row_level_permissions = True
        permissions = (('read_topic', 'Can read topic'),
                       ('rename_topic', 'Can rename topic'),
                       ('moderate_topic', 'Can moderate topics'))

#############################################################################
#
class Content(models.Model):
    edited_by = models.ForeignKey(User, db_index = True, editable = False)
    created = models.DateTimeField(auto_now_add = True, editable = False,
                                   db_index = True)
    content = models.TextField(maxlength = 16000, blank = True)
    content_html = models.TextField(maxlength = 16000, blank = True)
    markup = models.CharField(maxlength=80, blank=True, editable = False)
    revision = models.IntegerField(default = 0, editable = False)
    changelog = models.CharField(maxlength=255, default="", null=True, blank=True)

    class Meta:
        get_latest_by = 'created'
        ordering = ['revision', 'topic']
