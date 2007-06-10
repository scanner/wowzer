#
# Models for the Guild Event Manager interface.
#

# Django imports
#
from django.db import models
from django.db.models import signals, Q, permalink

# 3rd party imports
#
from tagging.fields import TagField

# Import django contrib models.
#
from django.contrib.auth.models import User

# Wowzer models
#
from wowzer.toons.models import Toon, PlayerClass

#############################################################################
#
class Event(models.Model):
    channel = models.CharField(maxlength = 256)
    created = models.DateTimeField(auto_now_add = True)
    update_time = models.DateTimeField()
    leader = models.ForeignKey(Toon)
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
        return ("views.event_detail", str(self.id))

#############################################################################
#
class ClassLimit(models.Model):
    event = models.ForeignKey(Event)
    player_class = models.ForeignKey(PlayerClass)
    min_level = models.PositiveSmallIntegerField(default = 0)
    max_level = models.PositiveSmallIntegerField(default = 0)

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
    PLAYER_STATES = ((0, 'unknown'),
                     (1, 'inraid'),
                     (2, 'substitute'),
                     (3, 'replacement'))
    
    event = models.ForeignKey(Event)
    toon = models.ForeignKey(Toon)
    state = models.PositiveSmallIntegerField(choices = PLAYER_STATES,
                                             default = 0)
    position = models.CharField(maxlength = 30)
    update_time = models.DateTimeField()
    comment = models.TextField(maxlength = 1024, blank = True)
    force_sub = models.PositiveSmallIntegerField(default = 0)
    
#############################################################################
#
class GemDataJob(models.Model):
    """
    This class represents a unit of work that needs to be in reading in and
    parsing a GuildEventManager2.lua file and creating the appropriate objects
    in the database.
    """
    
    data_file = models.FileField(upload_to = "uploads/gem/%Y/%m/%d")
    created = models.DateTimeField(auto_now_add = True)
    submitter = models.ForeignKey(User)
    completed = models.BooleanField(default = False)
    completed_at = models.DateTimeField(null = True)
    
    class Meta:
        get_latest_by = 'created'
        ordering = ['created']

    #########################################################################
    #
    def __str__(self):
        return "GemDataJob %d, submitted by %s at %s, completed: %s" % \
               (self.id, self.submitter, self.created, self.completed)
    
    #########################################################################
    #
    @permalink
    def get_absolute_url(self):
        return ("views.datajob_detail", str(self.id))
