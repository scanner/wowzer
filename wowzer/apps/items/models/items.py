#
# $Id$
#
# Description:
#   This defines the model's for the "objects" app in wowzer.
#   This app and its models represent objects in wow, like the "Rod of Arcane
#   Wrath"
#
#   This model is not used for auction house tracking stuff. That is in the
#   madhouse app. That app uses these models.
#
#   Yes, this basically duplicates thottbot data. We needed the basic
#   information anyways to map to the things in the auction house.
#   There is a LOT more data on thott (and where we can we link to thott's
#   info)
#
from django.core import meta

from wowzer.apps.toons.models.toons import Realm

#############################################################################
#
class Category(meta.Model):
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
class Object(meta.Model):
    """
    """

    fields = (
        meta.CharField('name', maxlength = 512),
        meta.BooleanField('bop'),
        meta.ForeignKey(Category),
        meta.ManyToManyField(Realm),
        )

    #########################################################################
    #
    def __repr__(self):
        return self.name
    
