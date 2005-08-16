#
# $Id$
#
# Description:
#   This defines the model's for the "toons" app in wowzer.
#   This app and its models represent the player characters and their realms.
#
from django.core import meta

#############################################################################
#
class RealmType(meta.Model):
    """Quite simply realms can be of a specific type: PvE, PvP, RP-PvE,
    RP-PvP. I could have just made this a string on the realm but I am getting
    a little class-happy.
    """

    fields = (
        meta.CharField('type', maxlength = 32),
        meta.CharField('description', maxlength = 1024),
        )

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

    fields = (
        meta.CharField('name', maxlength = 128),
        meta.ForeignKey(RealmType),
        )
    
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

    fields = (
        meta.CharField('name', maxlength = 128),
        meta.CharField('description', maxlength = 1024),
        )
    
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

    fields = (
        meta.CharField('name', maxlength = 128),
        meta.CharField('description', maxlength = 1024),
        )
    
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

    fields = (
        meta.CharField('name', maxlength = 128),
        meta.CharField('description', maxlength = 1024),
        )
    
    #########################################################################
    #
    def __repr__(self):
        return self.name

#############################################################################
#
class Guild(meta.Model):
    """
    """

    fields = (
        meta.CharField('name', maxlength = 128),
        )
    
    #########################################################################
    #
    def __repr__(self):
        return self.name

#############################################################################
#
class Toon(meta.Model):
    """
    """

    fields = (
        meta.CharField('name', maxlength = 128),
        meta.ForeignKey(Realm),
        meta.ForeignKey(Faction),
        meta.ForeignKey(Race),
        meta.ForeignKey(Class),
        meta.ForeignKey(Guild, null = True, blank = True),
        )
    
    #########################################################################
    #
    def __repr__(self):
        return "%s of %s" (self.name, self.get_realm())

