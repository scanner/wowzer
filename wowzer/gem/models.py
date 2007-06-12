#
# Models for the Guild Event Manager interface.
#

# Django imports
#
from django.db import models
from django.db.models import signals, Q, permalink
from django.dispatch import dispatcher
from django.conf import settings

# 3rd party imports
#
from tagging.fields import TagField

# Wowzer imports
#
import wowzer.gem.signals
from wowzer.utils import TZ_CHOICES

# Import django contrib models.
#
from django.contrib.auth.models import User

# Wowzer models
#
from wowzer.toons.models import Toon, PlayerClass

#############################################################################
#
class Event(models.Model):
    name = models.CharField(maxlength = 256, db_index = True)
    submitter = models.ForeignKey(User, db_index = True, editable = False)
    leader = models.ForeignKey(Toon, db_index = True, editable = False)
    channel = models.CharField(maxlength = 256)
    created = models.DateTimeField(auto_now_add = True)
    update_time = models.DateTimeField()
    when = models.DateTimeField(null = True)
    place = models.CharField(maxlength = 256)
    comment = models.TextField(maxlength = 2048)
    max_size = models.PositiveSmallIntegerField(default = 0)
    minlevel = models.PositiveSmallIntegerField(default = 0)
    maxlevel = models.PositiveSmallIntegerField(default = 0)
    sort_type = models.CharField(maxlength = 255)
    closed_comment = models.TextField(maxlength = 2048, null = True,
                                      blank = True)
    titular_count = models.IntegerField(null = False, default = 0)

    class Admin:
        pass

    class Meta:
        get_latest_by = 'created'
        ordering = ['created']
        row_level_permissions = True
    
    #########################################################################
    #
    def __str__(self):
        return "For %s at %s, run by: %s" % (self.place, self.when,
                                             self.leader)
    
    #########################################################################
    #
    @permalink
    def get_absolute_url(self):
        return ("wowzer.gem.views.event_detail", (), { 'event_id': self.id })

#############################################################################
#
class ClassRule(models.Model):
    """
    For an event we have a set of rules for how many of each type of
    class we need/want in the event.

    Each 'ClassRule' specifies the rule (min/max) for a given class.

    Only classes for which there is a class rule can signup for the event.
    """
    event = models.ForeignKey(Event, db_index = True)
    player_class = models.ForeignKey(PlayerClass)
    min = models.PositiveSmallIntegerField(default = 0)
    max = models.PositiveSmallIntegerField(default = 0)

    #########################################################################
    #
    def __str__(self):
        if self.min_level == 0 and self.max_level == 0:
            return "A %s of any level" % self.player_class.name
        return "A %s between %d and %d" % (self.player_class, self.min_level,
                                           self.max_level)

#############################################################################
#
class EventMember(models.Model):
    """
    """
    PLAYER_STATES = ((1, 'titular'),
                     (2, 'substitute'),
                     (3, 'replacement'),
                     (4, 'unknown'),
                     (5, 'banned'))
    
    event = models.ForeignKey(Event, db_index = True)
    toon = models.ForeignKey(Toon, db_index = True)
    state = models.PositiveSmallIntegerField(choices = PLAYER_STATES,
                                             default = 4)
    update_time = models.DateTimeField()
    comment = models.TextField(maxlength = 1024, blank = True)
    force_substitute = models.BooleanField(default = False)
    force_titular = models.BooleanField(default = False)
    assistant = models.BooleanField(default = False)

    class Meta:
        ordering = ['state', 'toon']
    
#############################################################################
#
class GemDataJob(models.Model):
    PENDING = 0
    PROCESSING = 1
    COMPLETED = 2
    ERROR = 3
    STATES = ((PENDING,    'pending'),
              (PROCESSING, 'processing'),
              (COMPLETED,  'completed'),
              (ERROR,      'error'))
    """
    This class represents a unit of work that needs to be in reading in and
    parsing a GuildEventManager2.lua file and creating the appropriate objects
    in the database.
    """
    
    data_file = models.FileField(upload_to = "uploads/gem/%Y/%m/%d")
    created = models.DateTimeField(auto_now_add = True, editable = False,
                                   db_index = True)
    submitter = models.ForeignKey(User, db_index = True, editable = False)
    state = models.PositiveSmallIntegerField(choices = STATES, default = 0,
                                             editable = False)
    completed_at = models.DateTimeField(null = True, editable = False)
    
    class Meta:
        get_latest_by = 'created'
        ordering = ['created']

    #########################################################################
    #
    def __str__(self):
        return "GemDataJob %d, submitted by %s at %s, state: %s" % \
               (self.id, self.submitter, self.created,
                self.get_state_display())
    
    #########################################################################
    #
    @permalink
    def get_absolute_url(self):
        return ("wowzer.gem.views.datajob_detail", (), { 'job_id': self.id })

# Signals
#
# On post_save of a GemDataJob, call the process_jobs signal handler.
#
dispatcher.connect(wowzer.gem.signals.process_jobs, signal = signals.post_save,
                   sender = GemDataJob)
