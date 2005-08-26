#
# $Id$
#
# Description:
#   This defines the model's for the "toons" app in wowzer.
#   This app and its models represent the player characters and their realms.
#
from django.core import meta
from django.models.auth import User

#############################################################################
#
class RealmType(meta.Model):
    """Quite simply realms can be of a specific type: PvE, PvP, RP-PvE,
    RP-PvP. I could have just made this a string on the realm but I am getting
    a little class-happy.
    """

    type = meta.CharField(maxlength = 32)
    description = meta.CharField(maxlength = 1024)

    class META:
        admin = meta.Admin()
    
    #########################################################################
    #
    def __repr__(self):
        return self.type

#############################################################################
#
class Realm(meta.Model):
    """In World of Warcraft the play happens in 'realms.' A realm is a
    collection of server instances that represents one instance of the world of
    azeroth. A specific player can only exist on a single realm.
    """

    name = meta.CharField(maxlength = 128)
    meta.ForeignKey(RealmType, blank = True, null = True)

    class META:
        admin = meta.Admin()

    #########################################################################
    #
    def __repr__(self):
        return self.name


#############################################################################
#
class Faction(meta.Model):
    """A player can be in one of two factions (alliance or horde.) There are a
    number of other factions as well.
    
    A player's relation to a faction is obviously unique to a single
    realm. However, the same factions occur on all realms.
    """

    name = meta.CharField(maxlength = 128)
    description = meta.CharField(maxlength = 1024)

    class META:
        admin = meta.Admin()

    #########################################################################
    #
    def __repr__(self):
        return self.name

#############################################################################
#
class Race(meta.Model):
    """Players can be one of several races. Like factions the same races exist
    on all servers.
    """

    name = meta.CharField(maxlength = 128)
    description = meta.CharField(maxlength = 1024)

    class META:
        admin = meta.Admin()

    #########################################################################
    #
    def __repr__(self):
        return self.name

#############################################################################
#
class Class(meta.Model):
    """Players can be one of several classes. Like factions and races the same
    classes exist on all realms.
    """

    name = meta.CharField(maxlength = 128)
    description = meta.CharField(maxlength = 1024)

    class META:
        admin = meta.Admin()
        verbose_name_plural = 'classes'

    #########################################################################
    #
    def __repr__(self):
        return self.name

#############################################################################
#
class Guild(meta.Model):
    """
    """

    name = meta.CharField(maxlength = 128)
    realm = meta.ForeignKey(Realm)
    faction = meta.ForeignKey(Faction)

    class META:
        admin = meta.Admin()

    #########################################################################
    #
    def __repr__(self):
        return self.name

    #########################################################################
    #
    def get_absolute_url(self):
        return "/toons/guild/%d/" % self.id

#############################################################################
#
class Toon(meta.Model):
    """
    """

    name = meta.CharField(maxlength = 256)
    realm = meta.ForeignKey(Realm)
    faction = meta.ForeignKey(Faction)
    race = meta.ForeignKey(Race, null = True, blank = True)
    klass = meta.ForeignKey(Class, db_column = "class_id",
                            null = True, blank = True)
    guild = meta.ForeignKey(Guild, null = True, blank = True)
    guild_rank = meta.CharField(maxlength = 256, null = True, blank = True)
    user = meta.ForeignKey(User, null = True, blank = True)

    class META:
        admin = meta.Admin()
        ordering = ['name']
    
    #########################################################################
    #
    def __repr__(self):
        return "%s of %s" % (self.name, self.get_realm().name)

    #########################################################################
    #
    def get_absolute_url(self):
        return "/toons/toon/%d/" % self.id
