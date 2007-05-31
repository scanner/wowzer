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

# 3rd party imports
#
from tagging.fields import TagField

#############################################################################
#
class Topic(models.Model):
    title = models.CharField(maxlength = 255, db_index = True, blank = True)
    slug = models.SlugField(maxlength = 255, db_index = True, unique = True,
                            blank = False)
    author = models.ForeignKey(User, db_index = True, editable = False)
    path = models.CharField(maxlength=255, db_index=True)
    created = models.DateTimeField(auto_now_add = True, editable = False,
                                   db_index = True)
    parent = models.ForeignKey("self")
    content = models.ForeignKey("Content")
    views = models.IntegerField(default = 0, editable = False)
    revision = models.IntegerField(default = 0, editable = False)
    locked = models.BooleanField(default = False, editable = False)
    tags = TagField()

    class Meta:
        get_latest_by = 'created'
        ordering = ['created']
        row_level_permissions = True
        permissions = (('read_topic', 'Can read topic'),
                       ('rename_topic', 'Can rename topic'),
                       ('moderate_topic', 'Can moderate topics'))

    #########################################################################
    #
    def __str__(self):
        return "<Topic: %s>" % self.slug

    #########################################################################
    #
    def get_absolute_url(self):
        return "/aswiki/topic/%d/" % self.id

#############################################################################
#
class Renames(models.Model):
    old = models.SlugField(maxlength=255, db_index = True, blank = False,
                           editable = False)
    changed = models.DateTimeField(auto_now_add = True, editable = False,
                                   db_index = True)
    topic = models.ForeignKey(Topic)

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
    changelog = models.CharField(maxlength=255, default="", null=True,
                                 blank=True)

    class Meta:
        get_latest_by = 'created'
        ordering = ['revision', 'topic']
