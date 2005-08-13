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

from wowzer.apps.toons.models.toons import Realm, Toon, Faction
from wowzer.apps.objects.models.objects import Object

#############################################################################
#
class AuctionDatum(meta.Model):
    """
    """

    fields = (
        meta.ForeignKey(Object),
        meta.ForeignKey(Realm),
        meta.ForeignKey(Faction),
        meta.DateTimeField("time"),
        meta.IntegerField("buyout"), # Value of 0 means no buyout
        meta.IntegerField("bid"),    # Value of 0 means no bid
        )

    ordering = ['time']
    
