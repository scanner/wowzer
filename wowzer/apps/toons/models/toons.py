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
class Realm(meta.Model):
    """
    """

    fields = (
        meta.CharField('name', maxlength = 128),
        meta.CharField('type', maxlength = 32),
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
        meta.ForeignKey(Guild, null = True, blank = True),
        meta.ForeignKey(Realm),
        )
    
    #########################################################################
    #
    def __repr__(self):
        return "%s of %s" (self.name, self.get_realm())

