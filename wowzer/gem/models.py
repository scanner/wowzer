#
# File: $Id$
"""
Models for the Guild Event Manager interface.
"""

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
    sources = models.("GemDataJob", editable = False)
    realm = models.ForeignKey(Realm, db_index = True, editable = False)
    leader = models.ForeignKey(Toon, db_index = True, editable = False)
    channel = models.CharField(maxlength = 256)
    created = models.DateTimeField(auto_now_add = True)
    update_time = models.DateTimeField()
    when = models.DateTimeField()
    place = models.CharField(maxlength = 256, default = "")
    comment = models.TextField(maxlength = 2048, null = True, blank = True)
    max_count = models.PositiveSmallIntegerField(default = 0)
    min_level = models.PositiveSmallIntegerField(default = 0)
    max_level = models.PositiveSmallIntegerField(default = 0)
    closed_comment = models.TextField(maxlength = 2048, null = True,
                                      blank = True)

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

    #########################################################################
    #
    def _players(self):
        """
        """
        return self.member_set.filter(state = Member.PLAYER)
    players = property(_players)
    
    #########################################################################
    #
    def _substitutes(self):
        """
        """
        return self.member_set.filter(state = Member.SUBSTITUTE)
    substitutes = property(_substitutes)

    #########################################################################
    #
    def _replacements(self):
        """
        """
        return self.member_set.filter(state = Member.REPLACEMENT)
    replacements = property(_replacements)

    #########################################################################
    #
    def _banned(self):
        """
        """
        return self.member_set.filter(state = Member.BANNED)
    banned = property(_banned)

    #########################################################################
    #
    def _assistants(self):
        """
        """
        return self.member_set.filter(state = Member.ASSISTANTS)
    assistants = property(_assistants)
    
#############################################################################
#
class ClassRule(models.Model):
    """
    For an event we have a set of rules for how many of each type of
    class we need/want in the event.

    Each 'ClassRule' specifies the rule (min/max) for a given class.

    Only classes for which there is a class rule can signup for the event.
    """

    # The GEM lua file, for some reason, stores the class as all upper case.
    # Also, I want an easy way to see what classes are not in the list.
    #
    CLASSES = (("HUNTER", "Hunter"), ("WARRIOR", "Warrior"),
               ("SHAMAN", "Shaman"), ("MAGE", "Mage"), ("PRIEST", "Priest"),
               ("WARLOCK", "Warlock"), ("DRUID", "Druid"),
               ("PALADIN", "Paladin"), ("ROGUE", "Rogue"))

    event = models.ForeignKey(Event, db_index = True)
    player_class = models.ForeignKey(PlayerClass, db_index = True)
    min = models.PositiveSmallIntegerField(default = 0)
    max = models.PositiveSmallIntegerField(default = 0)

    #########################################################################
    #
    def _players(self):
        """
        Return a count of the number of that class that are actually
        players in this event.

        This is a convenience method for easy calling inside of a template.
        """
        return event.players.filter(toon__player_class = self.player_class)
    players = property(_players)

    #########################################################################
    #
    def _sbustitutes(self):
        """
        Return a count of the number of that class that are actually
        players in this event.

        This is a convenience method for easy calling inside of a template.
        """
        return event.substitutes.filter(toon__player_class = self.player_class)
    substitutes = property(_substitutes)

    #########################################################################
    #
    def _replacements(self):
        """
        Return a count of the number of that class that are actually
        replacements in this event.

        This is a convenience method for easy calling inside of a template.
        """
        return event.replacements.filter(toon__player_class = self.player_class)
    replacements = property(_replacements)

    #########################################################################
    #
    def _assistants(self):
        """
        Return a count of the number of that class that are actually
        assistants in this event.

        This is a convenience method for easy calling inside of a template.
        """
        return event.assistants.filter(toon__player_class = self.player_class)
    assistants = property(_assistants)

    #########################################################################
    #
    def _banned(self):
        """
        Return a count of the number of that class that are actually
        banned in this event.

        This is a convenience method for easy calling inside of a template.
        """
        return event.banned.filter(toon__player_class = self.player_class)
    banned = property(_banned)
    
    #########################################################################
    #
    def __str__(self):
        if self.min_level == 0 and self.max_level == 0:
            return "A %s of any level" % self.player_class.name
        return "A %s between %d and %d" % (self.player_class, self.min_level,
                                           self.max_level)

#############################################################################
#
class Member(models.Model):
    """
    """

    # The list of 'states' an event member can be in.
    #
    UNKNOWN = 0
    PLAYER = 1
    ASSISTANT = 2
    SUBSTITUTE = 3
    REPLACEMENT = 4
    BANNED = 5

    # The list of keys in the GEM lua file for each type of member in the
    # event. This maps our states in to the key used in the GEM data file
    #
    PLAYER_STATE_KEYS = ((PLAYER,      'players'),
                         (ASSISTANT,   'assistants'),
                         (SUBSTITUTE,  'substitutes'),
                         (REPLACEMENT, 'replacements'),
                         (BANNED,      'banned'))

    # The 'states' and 'choices' used in the model and widget. This maps
    # our integer in to an appropriate human viewable string.
    #
    PLAYER_STATES = ((UNKNOWN, 'unknown'),
                     (PLAYER, 'player'),
                     (ASSISTANT, 'assistant'),
                     (SUBSTITUTE, 'substitute'),
                     (REPLACEMENT, 'replacement'),
                     (BANNED, 'banned'))
    
    event = models.ForeignKey(Event, db_index = True)
    toon = models.ForeignKey(Toon, db_index = True)
    state = models.PositiveSmallIntegerField(choices = PLAYER_STATES,
                                             db_index = True,
                                             default = UNKNOWN)
    update_time = models.DateTimeField()
    comment = models.TextField(maxlength = 1024, default = "", blank = True)
    force_substitute = models.BooleanField(default = False)
    force_titular = models.BooleanField(default = False)

    class Meta:
        ordering = ['state', 'toon']
    
#############################################################################
#
class GemDataJob(models.Model):
    """
    This class represents a unit of work that needs to be in reading in and
    parsing a GuildEventManager2.lua file and creating the appropriate objects
    in the database.
    """
    
    PENDING = 0
    PROCESSING = 1
    COMPLETED = 2
    ERROR = 3

    STATES = ((PENDING,    'pending'),
              (PROCESSING, 'processing'),
              (COMPLETED,  'completed'),
              (ERROR,      'error'))

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
