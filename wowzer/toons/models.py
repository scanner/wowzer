#
# Models for wowzer 'toons' app
#
# $Id$
#

# Django imports
#
from django.db import models
from django.conf import settings

# Wowzer imports
#
from wowzer.utils import TZ_CHOICES

# django model imports
#
from django.contrib.auth.models import User

REALM_TYPE_CHOICES = (
    ('pvp', 'Player versus player'),
    ('pve', 'Player versus environment'),
    ('pvp-rp', 'Player versus player, role playing'),
    ('rp', 'Role playing'),
    )

#############################################################################
#
class Realm(models.Model):
    """In World of Warcraft the play happens in 'realms.' A realm is a
    collection of server instances that represents one instance of the world of
    azeroth. A specific player can only exist on a single realm.
    """

    name = models.CharField(db_index = True, maxlength = 128)
    realm_type = models.CharField(maxlength = 16,
                                  choices = REALM_TYPE_CHOICES,
                                  default = 'pve')
    timezone = models.CharField(maxlength = 128, choices = TZ_CHOICES,
                                default = settings.TIME_ZONE)
    
    class Admin:
        pass

    #########################################################################
    #
    def __str__(self):
        return self.name

#############################################################################
#
class FactionGroup(models.Model):
    """Some factions belong to a grouping.. such as 'Alliance', 'Horde',
    'Steamwheedle Cartel'
    """
    name = models.CharField(maxlength = 128)
    description = models.CharField(maxlength = 1024)

    class Admin:
        pass

    #########################################################################
    #
    def __str__(self):
        return self.name

#############################################################################
#
class Faction(models.Model):
    """A player can be in one of two factions (alliance or horde.) There are a
    number of other factions as well.
    
    A player's relation to a faction is obviously unique to a single
    realm. However, the same factions occur on all realms.
    """

    name = models.CharField(maxlength = 128, db_index = True)
    description = models.CharField(maxlength = 1024)
    faction_group = models.ForeignKey(FactionGroup, blank = True, null = True)
    character_faction = models.BooleanField(default = False,
                                            help_text = 'True if this facition'
                                            ' is one a character can be a '
                                            'member of.')

    class Admin:
        pass
    
    #########################################################################
    #
    def __str__(self):
        return self.name

#############################################################################
#
class Race(models.Model):
    """Players can be one of several races. Like factions the same races exist
    on all servers. A race is implicitly a member of some faction.
    """

    name = models.CharField(maxlength = 128, db_index = True)
    description = models.CharField(maxlength = 1024)
    faction = models.ForeignKey(Faction)

    class Admin:
        pass

    #########################################################################
    #
    def __str__(self):
        return self.name

#############################################################################
#
class PlayerClass(models.Model):
    """Players can be one of several classes. Like factions and races the same
    classes exist on all realms.
    """

    name = models.CharField(maxlength = 128, db_index = True)
    description = models.CharField(maxlength = 1024)
    icon = models.ImageField(height_field = True, width_field = True,
                             null = True,
                             upload_to = "img/toon_icons/%Y/%m")
    
    class Admin:
        pass

    #########################################################################
    #
    def __str__(self):
        return self.name

#############################################################################
#
class GuildAlliance(models.Model):
    """
    """
    name = models.CharField(maxlength = 128, db_index = True)
    realm = models.ForeignKey(Realm)

    class Admin:
        pass

    class Meta:
        row_level_permissions = True
        permissions = (("Can examine guild", "examine_guild"),)
        unique_together = (('name', 'realm'),)

    #########################################################################
    #
    def __str__(self):
        return self.name

    #########################################################################
    #
    def get_absolute_url(self):
        return "/toons/guild_alliance/%d/" % self.id
    
#############################################################################
#
class Guild(models.Model):
    """
    """
    name = models.CharField(maxlength = 128, db_index = True)
    realm = models.ForeignKey(Realm)
    faction = models.ForeignKey(Faction)
    guild_alliance = models.ForeignKey(GuildAlliance)
    created = models.DateTimeField(auto_now_add = True)
    first_seen = models.DateTimeField(auto_now_add = True, editable = False)
    
    class Admin:
        pass

    class Meta:
        row_level_permissions = True
        permissions = (("Can examine guild", "examine_guild"),)
        unique_together = (('name', 'realm'),)

    #########################################################################
    #
    def __str__(self):
        return self.name

    #########################################################################
    #
    def get_absolute_url(self):
        return "/toons/guild/%d/" % self.id

#############################################################################
#
class GuildRank(models.Model):
    guild = models.ForeignKey(Guild)
    name = models.CharField(maxlength = 255, db_index = True)
    level = models.IntegerField(default = 0)
    officer = models.BooleanField(default = False)
    
#############################################################################
#
class RaidGroup(models.Model):
    name = models.CharField(maxlength = 128, db_index = True)
    realm = models.ForeignKey(Realm)

    class Meta:
        row_level_permissions = True
        permissions = (("Can examine raid group", "examine_raidgroup"),)
        unique_together = (('name', 'realm'),)
        
    #########################################################################
    #
    def __str__(self):
        return "RaidGroup '%s' on '%s'" % (self.name, self.realm.name)

    #########################################################################
    #
    def get_absolute_url(self):
        return "/toons/raidgroup/%d/" % self.id
    
#############################################################################
#
class Toon(models.Model):
    """
    """

    name = models.CharField(maxlength = 256, db_index = True)
    realm = models.ForeignKey(Realm)
    faction = models.ForeignKey(Faction, null = True)
    race = models.ForeignKey(Race, null = True)
    player_class = models.ForeignKey(PlayerClass, null = True)
    guild = models.ForeignKey(Guild, null = True, blank = True)
    guild_rank = models.ForeignKey(GuildRank, null = True, blank = True)
    user = models.ForeignKey(User, null = True, blank = True, db_index = True)
    raid_group = models.ManyToManyField(RaidGroup, null = True, blank = True)
    level = models.PositiveSmallIntegerField(default = 0)
    first_seen_time = models.DateTimeField(editable = False,
                                           auto_now_add = True)
    last_seen_location = models.CharField(maxlength = 256, null = True,
                                          blank = True, editable = False)
    last_login_time = models.DateTimeField(null = True, editable = False)
    last_logout_time = models.DateTimeField(null = True, editable = False)

    class Meta:
        ordering = ['realm','name']
        row_level_permissions = True
        unique_together = (('name', 'realm'),)
        
    class Admin:
        list_filter = ['faction', 'realm', 'race', 'guild', 'player_class']
        search_fields = ['name']
    
    #########################################################################
    #
    def __str__(self):
        return "%s of %s" % (self.name, self.realm.name)

    #########################################################################
    #
    def get_absolute_url(self):
        return "/toons/toon/%d/" % self.id
